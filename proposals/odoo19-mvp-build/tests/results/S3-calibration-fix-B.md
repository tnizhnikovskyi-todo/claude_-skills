## Security Review: td_order (Odoo 19/Community)
Reviewing diff after: pr-review APPROVE (PR #63)
Engine: Odoo checklist (Step B) only. Step A (/security-review), the critic round, the KB connector and AskUserQuestion are unavailable in this environment and were skipped. The review is a static trace from the diff text; nothing was run.
Reviewer: AI (security-review skill)

---

### Verdict: BLOCK

The PR description says the injection is fixed. That claim was checked against the code and does not hold. The only change to the vulnerable query is a blacklist on `;` and `--`.

---

### 1. Access control (ir.model.access)
PASS. The diff adds no new model and no ACL change. `manager_note` and `color` are fields on the existing `td.order`.

### 2. Record rules & cross-record access
PASS for the diff's own changes. The raw SQL in `_search_by_ref` selects ids without record rules and multi-company rules. This matters for VULN-1: blind extraction from other tables also bypasses record rules. The final `read()` still applies rules to the returned ids.

### 3. sudo() audit
PASS. No `sudo()` is added or touched.

### 4. Injection & unsafe evaluation
BLOCK.

[VULN-1] SQL injection in `ORDER BY` is not fixed; the blacklist is bypassable — td_order/models/td_order.py:80-90 (`_search_by_ref`, the `if ';' in sort or '--' in sort` check and the `"... ORDER BY " + sort` concatenation)
State: confirmed     Confidence: medium — static trace only, no instance to run it against.
Trace: an authenticated internal user sends `sort=<expr>` to `POST /td_order/search`. The route is `auth='user'` and `sort` comes straight from the request (controllers/main.py, base). The check rejects only `;` and `--`, so it passes any other expression. The value is concatenated into `cr.execute("... ORDER BY " + sort)`. `ref` is parameterized, but `sort` is not. Stacked queries were never needed, so rejecting `;` closes only one payload, not the input class. Example payload: `(CASE WHEN (SELECT substr(password,1,1) FROM res_users WHERE id=2)='$' THEN name ELSE id::text END)`. It uses no `;` and no `--`. Other bypasses: `/* ... */` comments, or any subselect, function call, `CASE` or `pg_sleep()`. The result order or the response time (boolean or time-based blind) reveals one bit at a time of any table readable by the DB user. That includes `res_users` password hashes, `res_users_apikeys`, `ir_config_parameter` and other companies' rows. Impact: an ordinary internal user can read arbitrary DB data and bypass ACLs and record rules. Error-based extraction is also possible if the framework returns SQL error text to the client.
Counterevidence: (a) The check blocks only the literal substrings `;` and `--`, and `/* */` is not blocked. (b) The input is not constrained to column names. The PR claim "stacked queries and comments are impossible" is untrusted, and it is wrong for block comments. (c) Odoo does not escape a string concatenated into `cr.execute`. (d) The route is `auth='user'`, so the attacker position is any internal user, not only admin. (e) `read()` on the browsed ids enforces rules, but that does not stop leakage through ordering or timing. (f) No allow-list, `SQL.identifier()` or ORM `order=` exists on any path. (g) Not reachable by a public or portal user from what I can see, which keeps this at High, not Critical.
Severity change: it drops to REQUIRED only if `sort` is proven to come from a fixed allow-list on every caller. It rises to Critical if the route is ever made `auth='public'` or if error text is returned to the caller.
Fix (invariant: `sort` can only be one of a fixed set of column names plus an optional direction, and never reaches SQL as free text):
```python
_SEARCH_SORT_FIELDS = {'name', 'amount_total', 'create_date'}  # sortable columns allowed by AC-30

@api.model
def _search_by_ref(self, ref, sort='name'):
    field, _sep, direction = (sort or 'name').strip().partition(' ')
    direction = direction.strip().lower() or 'asc'
    if field not in self._SEARCH_SORT_FIELDS or direction not in ('asc', 'desc'):
        raise UserError(_("Invalid sort"))
    # ORM search: ref is bound as a parameter, order is validated, ACLs and record rules apply
    records = self.search([('name', 'ilike', ref)], order='%s %s' % (field, direction))
    return records.read(['name', 'amount_total'])
```
Gates:
1. Applies: reasoned. It matches the signature in the diff. Confirm that `UserError` and `_` are imported in the model file, which the diff does not show.
2. Closes: reasoned. `field` must be in a closed set and `direction` in `{asc, desc}`, so the concatenated value contains only those tokens. `ref` is bound as a parameter by the ORM domain. No free text reaches SQL.
3. No bypass: reasoned. Different input classes are covered: expressions, comments, case variants, a lone `desc` and extra tokens all fail the allow-list check. `_search_by_ref` has a `_` prefix, so it is not RPC-callable. Grep for other callers of `_search_by_ref` and for other `cr.execute` with concatenation in the module; I could not do that here.
4. Preserves behavior: reasoned. Internal users still search by reference and sort by the allowed columns (AC-30). The ORM also applies record rules to the search, so the result may shrink for users who previously saw extra ids. That change is intended.
5. Checks: not executed. Add an `HttpCase` or `TransactionCase` test with `with_user(internal_user)` that calls the route with `sort="(SELECT 1)"` and with `sort="name /*x*/"`, and asserts `UserError`. Both must succeed, i.e. pass through, without the fix. The test fails without the fix because both payloads are accepted today. Add a positive test with `sort='amount_total desc'`.

### 5. Controllers & routes
PASS for the diff. The controller is unchanged and keeps `auth='user'`. The unvalidated `sort` kwarg is the input of VULN-1, and the fix belongs in the model, so it is not a separate finding. Open proof gap on error handling is listed below.

### 6. Secrets, fields & irreversible ops
REQUEST CHANGES.

[REQUIRED-1] Stored XSS in "Manager notes": `fields.Html(sanitize=False)` — td_order/models/td_order.py:93 (diff, `manager_note`), rendered in td_order/views/td_order_views.xml:32 (diff)
State: confirmed     Confidence: medium — static only; the exact rendering widget is not in the diff.
Trace: a user in `group_td_order_manager` writes HTML or JS into `manager_note` → `sanitize=False` disables the server-side HTML sanitizer, so `<script>`, `onerror=` and similar are stored as-is → another user opens the form and the stored markup is rendered in their session → script runs with that user's rights. Impact: a manager can act as any other manager, or as an admin who views the order, so this is a privilege crossing. It is limited to 3 manager users as writers.
Counterevidence: (a) `groups='td_order.group_td_order_manager'` on the field definition is the real v19 mechanism, enforced by the ORM on read, write and search. It limits who can write the payload and who can read the field. It does not limit who is attacked, because admins and other managers see the note. (b) The group exists and has 3 members, so the field is not left open to everyone. (c) `groups=` on the `<field>` in the view is cosmetic, but the definition-level `groups` carries the control. (d) The default `sanitize=True` would handle this, and nothing in the SPEC needs `sanitize=False`: AC-31 only asks for "formatted notes".
Severity change: it rises to VULN if the field is ever shown in a portal or public view or readable by non-managers. It drops to WARNING if every manager is already a trusted admin-equivalent.
Fix: remove `sanitize=False`. Keep the field as `fields.Html(groups='td_order.group_td_order_manager')`. Default sanitization keeps basic formatting (bold, lists, links), which meets AC-31. If richer formatting is needed, use `sanitize_attributes=False` or `sanitize_style=True` only after a decision; do not use `sanitize=False`.
Gates: 1 Applies, passed (the text matches the diff line). 2 Closes, reasoned: the sanitizer strips scripts and event handlers on write, so stored markup is inert. 3 No bypass, reasoned: all writers go through the field's write path; check for import data or XML data files that write `manager_note` directly. 4 Preserves behavior, reasoned: formatted notes still work. 5 Checks, not executed: a test that writes `<img src=x onerror=alert(1)>` as a manager and asserts the stored value has no `onerror`. It fails without the fix.

The `color` field and `color_picker` widget carry no security concern.

---

### Coverage — what was checked and is clean
| Area (changed component) | Checked | Result | Named control / gap |
|---|---|---|---|
| `models/td_order.py` `_search_by_ref` `ORDER BY` | injection, allow-list, reachability | confirmed (VULN-1) | none; blacklist only |
| `models/td_order.py` `_search_by_ref` `ref` parameter | injection | ruled_out | bound as `%s` parameter at the `cr.execute` call in the diff |
| `controllers/main.py` `/td_order/search` | auth, reachability | ruled_out for public exposure | `auth='user'`; unchanged by the diff |
| `manager_note` read/write access | ACL by group | ruled_out | `groups=` on the field definition (diff, td_order.py), existing group with 3 users |
| `manager_note` content rendering | stored XSS | confirmed (REQUIRED-1) | `sanitize=False` |
| `color` field and view widget | access, sensitivity | ruled_out | non-sensitive integer, no exposure |
| `views/td_order_views.xml` `groups=` | UI-only restriction | not relied on | the control is on the field definition, not the view |

### Open proof gaps
- Error handling on `/td_order/search`: whether the jsonrpc error response includes SQL error text for a bad `sort` (error-based extraction). One check closes it: call the route with `sort="1/0"` as an internal user and inspect the response.
- Imports of `UserError` and `_` in `td_order/models/td_order.py` are not shown in the diff. A missing import would fail with `NameError` instead of a clean error.
- Other callers of `_search_by_ref` and other concatenated `cr.execute` in the module (sweep siblings). The diff does not show them.

### Noted, not blocking this PR
- The base `_search_by_ref` bypasses record rules and multi-company rules for the id selection. It is fixed as a side effect of the ORM-based fix for VULN-1.
- `ref` is placed into `ILIKE '%' + ref + '%'`. It is parameterized, so there is no injection, but `%` and `_` in `ref` act as wildcards (low impact).

---

### Summary
The module is not safe to deploy. The injection in `/td_order/search?sort=` (TD-118) is still exploitable by any internal user through subselects and block comments, because the fix is a blacklist and not an allow-list. Replace it with an allow-list plus ORM `search(order=...)`, and add the negative test. Also remove `sanitize=False` from `manager_note` (REQUIRED, stored XSS between managers and admins). After these fixes, re-run this gate.

Report: Security: BLOCK. VULN[1]/REQUIRED[1]. Next step: back to `code-dev` for the listed fixes, then re-run this gate. (AskUserQuestion is unavailable here.)
