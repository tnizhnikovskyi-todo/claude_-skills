## PR Review: td_credit (PR #80, AC-03)

Skipped (not available here): running tests/CI, Odoo instance, `/security-review`, KB, subagents. Review is from the text only. Note: the diff shows no import lines, so `ValidationError`/`_` imports cannot be verified.

### Verdict: REQUEST CHANGES

### 1. Spec compliance — findings
- **REQUIRED** `td_credit/models/sale_order.py:11-12` (new line `partner.td_open_credit + order.amount_total > partner.td_credit_limit`): the check mixes currencies. `order.amount_total` is in the order currency, and `td_open_credit` (base, `res_partner.py`, unchanged) sums order-currency amounts without conversion. The limit `td_credit_limit` is a Monetary on the partner (company currency). So a 900 EUR order and a 900 USD order are summed and compared as the same unit, and AC-03 gives wrong results (false block or false pass) for any non-company-currency order. This PR is what makes the comparison user-facing, so fix it here: convert `order.amount_total` into the limit's currency (`order.currency_id._convert(order.amount_total, partner.currency_id, order.company_id, order.date_order or fields.Date.today())`). Also fix the base compute, which is pre-existing, not changed by this diff, but this PR depends on it: convert each order's `amount_total` the same way inside `_compute_td_open_credit`. If the author prefers a separate PR for the base compute, then this PR must at least convert the new order amount and the reliance on the unconverted `td_open_credit` should be recorded as a known defect.
- **SUGGESTION** (pre-existing, `res_partner.py` `_compute_td_open_credit`): the compute searches `('partner_id', '=', partner.id)`, but the check uses `commercial_partner_id`. Orders addressed to child contacts (delivery/invoice contacts) of the company are not counted in the company's open credit, which understates exposure. Use `('partner_id', 'child_of', partner.id)`. Also, `search` runs under the current user's record rules; a salesperson who sees only their own orders gets an understated open credit. Consider `.sudo()` for this read only.
- AC-03 otherwise matches: the check runs before `super().action_confirm()`, so the order stays in draft on error. `> limit` matches "exceeds".
- AC-04 (`td_credit_limit = 0` means no limit): implemented via the truthiness test `partner.td_credit_limit and ...`, correct. No code beyond SPEC.

### 2. Odoo conventions — findings
- **SUGGESTION** `sale_order.py:9-13`: confirm that `ValidationError` (`from odoo.exceptions import ValidationError`) and `_` (`from odoo import _, models`) are imported at the top of the file. They are not visible in the diff, and the only test never reaches the `raise`, so a missing import would pass CI and fail at runtime with a `NameError`. If absent, this becomes REQUIRED.
- **SUGGESTION** (pre-existing) `_compute_td_open_credit` is a non-stored compute with no `@api.depends`; acceptable for a non-stored field but should be stated explicitly.
- Naming and `_inherit` usage are fine. Manifest `depends` is not in the diff; confirm it includes `sale`.

### 3. Code quality — findings
- **SUGGESTION** `sale_order.py:9-13`: when `action_confirm` is called on several orders of the same partner at once, each order is checked against the same `td_open_credit` (none are in state `sale` yet), so a batch confirm can exceed the limit. Accumulate per commercial partner within the loop, or document the limitation.
- **SUGGESTION**: `td_open_credit` is recomputed per order inside the loop (one `search` each). Group by `commercial_partner_id` to avoid N queries on large batches.

### 4. Tests — findings
- **REQUIRED** `td_credit/tests/test_credit.py`: only `test_confirm_under_limit` exists. There is no test of the AC-03 behavior itself. Add: (a) over-limit confirm raises `ValidationError("Credit limit exceeded")` and the order remains `draft`; (b) limit reached exactly (equal) does not raise; (c) open credit from an already confirmed order is counted (create and confirm one order, then try a second that pushes over the limit); (d) a foreign-currency order case covering the finding in section 1.
- **REQUIRED** No test for AC-04: a partner with `td_credit_limit = 0` confirms an arbitrarily large order without error. Each AC needs a test, and green CI here only shows that the happy path works.

### Summary
The mechanics of AC-03 and AC-04 are implemented in the right place, but the comparison adds an order-currency amount to an unconverted open-credit sum, so the limit check is wrong for multi-currency orders (REQUIRED; the base compute is pre-existing but the PR depends on it and should not ship the check on top of it unaddressed). The test file covers only the non-blocking path, so the main AC-03 behavior and AC-04 are untested (REQUIRED). Green CI (12 tests) does not demonstrate either AC. Fix the REQUIRED items and re-review; then proceed to `security-review`.
