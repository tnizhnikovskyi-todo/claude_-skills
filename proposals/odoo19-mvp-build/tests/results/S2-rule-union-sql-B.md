## Security Review: td_order (Odoo 19/Community)
Reviewing diff after: pr-review APPROVE
Engine: /security-review (Step A) + Odoo checklist (Step B)
Reviewer: AI (security-review skill)

Environment notes: the built-in `/security-review` (Step A) is not available here, so Step A is replaced by a manual language-level pass over the diff. The critic subagents, the KB connector and `AskUserQuestion` are also unavailable and were skipped (single pass). Nothing was executed; all traces are static, so confidence is at most medium.

The PR description says `export_orders` is "an internal helper, only called from the cron". That is untrusted. I checked it against the code, and it does not hold (see VULN-2).

---

### Verdict: BLOCK

---

### 1. Access control (ir.model.access)
PASS (with one open proof gap). The diff adds no `ir.model.access.csv` row and creates no new model. The new group `td_order.group_td_order_viewer` exists and is defined in the same file. Whether any ACL row grants this group `perm_read` on `td.order` is not visible in the diff. See "Open proof gaps".

### 2. Record rules & cross-record access
BLOCK.

[VULN-1] The "Order viewer" rule is granted to every internal user, so AC-20 is broken — `td_order/security/td_order_security.xml` (diff lines +44-46 and +47-55)
State: confirmed     Confidence: medium — static trace only, not run on an instance
Trace: the diff makes `base.group_user` imply `group_td_order_viewer` (`implied_ids`, `(4, ref(...))`). Every internal user therefore becomes a member of the viewer group. The viewer rule has `domain_force = [(1,'=',1)]`. Non-global rules of different groups are OR-ed. The unchanged base rule `td_order_salesperson_rule` (`[('user_id','=',user.id)]`, group `base.group_user`) is OR-ed with the new rule, and `[(1,'=',1)]` matches everything. As a result every salesperson can read all orders (`search`, `read`, `read_group`, RPC, views). This is cross-owner data exposure. The attacker position is an ordinary internal user.
- Write, create and unlink stay restricted, because the new rule has `perm_write/create/unlink = False`. Only read is affected.
- The exposure covers all companies, not just the user's own. The rule has no `company_id` condition, which also contradicts AC-21 ("all orders of **their company**").

Counterevidence: I looked for a limiting control and found none.
- The rule `td_order_salesperson_rule` does not limit it, because it is OR-ed with the new rule, not AND-ed.
- No global (`global=True`) rule is visible in the diff or the base context. If a global multi-company rule exists for `td.order`, it would limit the cross-company part only. It would not limit the cross-owner part. This is stated in the gap list.
- The `implied_ids` change on `base.group_user` is the new control weakening an existing control. The PR adds no test.

Severity change: lowers to REQUIRED only if the `td.order` data is non-sensitive and AC-20 is formally dropped. It is raised to critical if a multi-company deployment lacks a global company rule (cross-company leak).
Fix: the invariant is "only members of Order viewer see all orders of their company; other internal users see only their own."
1. Remove the `base.group_user` `implied_ids` record. Assign `group_td_order_viewer` manually to the reporting team users, or via a dedicated parent group.
2. Change the rule domain to `[('company_id', 'in', company_ids)]`.
```xml
<record id="td_order_viewer_rule" model="ir.rule">
    <field name="name">td.order: viewer sees all of own company</field>
    <field name="model_id" ref="model_td_order"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="groups" eval="[(4, ref('td_order.group_td_order_viewer'))]"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```
Gates 1-5: gate 1 (applies) passed. Gate 2 (closes) passed by trace: a plain `base.group_user` member no longer carries the viewer rule, so only the own-orders rule applies. Gate 3 (no bypass) is reasoned only: a user who is both viewer and salesperson still sees company-wide, which is intended. Gate 4 (legitimate use) is reasoned: the reporting team keeps read access. Gate 5 (check) is a proposed test: `TransactionCase` with `with_user(salesperson)`, a `td.order` of another user, and `assertEqual(search_count, 0)` for it. That test fails on the current PR. All gates are "reasoned, not executed".
The product decision of who belongs to the reporting team is the BA's. The fix does not change it.

### 3. sudo() audit
REQUEST CHANGES (hardening only).

[WARNING-1] The `sudo()` on `ir.config_parameter` has no justifying comment — `td_order/models/td_order.py` (diff line +71)
`self.env['ir.config_parameter'].sudo().get_param('td_order.export_sort', 'name')` is the standard pattern. The key is admin-written, so the value is not user-controlled on the cron path. It is provably safe but uncommented (Dimension 3 rule). Add a comment, for example "`ir.config_parameter` is readable only by admins; the value is trusted." The value is still a sink input (see VULN-2), so it must be validated.

No new `sudo()` on user-controlled domains or on write/unlink was found in the diff.

### 4. Injection & unsafe evaluation
BLOCK.

[VULN-2] SQL injection via `order_by` in a public, RPC-callable method that bypasses ACL and record rules — `td_order/models/td_order.py` (diff lines +59-67)
State: confirmed     Confidence: medium — static trace, not run on an instance; stacked statements depend on the driver and DB role
Trace:
- input: the `order_by` argument of `export_orders`. The method has no `_` prefix, so it is a public model method, callable by any user with access to the model through `/web/dataset/call_kw/td.order/export_orders`. The kwargs come straight from the client.
- missing control: no allow-list and no quoting of `order_by`. It is placed into the query with an f-string (`ORDER BY {order_by}`). Only `company_id` goes through `%s`.
- sink: `self.env.cr.execute(...)`, running as the DB role of the Odoo process.
- impact:
  - an authenticated internal user injects expressions into `ORDER BY`, e.g. a sub-select on `res_users`/`res_users_apikeys`/`ir_config_parameter`. This allows blind or error-based extraction of any table (password hashes, API key hashes, `database.secret`);
  - psycopg2 accepts stacked statements, so a `; UPDATE ...` payload may also give a write primitive (needs the injection to be allowed to close the statement);
  - the method returns rows via `dictfetchall()` from raw SQL, so ORM ACLs and `ir.rule` records are not applied at all. Even a harmless `order_by='name'` returns every `td_order` row of the current company to any internal user. That is a second AC-20 violation, independent of VULN-1.

Counterevidence:
- "Only called from the cron" is a claim, not a control. A cron caller is not the only entry point, because RPC counts as a caller.
- The cron path alone is not exploitable by a normal user: it takes the value from `ir.config_parameter`, which is admin-written. That limits the cron route only and does not make the public method safe.
- `self.env.company.id` is parameterized and is not injectable.
- The method takes no `self.check_access('read')`. The ACL row for `td.order` does not stop calling it either: the ACL only gates the RPC to the model, which every internal user passes.
- No `@api.model` guard and no `_` prefix on `export_orders` are present.

Severity change: lowers one level if the ACL for `td.order` is granted only to a narrow group, which would make it a manager-only attack. Raises nothing further, because it is already BLOCK class.
Fix: the invariant is "`order_by` is always one of a fixed set of column identifiers, the method cannot be called over RPC, and a user can only export rows they may read."
```python
_EXPORT_SORT_COLUMNS = ('id', 'name', 'amount_total', 'partner_id')

def _export_orders(self, order_by='name'):
    # private (not RPC-callable); only for _cron_export_orders
    if order_by not in self._EXPORT_SORT_COLUMNS:
        order_by = 'name'
    query = SQL(
        "SELECT id, name, amount_total, partner_id FROM td_order "
        "WHERE company_id = %s ORDER BY %s",
        self.env.company.id, SQL.identifier(order_by),
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()

@api.model
def _cron_export_orders(self):
    # config param is admin-written; still validated by the allow-list in _export_orders
    column = self.env['ir.config_parameter'].sudo().get_param('td_order.export_sort', 'name')
    return self._export_orders(order_by=column)
```
(`SQL` is `odoo.tools.SQL`. Import it.) The `_` prefix removes RPC reach. An alternative that keeps ORM rules: use `self.search_fetch([...], ['name', 'amount_total', 'partner_id'], order=...)` and keep the allow-list.
Gates 1-5: gate 1 (applies) passed. Gate 2 (closes): the `ORDER BY` value is always from the tuple, then quoted by `SQL.identifier`, so no attacker text reaches the SQL; the RPC entry is gone. Gate 3 (no bypass): sibling call site is only the cron; a user who calls `_cron_export_orders` over RPC cannot, because of the `_` prefix; reasoned only. Gate 4 (legitimate use): the cron still sorts by any listed column; if `td_order.export_sort` holds a column outside the list, it silently falls back to `name`, so extend the tuple if AC-22 needs more. Gate 5 (check): proposed `HttpCase`/`TransactionCase` test with `with_user(internal)`: `call_kw` on `export_orders` must raise `AccessError`/`AttributeError`, and `_export_orders(order_by="name; SELECT 1")` must not execute the payload. It fails without the fix. All gates are "reasoned, not executed".
Also: AC-22 says "sorted by the configured column". The allow-list must contain every legitimate configured value. This is a BA decision and is flagged, not assumed.

No `eval`, `safe_eval`, `pickle` or `yaml.load` found in the diff.

### 5. Controllers & routes
PASS. The diff adds no `@http.route`. The new RPC surface (public method `export_orders`) is covered under Dimension 4.

### 6. Secrets, fields & irreversible ops
PASS. No hardcoded secrets, no logging of PII, and no mass write or unlink. The cron only reads. One note: `self.env.company` in a cron runs in the superuser's company, so the export covers one company. If AC-22 means all companies, this is a functional gap for `pr-review`, not a security finding.

---

### Coverage — what was checked and is clean
| Area (changed component) | Checked | Result | Named control / gap |
|---|---|---|---|
| `td_order_security.xml` group `group_td_order_viewer` | exists, manifest dependency | ruled_out | defined in the same file (diff +41-43) |
| `td_order_security.xml` `base.group_user` `implied_ids` | rule union, reach | confirmed (VULN-1) | no control; OR with salesperson rule |
| `td_order_security.xml` `td_order_viewer_rule` | domain, company scope, perms | confirmed (VULN-1) | `[(1,'=',1)]`, no company; write/create/unlink off is correct |
| `models/td_order.py` `export_orders` | SQL, RPC reach, ACL bypass | confirmed (VULN-2) | no allow-list, no `_` prefix, no `check_access` |
| `models/td_order.py` `_cron_export_orders` | param source, sudo | ruled_out (as a source) | `ir.config_parameter` is admin-written; only a comment is missing (WARNING-1) |
| `models/td_order.py` `company_id = %s` | interpolation | ruled_out | parameter tuple `(self.env.company.id,)` at diff +66 |
| Controllers / routes | existence | ruled_out | no route in diff |
| Secrets / PII / mass ops | scan of diff | ruled_out | none present |

### Open proof gaps
- ACL for the viewer group: the diff shows no `ir.model.access.csv` row. Check that `base.group_user` (or the new viewer group) has `perm_read=1` and no write/unlink on `td.order`. Closing check: read `ir.model.access.csv`.
- Global company rule: confirm whether a global `ir.rule` `[('company_id','in',company_ids)]` exists for `td.order`. If it does, the cross-company part of VULN-1 is limited. It never limits the cross-owner part. Closing check: grep `td_order_security.xml` (lines before 20 are not in the diff).
- DB-level write via stacked statements in VULN-2: depends on the driver/role. Closing check: a test with `order_by="name; UPDATE td_order SET name='x'"` as an internal user.

### Noted, not blocking this PR
- `action_recompute_totals` (base, unchanged) is public and uses `self.sudo()`, with no ownership check and no comment. An internal user can recompute totals of orders they cannot read by passing ids over RPC. Not touched or newly reached by this diff.

---

### Summary
The module is not safe to deploy. Two exploitable issues must be fixed first. (1) The viewer group is implied by `base.group_user` and its rule is `[(1,'=',1)]`, so every internal user sees all orders, against AC-20 (and across companies, against AC-21). (2) `export_orders` is an RPC-callable public method that interpolates `order_by` into raw SQL and skips ACL and record rules. After the fixes, re-run this gate. The ACL row and company-rule gaps also need closing.

Security: BLOCK. VULN[2] / REQUIRED[0] / WARNING[1].
