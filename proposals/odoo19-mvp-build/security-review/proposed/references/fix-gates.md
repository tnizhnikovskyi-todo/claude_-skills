# Fix verification gates — details for `security-review`

Adapted from Strix `strix/skills/analysis/fix_verification.md` (Apache-2.0, see `ATTRIBUTION.md`).

## Priority order — never trade an earlier one for a later one
1. Current state correctly classified (vulnerable / safe / unproven).
2. Fix fully closes the broken boundary.
3. Legitimate behavior preserved.
4. Repository checks pass.
5. Follows module conventions.
6. Contains only what 1–5 need. "Minimal" = smallest change satisfying 1–5, not fewest lines.

## Before writing the fix
- Source → sink path, user-controlled input, preconditions.
- **Invariant in one sentence**, e.g. "a portal user reads only `td.order` of their commercial partner".
  Can't state it → can't verify the fix.
- Narrowest enforcement point; reuse Odoo's own mechanisms first: `ir.model.access`, `ir.rule`,
  `check_access(...)`, portal `_document_check_access`, `SQL` with params, `groups=` on the field.

## The gates (in order; failing one disqualifies the fix)
1. **Applicability** — the "before" matches current code exactly; diff has nothing unrelated;
   module still loads (XML ids exist, CSV columns valid).
2. **Security closure** — re-trace through the patched code; say precisely which step now fails.
   "Adds validation" is not closure; "`_document_check_access` raises `AccessError` before
   `sudo().read()`, the only sink on this route" is.
3. **Bypass review** — re-read without relying on your fix's reasoning. Check: sibling routes and
   methods on the same model; RPC entry (`call_kw`) for public methods; cron/server actions;
   other `sudo()` callers; another input class (`order`/`groupby`/field name instead of value, id
   list instead of int, other `company_id`, context keys, `access_token` missing vs wrong).
4. **Preserved behavior** — the legitimate user flow still works (portal user sees own records;
   manager still sees all); error semantics (`AccessError` vs 404) intentional.
5. **Repository checks** — name the focused test (`TransactionCase`/`HttpCase` with
   `with_user(...)`, `assertRaises(AccessError)`) and that it **fails without the fix**; then module
   tests and lint (`pylint-odoo`/`ruff` if the repo uses them).

Gates you could only reason about (no Odoo instance) are marked "reasoned, not executed".

## Disqualifies a fix
- Closes one payload, not the input class.
- Checks at the wrong layer (after the read; in a helper other callers bypass).
- Relies on a caller flag, context key or admin configuration.
- Fails open (`try/except` swallowing, "allow on error").
- Weakens ACL, rules, validation, logging or tests elsewhere to make it pass.
- Adds unrelated refactoring or fixes sibling findings in the same patch silently.

## Withhold the fix when
- It depends on an unresolved product decision (who should see what — ask BA / SPEC).
- It needs cross-module changes you cannot validate.
- You could not show the vulnerable path is real — do not patch an adjacent weakness instead.

Then: prose remediation + which gate failed + what is needed (decision, instance, test data).
