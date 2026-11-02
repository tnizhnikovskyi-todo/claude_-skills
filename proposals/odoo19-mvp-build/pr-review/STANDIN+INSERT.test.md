<!-- Заменитель + вставка. Только для мини-проверок. -->
---
name: pr-review
description: Code-vs-spec review of a custom Odoo `td.*` module PR before the security gate.
---

# Odoo PR-Review — code vs SPEC

Review the PR diff of a `td.*` module against `SPEC.md`. Runs after `code-dev` / `testing`,
before `security-review`.

## Inputs
- PR diff, `SPEC.md` (AC-NN), test results.

## Review discipline (applies to every dimension)

### Finding format — no concrete case, no finding
Every finding has four parts; if you cannot write part 2 as a concrete case, it is not a finding.
```
[REQUIRED-1] {short title} — {file:line}   Origin: regression | newly reached | pre-existing
1. What:      {what this code does, one sentence a PM can read}
2. Problem:   {concrete case: "with <input/state>, <code> produces <wrong result>"; AC-NN affected}
3. Fix:       {the concrete change}
4. If not fixed: {consequence for the user / data / next stage}
```

### Regression vs pre-existing
For each finding check the base branch (`git show <base>:<path>`, `git blame`):
- **regression** — introduced by this diff → counts toward the verdict;
- **newly reached** — the defect existed, but this diff is the first to call/expose it → counts as a regression;
- **pre-existing** — on base, reach unchanged → goes to "Pre-existing (not blocking)", never into the verdict.
Never block a PR for pre-existing defects; never relabel a regression as pre-existing.

### Quality floor — any hit is at least REQUIRED
Grep the diff (added lines `+` / removed lines `-`) before anything else. The diff must not:
- add `# noqa`, `# pylint: disable`, `# type: ignore`, `# fmt: off` to silence a real warning;
- add `@unittest.skip*`, `self.skipTest`, comment out a test, or move it out of the test tags CI runs;
- delete or weaken a test: removed test method or `assert*`, `assertEqual`→`assertTrue`, narrower
  expected value, `assertRaises` removed, magic expected value copied from current output;
- lower a threshold: coverage, CI `--test-tags`, timeouts, linters config;
- add empty `except: pass` / `except Exception: pass`, `NotImplementedError`/`TODO` where an AC needs logic;
- widen ACL, add `sudo()` or a permissive record rule to make a test pass.
Exception only if the PR states the reason **and** an owner/expiry; still listed under "Floor exceptions".
The floor is checked even when spec compliance is perfect.

### Tests must be able to fail (mutation check)
Pick 1–3 AC-critical changed conditions (an `if`, a `domain`, a `@api.constrains`, a compute).
Mutate one at a time (invert the condition / return a constant), run the module's tests, revert.
Tests still green → finding "tests do not detect a broken AC-NN". No runnable Odoo here → do it
on paper: name the `assert` that would fail; none → the same finding, marked `static`.
Procedure and commands → `references/review-discipline.md`.

### Prove-It for bug fixes
A PR that fixes a defect must carry a test that **fails on base and passes on head**, asserting the
symptom from the bug report. Missing → `REQUIRED`. Can't run base → show from the code why the test
would fail there.

## Review dimensions
1. **Spec compliance** — every AC-NN in scope is implemented; nothing extra beyond SPEC.
2. **Odoo conventions** — models, fields, views, manifest `depends`, naming `td.*`, no deprecated v19 API.
3. **Code quality** — readability, duplication, error handling, performance (no N+1 in computes).
4. **Tests** — each AC has a test; tests pass.

## Output
```markdown
## PR Review: {module}
### Verdict: {APPROVE | REQUEST CHANGES}
### 1. Spec compliance — {PASS | findings}
### 2. Odoo conventions — {PASS | findings}
### 3. Code quality — {PASS | findings}
### 4. Tests — {PASS | findings}
### Quality floor
{PASS | list of hits with file:line} — Floor exceptions: {reason + owner, or "none"}

### Tests: mutation & Prove-It
| Mutated condition (file:line) | Mutation | Tests | Result |
|---|---|---|---|
| `models/td_order.py:57` `if amount > limit` | `>` → `>=` | `test_td_order.py` | killed / SURVIVED / static |
Prove-It: {n/a | test X fails on base, passes on head | MISSING}

### Pre-existing (not blocking)
{one line each, with a suggested ticket}

### Not checked
{what was not run or read, and the risk}
### Summary
```
Findings: `REQUIRED` (must fix), `SUGGESTION` (optional), each with file:line and a fix.

## Verdict rules
Any REQUIRED → REQUEST CHANGES.

| Condition | Verdict |
|---|---|
| Any quality-floor hit without a stated, owned exception | REQUEST CHANGES |
| Mutation survived on an AC-critical condition | REQUEST CHANGES |
| Bug-fix PR without a failing-first test | REQUEST CHANGES |
| Pre-existing defects only | do not affect the verdict; list them |

Otherwise APPROVE → `security-review`.

## DO / DO NOT
**DO** write every finding in 4 parts with a concrete case; tag its origin; check the quality floor first.
**DO NOT** report "consider…" without a case; block on pre-existing defects; accept a green test
run as proof that tests cover the change.
