# Review discipline — details for `pr-review`

## 1. Quality-floor grep (run first)

```bash
BASE=origin/main   # the PR's base branch
git diff "$BASE"...HEAD -U0 -- . | grep -nE \
  '^\+.*(# *noqa|pylint: *disable|type: *ignore|fmt: *off|skipTest|unittest\.skip|@skip|except( Exception)?:\s*pass|NotImplementedError|TODO|FIXME|sudo\(\))'
git diff "$BASE"...HEAD -U0 -- '*/tests/*' | grep -nE '^-\s*(def test_|self\.assert)'   # removed tests/asserts
git diff "$BASE"...HEAD --stat -- '*/security/*' '.github/*' '*.cfg' '*.toml' '.pylintrc' '.pre-commit-config.yaml'
```
Each hit is a candidate: read it in context. A `sudo()` hit goes to `security-review` too, but a
`sudo()` added only to make a test green is a floor violation here.

Weakened-assert patterns to look for in modified tests: `assertEqual(x, 5)` → `assertTrue(x)`;
`assertEqual(len(recs), 3)` → `assertGreater(len(recs), 0)`; `with self.assertRaises(...)` removed;
expected value changed to whatever the new code returns without a SPEC/AC reason.

## 2. Mutation check procedure (Odoo)

1. Choose 1–3 conditions in **changed** code that implement an AC (state transitions, amount/limit
   comparisons, domains that filter by company/partner, constraints).
2. For each: apply one mutation — invert (`>`→`<=`, `in`→`not in`), drop a domain leaf, make a
   compute return a constant, remove a `raise ValidationError`.
3. Run only the module tests:
   `odoo-bin -d <testdb> -i <td_module> --test-tags /<td_module> --stop-after-init`
   (or the project's own test command / CI job).
4. Revert (`git checkout -- <file>`), confirm clean `git status`.
5. Record killed / SURVIVED. A survivor = the tests do not protect that AC → finding.

Static fallback (no Odoo instance, typical for cloud review): for each mutation, name the test and
the `assert` that would fail. If none would, report the survivor and mark it `static`.
Never commit a mutation; never leave the tree modified.

## 3. Prove-It for bug fixes

- The PR must add/modify a test that reproduces the reported symptom.
- Ideal proof: run that test on base (it fails) and on head (it passes). Commands:
  `git stash; git checkout <base> -- <module>/models; <run test>; git checkout HEAD -- <module>/models; git stash pop`
  — or simply reason from the code why the base version fails the assertion.
- A test that would pass on base too is not a Prove-It test (it does not test the bug).

## 4. Regression vs pre-existing — how to decide

| Question | Answer → origin |
|---|---|
| Is the defective line added/changed by the diff? | yes → regression |
| Line unchanged, but the diff adds the first caller / new route / new field that reaches it? | newly reached (counts as regression) |
| Line unchanged and reachable the same way on base? | pre-existing |

Check with `git show <base>:<path>` and `git log -L <line>,<line>:<path>` rather than memory.

## 5. 4-part format — example

```
[REQUIRED-2] Discount ignores company currency — models/td_order.py:88   Origin: regression
1. What:   computes the order discount from `amount_total`.
2. Problem: an order in EUR for a UAH company gets the discount limit compared in EUR against a UAH
   limit: 1 000 EUR passes a 10 000 UAH limit check (AC-07 broken).
3. Fix:    convert with `order.currency_id._convert(amount, company.currency_id, company, date)` before comparing.
4. If not fixed: managers approve discounts above their limit for foreign-currency orders.
```

Sources (ideas, re-written): ponytail `skills/ponytail-review` (MIT, v5.3.3) — 4-part findings,
"no concrete case = no finding"; addyosmani/agent-skills (MIT, 0.6.15) —
`constraint-driven-development` (quality floor), `code-review-and-quality` (mutation check,
pre-existing vs regression), `test-driven-development` (Prove-It: failing test first).
