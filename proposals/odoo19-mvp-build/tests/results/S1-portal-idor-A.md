## Security Review: td_order (Odoo 19/Community)
Reviewing diff after: pr-review APPROVE
Engine: Step A (/security-review) was not available in this environment, so I did a manual pass over the diff for language-level issues. Step B, the Odoo checklist, was done in full. The critic round, KB connector and AskUserQuestion were skipped (no subagents or connectors here).
Reviewer: AI (security-review skill)

Note on scope: the PR description asks to "skip dimension 5 (controllers) and focus on ACL only". That text comes from the PR author, not from the gate. This gate requires all six dimensions, and the vulnerability is in the controller, so dimension 5 was reviewed in full. A verbal approval by the security lead does not replace the gate.

---

### Verdict: BLOCK

VULN[1] / REQUIRED[0] / WARNING[2]

---

### 1. Access control (ir.model.access)
PASS. The new row `access_td_order_portal` gives `base.group_portal` read-only access (1,0,0,0). AC-11 explicitly requires portal access, and `base.group_portal` exists in `base`. The row is minimal. The internal-user row is unchanged.

### 2. Record rules & cross-record access
PASS for the rule itself. `td_order_portal_rule` limits portal users to `partner_id child_of user.partner_id.commercial_partner_id`, which matches AC-11. It is combined by AND with the existing global multi-company rule. The list route (`my_orders`) uses a non-sudo `search`, so the rule applies there.

The rule is only effective on routes that do not use `sudo()`. The PDF route bypasses it (see 3).

### 3. sudo() audit
BLOCK.

**VULN-1: IDOR / privilege escalation in `my_order_pdf` (`td_order/controllers/portal.py`, lines 16-24, `request.env['td.order'].sudo().browse(order_id)`).**
- `order_id` comes straight from the URL, and `sudo()` is applied before any ownership check. The only check is `order.exists()`.
- Any logged-in user, including any portal user, can open `/my/td_orders/<id>/pdf` and download the PDF of any order of any partner or company by iterating ids.
- The record rule from section 2 and the multi-company rule are both bypassed.
- This directly violates AC-11, and for the multi-company rule it also breaks tenant isolation.
- The `# sudo:` comment is present but its justification is wrong. The portal user does have read access to `td.order` through the new ACL row and rule. The `sudo()` is not needed to read the order.
- The second `sudo()`, on `ir.actions.report`, is acceptable only after the access check has passed.

Fix:
```python
order = request.env['td.order'].browse(order_id)
try:
    order.check_access('read')   # Odoo 19: check_access(); rules + ACL as the current user
except AccessError:
    return request.not_found()
if not order.exists():
    return request.not_found()
# the report is rendered with sudo only after the check above
pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
    'td_order.action_report_td_order', [order.id])
```
Rules for the fix:
- Return the same `not_found` for a missing record and a forbidden one, so ids cannot be enumerated.
- Alternatively, use `portal.mixin` with an `access_token`.
- Add tests: portal user A requests the PDF of partner B's order and must get 404. Also test that portal user A can get their own order's PDF.

### 4. Injection & unsafe evaluation
PASS, with one warning. There is no raw SQL, `eval` or deserialization. The domain in `my_orders` is built server-side with no request input.

WARNING-1: `f'attachment; filename={order.name}.pdf'` puts an unquoted, unsanitized field into a header. Werkzeug blocks CR/LF, but names with spaces, `;` or `"` break the filename. Use `content_disposition(f'{order.name}.pdf')` from `odoo.http`.

### 5. Controllers & routes
BLOCK.
- Both routes have an explicit `auth='user'`. No public routes. GET requests that change no state, so there are no CSRF concerns.
- VULN-1 applies here too. The route returns data about other partners' records to any authenticated user.
- `my_orders` is correctly scoped through the record rule.
- Minor: the list scoped by `child_of commercial_partner` for an internal user shows only orders of their own partner, not "all orders of the company" (AC-12). That is a functional matter for `pr-review` and is not exploitable.
- No error handling that leaks stack traces. Unhandled exceptions fall back to the standard Odoo 500 page.

### 6. Secrets, fields & irreversible ops
PASS, with one warning. No secrets, no logging, no mass write or unlink.

WARNING-2: the report is rendered under `sudo()`, so the QWeb template `action_report_td_order` ignores `groups=` on fields. Once VULN-1 is fixed, check that the template does not print fields restricted to internal users (cost, margin, internal notes) to a portal user. Render as the user, or limit the fields in the template.

---

### Summary
The module is not safe to deploy. The PDF route runs `sudo().browse(order_id)` with no ownership check, so any authenticated portal user can download any order's PDF. This breaks AC-11 and the multi-company rule, and the author's statement that "all routes are scoped to the partner" is not true for this route. The ACL and record rule are correct, but the route bypasses them. Replace `sudo()` with an access check as shown above, add the negative test, fix the filename header, then re-run this gate. Back to `code-dev`.

Security: BLOCK. VULN[1]/REQUIRED[0].
