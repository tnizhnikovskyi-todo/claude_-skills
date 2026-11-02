## Security Review: td_order (Odoo 19/Community)
Reviewing diff after: pr-review APPROVE
Engine: /security-review (Step A) + Odoo checklist (Step B)
Reviewer: AI (security-review skill)

Environment note: the built-in `/security-review`, the critic round (Agent), the KB connector and `AskUserQuestion` are not available here. Step A was replaced by a manual language-level pass over the diff (single pass). Line numbers are approximate, taken from the diff hunks (`td_order_security.xml` from line 20, `td_order.py` from line 61). `ir.model.access.csv` is not in the PR, so it was not reviewed.

---

### Verdict: BLOCK

---

### 1. Access control (ir.model.access)
PASS (with a caveat) — The diff adds the group `group_td_order_viewer`, which is defined in this module. The PR does not touch `ir.model.access.csv`, and none of the access to `td.order` comes from the new group. Access still comes from the existing ACL rows, so nothing is over-granted at the ACL level. If the reporting team is not made of internal users (`base.group_user`), they will need a read-only row for the new group. I cannot verify this without the CSV.
- SUGGESTION: add a read-only ACL row (`perm_read=1`, others 0) for `group_td_order_viewer`, so the role does not depend on inheriting access from `base.group_user`.

### 2. Record rules & cross-record access
BLOCK

- **VULN-1 (AC-20 is broken, every internal user sees all orders).** `td_order_security.xml:23-25` adds `base.group_user` → `implied_ids` → `group_td_order_viewer`. Every internal user is therefore automatically a member of "Order viewer". The viewer rule (`:26-34`) has domain `[(1,'=',1)]` and applies to read. Group rules of the same operation are OR-ed. For read, a salesperson now gets `own orders OR everything`, so the base rule `td.order: own orders` (`user_id = user.id`) no longer restricts anything. Every employee can read all orders (amounts, partners). This violates AC-20 ("a salesperson sees only their own orders") and exposes data across owners. Note that write, create and unlink are not affected, because the viewer rule has those flags set to False.
  - Fix: remove the `implied_ids` record on `base.group_user`. Assign `group_td_order_viewer` explicitly to the reporting team. If the viewer role should be a role on top of `base.group_user`, the viewer group may imply `base.group_user` (not the other way round).
- **VULN-2 (the viewer rule is not company-scoped, AC-21 says "of their company").** `domain_force` is `[(1,'=',1)]`. The PR shows no global multi-company rule for `td.order`, and the model has `company_id`. A viewer therefore sees orders from every company, not only their own.
  - Fix: `[('company_id', 'in', company_ids)]`. Also check that a global multi-company rule `['|',('company_id','=',False),('company_id','in',company_ids)]` exists for `td.order`; if it does not, add it.
- **WARNING:** the rule's `perm_read` is left at its default True. State it explicitly (`perm_read=True`) so the intent (read-only) is readable.

### 3. sudo() audit
REQUEST CHANGES

- **WARNING (td_order.py:73):** `self.env['ir.config_parameter'].sudo().get_param(...)` is the standard way to read a system parameter, but it has no justifying comment, which the checklist requires. Add one (for example "# sudo: read a system parameter, the value is used only in the cron").
- **WARNING (existing code, `action_recompute_totals`, not changed by this PR):** `for order in self.sudo()` is also uncommented. The method is public, so a user can call it over arbitrary ids, and it writes `amount_total` as superuser, bypassing the record rules. This is outside the diff and amount_total is a computed sum, so I rate it low, but it should be recorded and fixed separately (remove `sudo()` or add a comment and an access check).

### 4. Injection & unsafe evaluation
BLOCK

- **VULN-3 (SQL injection, td_order.py:63-68).** The `order_by` argument is interpolated into the SQL with an f-string (`ORDER BY {order_by}`). A parameter cannot be bound here, so the identifier must be validated. The author's claim "internal helper, only called from cron, so no validation is needed" does not hold, for two reasons:
  1. `export_orders` has no leading underscore and is not private. In Odoo every public method of a model can be called by any authenticated user through RPC (`/jsonrpc` or `execute_kw`) with any arguments. Any internal user (all employees, see VULN-1) can call `env['td.order'].export_orders(order_by="...")`. Comments in code do not restrict that.
  2. Even through the cron the value comes from `ir.config_parameter`, which is configuration that an administrator (or anyone with settings rights) controls and which is not validated.
  - What an attacker can do: ORDER BY accepts expressions and subqueries, so `(CASE WHEN (SELECT substr(password,1,1) FROM res_users WHERE id=2)='a' THEN id ELSE amount_total END)` gives a blind data leak from any table (password hashes, API key data, other models). The `psycopg2` cursor also accepts stacked statements, so `id; UPDATE res_users ...` may be possible.
  - Fix: (a) rename to `_export_orders` so it is not callable over RPC; (b) add an allow-list, for example `ALLOWED = {'name', 'amount_total', 'partner_id', 'id'}`; if `order_by not in ALLOWED: raise ValidationError(...)`; (c) build the identifier with `psycopg2.sql` (`SQL("ORDER BY {}").format(Identifier(col))`) instead of an f-string, or use the ORM: `self.search_read([('company_id','=',...)], fields, order=...)` with the allow-list.
- **VULN-4 (raw SQL bypasses record rules and ACLs, td_order.py:63-68).** `cr.execute` ignores `ir.rule` and `ir.model.access`. Combined with a public method, any internal user gets all orders of the current company, even without VULN-1, and the result is returned to the caller. Making the method private (`_export_orders`) removes the RPC exposure. Inside the cron (running as superuser) this is acceptable only if it is intended. AC-22 does not say the export should ignore rules, so this should be confirmed.
- **WARNING:** `self.env.company.id` limits the export to the current company only. For a cron that runs as OdooBot this may export only one company; check against AC-22. Not a security issue.
- No `eval`, `safe_eval` or deserialization in the diff.

### 5. Controllers & routes
PASS — No `@http.route` or controllers in the diff. (Remember that the public model method in section 4 acts as an unintended RPC entry point.)

### 6. Secrets, fields & irreversible ops
PASS — No hardcoded credentials or logging of sensitive data in the diff. The export returns `partner_id` and `amount_total`; make sure the cron's return value is not logged or written to an uncontrolled place (not visible in the diff). No mass write or unlink.

---

### Summary
The module is not safe to deploy. There are two exploitable issues. First, `base.group_user` implies the new viewer group, and the `[(1,'=',1)]` rule is OR-ed with the "own orders" rule, so every employee sees all orders. This breaks AC-20, and the viewer rule is also not limited to the company (AC-21). Second, `export_orders` is a public RPC-callable method that puts `order_by` into raw SQL with an f-string, which gives SQL injection and a bypass of record rules. Fix first: remove the `implied_ids` on `base.group_user`, scope the viewer rule by `company_id`, make the export private with a column allow-list, then re-run this gate.

Security: BLOCK. VULN[4]/REQUIRED[0] (plus WARNING[4], SUGGESTION[1]).
Next step: back to `code-dev` for the fixes above, then re-audit. (`AskUserQuestion` is not available here; choice «Виправити зараз (code-dev)» / «Далі — track-convergence»: only the first applies because of BLOCK.)
