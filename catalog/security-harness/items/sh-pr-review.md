# sh-pr-review (ревью одного PR как гейт слияния)

- **Источник:** `plugins/security-harness/skills/sh-pr-review/SKILL.md@68748d5`,
  `plugins/security-harness/references/pr-review-mapping.md@68748d5`, `.../scripts/*.py@68748d5`
- **Вердикт:** адаптировать (текст правил), инструмент — отклонить

## Что делает

Резолвит PR (URL / номер / текущая ветка), кладёт код PR в отдельный worktree, не трогая
ветку пользователя. Триаж без агентов: глобы путей и regex-токены по **добавленным**
строкам → классы → Tier 0–3. Tier 0 — ноль агентов, только status. Дальше охотники только
по сработавшим классам, верификатор только на то, что может заблокировать слияние
(severity ≥ medium, confidence ≥ 80, `introduced`/`aggravated`). Отпечатки находок в
скрытых HTML-комментариях на PR, дедуп до траты токенов, локальный кэш. Постинг
`sh-pr-post.py`: ревью всегда `COMMENT`, гейт — commit status.

## Что взять (подробно в `../README.md`, «Что взять» 1–4)

1. **`pr_impact` с закрытым списком критериев.** Самое ценное. Наш `diff-scope.md`
   уже говорит «old sink, new reach», «weakened control», «removed control», но не даёт
   ярлыка, тай-брейка и не знает «newly chainable» / «blast radius increased». Правило
   `introduced` («или в функции с добавленной строкой») снимает вопрос P2 из
   `SCORES.md`.
2. **Триаж по тирам** → у нас правило запуска critic round. Набросок Odoo-сигналов:
   - Tier 0: только `*.md`, `i18n/*.po`, `static/description/`, тесты без групп/прав.
   - Tier 1: один класс (например, только вью без `groups=`).
   - Tier 2+: `security/*.csv`, XML с `ir.rule` / `res.groups` / `implied_ids`,
     `controllers/`, токены `sudo(`, `cr.execute`, `SQL(`, `Markup(`, `sanitize=False`,
     `safe_eval`, `auth=`, `csrf=False`, публичный метод без `_`.
   - Critic round — только с Tier 2.
3. **Стиль находки** (таблица «slop»).
4. **Отпечатки без номера строки** и «исправлено с прошлой итерации» — позже.

## Чего не брать

- Постинг по умолчанию: противоречит своему же описанию; у нас внешние действия только
  с подтверждения.
- Commit status и кэш: у нас нет CI-гейта на PR клиента.
- `--fail-on=medium` и порог 80: числа подогнаны под их рубрику, у нас VULN/REQUIRED.
