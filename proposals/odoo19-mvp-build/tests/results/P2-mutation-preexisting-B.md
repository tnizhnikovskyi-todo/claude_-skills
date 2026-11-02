## PR Review: td_credit (PR #80, AC-03)

Environment note: no Odoo instance, git repo, `/security-review`, KB connector or subagents. Mutation check done on paper (static). Base comparison is limited to the "Context" block in PR.md.

### Verdict: REQUEST CHANGES

### 1. Spec compliance — PASS (code), with a test gap (see 4)
- AC-03: `action_confirm` calls `_td_check_credit` before `super()`, so on error the order stays in draft. The limit is read from `commercial_partner_id` (reasonable). Comparison `>` matches "exceeds".
- AC-04: `partner.td_credit_limit and ...` skips partners with limit 0. Implemented, but untested (see 4).
- Nothing extra beyond SPEC.

### 2. Odoo conventions — PASS
Override of `action_confirm` with `super()`, `_inherit`, translatable message via `_()`. Imports of `ValidationError` and `_` are not visible in the hunk (see "Not checked").

### 3. Code quality — PASS
Small and readable. `td_open_credit` is computed per partner in a loop, which is fine for a per-order check.

### 4. Tests — findings

[REQUIRED-1] Tests do not detect a broken AC-03 — td_credit/tests/test_credit.py:20-22 (covers td_credit/models/sale_order.py:13-15)   Origin: regression
1. What: the only new test confirms a 200 order under a 1000 limit and asserts `state == 'sale'`.
2. Problem: no test confirms an order OVER the limit. With `raise ValidationError(...)` removed (or the condition made constant `False`), `test_confirm_under_limit` still passes (200 < 1000, state is `sale`). AC-03 ("raises ValidationError, order stays in draft") has no asserting test; green CI (12 tests) proves nothing about it. Static mutation survivors: see table.
3. Fix: add `test_confirm_over_limit`: with `with self.assertRaises(ValidationError): order.action_confirm()` for an order of 11 x 100 = 1100 > 1000, then `assertEqual(order.state, 'draft')`. Add a boundary test (total exactly 1000 confirms) and one with an existing confirmed order so `td_open_credit` is part of the sum (e.g. confirmed 800 + new 300 raises).
4. If not fixed: someone can delete or break the credit check and CI stays green; customers go over their credit limit.

[REQUIRED-2] AC-04 (limit 0 = no limit) has no test — td_credit/tests/test_credit.py   Origin: regression
1. What: `partner.td_credit_limit and ...` is the only thing implementing AC-04.
2. Problem: the fixture partner always has `td_credit_limit = 1000`. If the guard is dropped, the check becomes `open + amount > 0` and every order of a limit-0 partner is blocked; no test would fail.
3. Fix: add `test_no_limit`: partner with `td_credit_limit = 0`, a large order (e.g. qty 1000) confirms without error.
4. If not fixed: a refactor can silently block all partners without a limit.

### Quality floor
PASS. No `noqa`/`type: ignore`/skip, no removed or weakened tests, no thresholds changed, no `sudo()`/ACL changes, no empty `except`. — Floor exceptions: none

### Tests: mutation & Prove-It
| Mutated condition (file:line) | Mutation | Tests | Result |
|---|---|---|---|
| `models/sale_order.py:14` `... > partner.td_credit_limit` | `>` → `<=` | `test_confirm_under_limit` (200 <= 1000 raises, `order.action_confirm()` errors) | killed (static) |
| `models/sale_order.py:15` `raise ValidationError` | remove raise / condition constant False | `test_confirm_under_limit` (still `sale`) | SURVIVED (static) |
| `models/sale_order.py:14` `>` | `>=` (boundary) | none at the boundary | SURVIVED (static) |
| `models/sale_order.py:13` `partner.td_credit_limit and` | drop guard (AC-04) | none with limit 0 | SURVIVED (static) |

Prove-It: n/a (feature, not a bug fix)

### Pre-existing (not blocking)
- `td_credit/models/res_partner.py` `_compute_td_open_credit` sums `amount_total` in each order's own currency with no conversion to company currency, then compares to `td_credit_limit`. E.g. an open EUR order of 900 and a UAH limit of 1000 are treated as 900 UAH. The compute is unchanged by this PR and I cannot see from the provided context whether base code already reads it elsewhere; treated as pre-existing, not part of the verdict. Suggested ticket: "Convert open credit and order amount to company currency in td_credit". Note the new check line also adds `order.amount_total` unconverted, so the ticket should cover both. If it turns out this PR is the first caller of `td_open_credit` in a blocking path, re-label it "newly reached" and make it REQUIRED.

### Not checked
- Whether `ValidationError` and `_` are imported at the top of `sale_order.py` (hunk starts at line 8; a missing import would give `NameError` on the first over-limit confirm, which no test exercises).
- Other base callers of `td_open_credit`, `git blame`, the real test run (mutations were reasoned on paper, not executed).
- Multi-company, currency of `td_credit_limit` (Monetary field's currency field), and SPEC wording on currency: SPEC excerpt is silent.
- Security gate is a separate stage (`security-review`).

### Summary
Implementation matches AC-03 and AC-04 and the quality floor is clean, but the single added test only covers the under-limit path. Removing the `raise`, changing `>` to `>=`, or dropping the limit-0 guard all leave CI green, so AC-03 and AC-04 are unprotected. Two REQUIRED test findings, so REQUEST CHANGES. The currency-mixing in `_compute_td_open_credit` is pre-existing and listed separately.
