<!--
ЗАМЕНИТЕЛЬ, НЕ ОРИГИНАЛ. Текст `odoo19-mvp-build:pr-review` в окружении не найден.
Этот файл — реконструкция по тому, что о скилле известно из соседнего `security-review`
(«code-vs-spec review», вердикт APPROVE / REQUEST CHANGES, AC-NN, SPEC.md, затем security-review).
Используется ТОЛЬКО как «текущий текст» в мини-проверках. Не применять.
-->
---
name: pr-review
description: Code-vs-spec review of a custom Odoo `td.*` module PR before the security gate.
---

# Odoo PR-Review — code vs SPEC

Review the PR diff of a `td.*` module against `SPEC.md`. Runs after `code-dev` / `testing`,
before `security-review`.

## Inputs
- PR diff, `SPEC.md` (AC-NN), test results.

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
### Summary
```
Findings: `REQUIRED` (must fix), `SUGGESTION` (optional), each with file:line and a fix.

## Verdict rules
Any REQUIRED → REQUEST CHANGES. Otherwise APPROVE → `security-review`.
