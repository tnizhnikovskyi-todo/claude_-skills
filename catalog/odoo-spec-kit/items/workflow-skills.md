# Скиллы workflow и утилиты (odoo-spec-kit)

- **Тип:** 16 скиллов (`ai-specs/skills/`) + 3 агента (`ai-specs/agents/`), экспонируются симлинками в `.claude/`
- **Источник:** `focuz-ai/odoo-spec-kit@23df08b`
- **Дата разбора:** 2026-11-03
- **Вердикт:** отклонить; взять 4 правила (идеи) и Odoo-чек-лист мёртвого кода (пересказ)

## Цепочка

`odoo-enrich-us` (тикет → «Enhanced Odoo Spec» из 8 разделов, Jira/Plane MCP опционально) → `/propose` (OpenSpec)
→ `odoo-build-and-qa` (apply → verify → `odoo-security-audit` → `odoo-adversarial-review`; при FAIL — авторемонт,
до 3 попыток) → `odoo-ship` (sync specs → archive → `odoo-commit`: commit, push, `gh pr create`).

## Против нашего `odoo19-mvp-build` (по описаниям; тексты в приватном маркетплейсе не читали)

| Их скилл | Наш аналог | Сравнение |
|---|---|---|
| `odoo-enrich-us` | `odoo-spec-writer` + цепочка `tr-*` | У нас SPEC только из утверждённого ТР, AC с ID без перенумерации, трассировка. У них формат без ID и трассировки. **Сильное у них:** ранний выход «закрывается стандартом/настройкой → не проектировать» (`SKILL.md:39-43`) |
| `odoo-adversarial-review` | `pr-review` (+ вставка 3.2) | Наш формат (4 части, пол качества, мутации, Prove-It) богаче. **Мелкое у них:** поле «где чинить: код/тест/спека/доки» и класс «вопрос/допущение» (`SKILL.md:57-66`); вердикт PASS WITH GAPS ≈ наш `open_proof_gap` |
| `odoo-security-audit` | `security-review` (+ Strix, 3.1) | Наш сильнее. У них ошибка «ровно одна строка ACL на модель» (`SKILL.md:23-24`); правило «`company_id` без `ir.rule` = Blocker» у нас уже в `repo-audit` (пилот K12/K15) |
| `odoo-build-and-qa`, `odoo-ship`, `odoo-commit` | `build-orchestrator`, `code-dev` | Автономный цикл с push/PR без человека — у нас не нужен. **Полезное:** правила из `docs/` — изменение после начала кода идёт через спеку (`base-standards.md:106-116`); `[x]` только после выполненной проверки (`openspec-tasks-mandatory-steps.md:108-113`) |
| `odoo-test-runner` | `testing` | Команды `odoo-bin --test-tags`; ничего нового |
| `odoo-scaffold` | `scaffolding` | Шаблон 16.0 с `# -*- coding: utf-8 -*-` (их же pylint это запрещает), `author: Focuz AI` |
| `odoo-code-auditing` | `boost:repo-audit` | Методика из somepulp (MIT). **Полезное:** `references/dead-code-methodology.md` — Odoo-точки входа, из-за которых «неиспользуемое» на деле используется |
| `odoo-explain`, `update-docs`, `show-spec-working`, `meta-prompt`, `sync-agent-symlinks`, `using-git-worktrees`, `writing-skills` | `interview-me`, `skill-creator`, встроенные worktree | Не нужны; часть — чужие тексты (superpowers, документация Anthropic, LIDR.co) |

Триггеры: описания по-испански, широкие («Úsalo cuando se requiera este flujo de trabajo»), `base-standards.md:78-79`
велит грузить скилл «автоматически при совпадении». В облачной сессии не проверяли.

## Что взять (детали — `../README.md`, «Что взять», п. 1–5)

1. Odoo-чек-лист ложных срабатываний при поиске мёртвого кода → `boost:repo-audit/references/` (пересказ, MIT).
2. «`[x]` только после выполненной команды проверки, результат рядом с планом» → T13.
3. «Изменение после начала кода — сначала ТР/SPEC, потом код, потом повтор ревью» → `code-dev`/`build-orchestrator`.
4. Ранний выход «закрывается стандартом» → сверить с `tr-odoo-tech-design`.
5. «Где чинить» и «вопрос/допущение» в находке → `pr-review`.

Все пункты — короткие вставки; эффект оценивать в общем A/B соответствующей задачи, отдельный скилл не нужен.
