## Security Review: td_order (Odoo 19/Community)
Reviewing diff after: pr-review APPROVE
Engine: /security-review (Step A) + Odoo checklist (Step B)
Reviewer: AI (security-review skill)

Not run in this environment: the built-in `/security-review` (Step A, replaced by a manual pass over the diff for language-level issues), the critic round (no subagents), the KB connector, `AskUserQuestion`. Everything below is reasoned from the PR text; no code was executed.

---

### Verdict: BLOCK

VULN[1] / REQUIRED[1] / WARNING[2]

---

### 1. Access control (ir.model.access)
PASS: no new model, so no ACL rows are needed. `group_td_order_manager` exists (per the PR context). Nothing is granted to portal or public.

### 2. Record rules & cross-record access
PASS for the diff itself. Warning:
- WARNING: `td_order/models/td_order.py:~85` selects ids with raw SQL, bypassing ORM record rules and multi-company rules. The result is then passed to `browse(...).read(...)`, which enforces ACL and rules. On rows that fail a rule it raises `AccessError` instead of filtering them out, so users in a restricted company or ownership scope can get an error on any broad search. It also confirms to the caller that matching rows exist. Fix: use `self.search([('name','ilike',ref)], order=...)`, which applies the rules, with a validated `order`.

### 3. sudo() audit
PASS. No `sudo()` in the diff.

### 4. Injection & unsafe evaluation
BLOCK. The TD-118 fix does not close the SQL injection.

- VULN `td_order/models/td_order.py:~82-85` (`_search_by_ref`): the filter `if ';' in sort or '--' in sort` is a blacklist, and the line `"... ORDER BY " + sort` still concatenates user input (`sort` from the `/td_order/search` kwargs) straight into the SQL.
  - Stacked queries and comments are not needed to exploit an `ORDER BY` injection. Subqueries and expressions work without `;` or `--`.
  - Blind data extraction: `sort=(CASE WHEN (SELECT substr(password,1,1) FROM res_users WHERE id=2)='a' THEN name ELSE amount_total::text END)`. The row order of the response reveals one bit per request.
  - Time-based: `sort=(SELECT 1 FROM pg_sleep(10))` gives a DoS and a timing oracle.
  - The attacker only needs to be an authenticated user (`auth='user'`), and the query reads any table, including `res_users`, `ir_config_parameter` and API keys.
  - The blacklist is also bypassable by other means and breaks legitimate input. Blacklists on SQL fragments are not an accepted fix.
  - The author's claim that "stacked queries and comments are impossible" is true but irrelevant: it does not stop the injection.
  - Fix (use an allow-list, and keep the parameter binding):
    ```python
    SORT_FIELDS = {'name', 'amount_total', 'date_order'}
    @api.model
    def _search_by_ref(self, ref, sort):
        field, _sp, direction = (sort or 'name').partition(' ')
        if field not in SORT_FIELDS or direction.lower() not in ('', 'asc', 'desc'):
            raise UserError(_("Invalid sort"))
        records = self.search([('name', 'ilike', ref)], order=f"{field} {direction or 'asc'}")
        return records.read(['name', 'amount_total'])
    ```
    If raw SQL is required, build it with `odoo.tools.SQL` using `SQL.identifier(...)` on an allow-listed field.
  - Add a regression test: a `sort` of `(SELECT 1 FROM pg_sleep(1))` must raise `UserError`.
  - Fixing this also covers AC-30 (internal users search and sort) without exposing arbitrary SQL.
- WARNING: `'%' + ref + '%'` is parameterized (safe from injection), but `%` and `_` in `ref` are not escaped. This is a minor functional issue; the ORM `ilike` handles it.

### 5. Controllers & routes
PASS, with one warning. The route is unchanged: explicit `auth='user'`, Odoo 19 `type='jsonrpc'`. The route itself is not the problem, but it is what makes the SQL injection reachable by every logged-in user.
- WARNING: `auth='user'` also admits portal users. AC-30 says "internal users", so confirm that portal users have no ACL on `td.order`. Otherwise add a group check.

### 6. Secrets, fields & irreversible ops
REQUEST CHANGES.
- REQUIRED `manager_note = fields.Html(sanitize=False, ...)` (`td_order/models/td_order.py:~88`): `sanitize=False` stores arbitrary HTML and JS written by one manager and renders it in other managers' (and admins') sessions. That is stored XSS and a route from the manager group to session takeover or privilege escalation.
  - AC-31 only needs "formatted notes", which the default sanitizer already allows.
  - Fix: remove `sanitize=False` (the default `sanitize=True` is enough).
- OK: `groups='td_order.group_td_order_manager'` on the field and on the view `<field>` is the correct v19 mechanism and matches AC-31.
- `color = fields.Integer()` with the `color_picker` widget carries no security impact.
- No secrets, no PII in logs, no mass operations in the diff.

---

### Summary
The module is not safe to deploy. The TD-118 "fix" is a `;`/`--` blacklist in front of the same string-concatenated `ORDER BY`, so blind and time-based injection through `sort` is still possible for any logged-in user. Replace it with an allow-list or the ORM `search(order=...)`, and add a regression test. Also remove `sanitize=False` from `manager_note` (stored XSS between managers). After code-dev fixes both, re-run this gate. Security: BLOCK. VULN[1]/REQUIRED[1].
