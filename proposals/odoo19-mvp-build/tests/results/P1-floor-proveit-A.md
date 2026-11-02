## PR Review: td_discount (PR #72, TD-131)

Skipped because the environment lacks them: running tests or CI, an Odoo instance, the KB connector. Based on diff text only.

### Verdict: REQUEST CHANGES

### 1. Spec compliance — findings
- The core fix is correct for AC-05. `max(order.order_line.mapped('discount') or [0])` takes the maximum over all lines; the empty-order case is handled by `or [0]`.
- **REQUIRED**: `td_discount/models/sale_order.py:~31-36` adds `_td_notify_manager()`, which is not in SPEC (AC-05 or the PR description): extra beyond SPEC. It is also in the wrong branch: it runs only for orders at or under the limit, which need no approval. If the notification was meant for `to_approve` orders, it is on the wrong path. Either remove it from this bug-fix PR, or add an AC for it and put it in the correct branch.

### 2. Odoo conventions — findings
- **REQUIRED**: `sale_order.py:~17`: `# noqa: C901` on `action_confirm` suppresses the complexity warning without a reason. The function is small, so it is unnecessary. Remove it.
- **SUGGESTION**: `order.state = 'to_approve'` is written directly; consider a dedicated method. Pre-existing, not blocking.

### 3. Code quality — findings
- **REQUIRED**: `sale_order.py:~33-36`: `try: order._td_notify_manager() except Exception: pass` swallows every error silently, hiding real failures (mail config, access rights). Fix: do not catch it, or catch the specific exception and `_logger.exception(...)`.
- **SUGGESTION**: Compute the max discount once per order via a small helper/compute so the logic is testable on its own.

### 4. Tests — findings
- **REQUIRED**: `tests/test_discount.py:~24`: `assertEqual(order.state, 'to_approve')` replaced with `assertTrue(order.state)`, which is always true. The only test for AC-05's "over limit goes to approval" checks nothing now. Restore the original assertion.
- **REQUIRED**: `@unittest.skip("flaky on CI")` on `test_under_limit_confirms` disables the "under limit → `sale`" test, the one that would catch `_td_notify_manager` side effects. Find the cause of the flakiness and fix it, or open a ticket and justify the skip. Green CI is not evidence here because the key tests are neutralised.
- **REQUIRED**: No regression test for TD-131. Add a multi-line case where the first line is under the limit and a later one is over (e.g. `discounts=[5.0, 15.0]`, limit 10%) and assert `to_approve`.
- **SUGGESTION**: Add boundary (discount equals limit confirms) and no-lines tests.

### Summary
The one-line fix for TD-131 is right. The PR also adds unspecified manager-notification behaviour on the wrong path with errors silently swallowed, adds a `noqa` suppression, weakens the AC-05 assertion to `assertTrue(order.state)`, skips the under-limit test and adds no regression test for the bug. With the tests neutralised, green CI proves nothing about AC-05. Fix the REQUIRED items and resubmit; only then go to `security-review`.
