# Что мы взяли и откуда

Реестр заимствований: что у нас появилось, из какого источника, под
какой лицензией и как именно взято. Ведёт главная сессия при слиянии.
Подробности по каждому — в файле атрибуции, указанном в последнем столбце.

**Как взято:** «перевод/адаптация» — текст переведён и сокращён с
атрибуцией; «пересказ» — своими словами; «идея» — только принцип, текст
свой.

## Плагин `boost` (`plugins/boost/`, опубликован в `todoltd/claude-methodology-marketplace`)

| Что у нас | Источник (репозиторий @ коммит, файл) | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `interview-me` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) @ `301b02b` (v0.6.15), `skills/interview-me` | MIT | перевод/адаптация | `plugins/boost/skills/interview-me/references/attribution.md` |
| `source-check` | addyosmani/agent-skills @ `301b02b`, `skills/source-driven-development`; правило Context7 — [upstash/context7](https://github.com/upstash/context7); принцип №28 — [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all) `references/starter-principles.md` | MIT; MIT; CC BY 4.0 | перевод/адаптация; идея; пересказ | `plugins/boost/skills/source-check/references/attribution.md` |
| `cloud-memory` (+ хуки) | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) v15.8.3; one-skill-to-rule-them-all (task-observer 3.8.1); [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Apache-2.0; CC BY 4.0; Apache-2.0 | идея (код и текст свои) | `plugins/boost/skills/cloud-memory/references/attribution.md` |
| `lean-change` | [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail) @ `96608e0` (v5.3.3), `skills/ponytail/SKILL.md` | MIT | перевод/адаптация | `plugins/boost/skills/lean-change/references/attribution.md` |
| `repo-audit` | dietrichgebert/ponytail @ `96608e0`, `skills/ponytail-audit/SKILL.md`, формат из `skills/ponytail-review/SKILL.md` | MIT | перевод/адаптация | `plugins/boost/skills/repo-audit/references/attribution.md` |
| `odoo-model-map` (+ `odoo_map.py`) | [oraios/serena](https://github.com/oraios/serena), [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), graphify; принцип №28 — one-skill @ `ba696b2` | GPL-3.0+/MIT; MIT; Apache-2.0; CC BY 4.0 | идея (скрипт и текст свои) | `plugins/boost/skills/odoo-model-map/references/attribution.md` |
| `automation-audit` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) @ `a7ba5b9`, `plugins/claude-code-setup` (скилл `claude-automation-recommender` v1.0.0) | Apache-2.0 | пересказ и перевод, изменения отмечены (п. 4(b)) | `plugins/boost/skills/automation-audit/references/attribution.md` |
| `skill-feedback` + `observations/` | one-skill-to-rule-them-all (task-observer 3.8.1) | CC BY 4.0 | идея (текст свой) | `plugins/boost/skills/skill-feedback/references/attribution.md` |
| `independent-check` (**отклонён**, ветка-архив) | agent-skills (`doubt-driven-development`), [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill), [usestrix/strix](https://github.com/usestrix/strix) | MIT; MIT; Apache-2.0 | идея | ветка `build/independent-check`, `references/attribution.md` |

## Шаблоны (`templates/`)

| Что у нас | Источник | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `CLAUDE.md`: «Пол качества» | agent-skills, `constraint-driven-development` | MIT | пересказ | `templates/README.md` |
| `CLAUDE.md`: `shortcut:` и «Не проверено / риск» | ponytail, `skills/ponytail` | MIT | пересказ | `templates/README.md` |
| `CLAUDE.md`: «Отсутствие не доказывается поиском» | one-skill, принцип №28 | CC BY 4.0 | пересказ | `templates/README.md` |
| `CLAUDE.md`: правило Context7; `mcp.json` | upstash/context7 | MIT | идея | `templates/README.md` |
| `CLAUDE.md`: «Стиль и субагенты»; `CLAUDE-style.md` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (`caveman`, `cavecrew`) | Apache-2.0 | пересказ | `templates/README.md` |

## Правки плагинов `odoo19-*` (влиты в `todoltd/claude-methodology-marketplace`, `e4c70d8`)

| Что у нас | Источник | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `odoo19-mvp-build:security-review`: counterevidence, калибровка severity, ворота фикса, скоуп диффа | usestrix/strix @ `6b7ae2e`, knowledge packs (`counterevidence.md`, `severity_calibration.md`, `fix_verification.md`, `diff.md`) | Apache-2.0 | перевод/адаптация | `plugins/odoo19-mvp-build/skills/security-review/references/ATTRIBUTION.md` в маркетплейсе |
| `odoo19-mvp-build:pr-review`: 4-частная находка, «пол» качества, мутации, Prove-It | ponytail (`ponytail-review`); agent-skills (`constraint-driven-development`, `code-review-and-quality`) | MIT; MIT | перевод/адаптация | `plugins/odoo19-mvp-build/skills/pr-review/references/ATTRIBUTION.md` в маркетплейсе |
| Вопросы дискавери (`session-question-builder`, `kickoff-question-builder`): гипотеза к вопросу, Out of scope | agent-skills @ `301b02b`, `interview-me` (через наш `boost:interview-me`) | MIT | перевод/адаптация | `.../references/ATTRIBUTION.md` в маркетплейсе |
| Правило `siblings_checked` (`CLAUDE.md` маркетплейса) | one-skill (task-observer) | CC BY 4.0 | идея | `proposals/siblings-checked.md` |

## Процесс и критерии

| Что у нас | Источник | Лицензия | Как взято |
|---|---|---|---|
| `criteria.md` «Принципы, проверенные на практике» (№7, 12, 14–15, 16, 20, 24, 26, 28, 29) | one-skill, `references/starter-principles.md` | CC BY 4.0 | пересказ, номера сохранены |
| Чек-лист `repo-audit`: `ir.rule` дочерних моделей, пустые группы | собственный пилот (`pilot-notes/KEYS.md`, K12, K15) | — | своё |
| Список кандидатов третьего прохода | `HANDOFF_candidates_2026-11-03.md` из ветки `claude/bold-bell-5okjhm` (`6a6d764`), копия в `candidates-2026-11-03.md` | — | поиск по GitHub, только метаданные |

## Отклонено, ничего не взято

freellmapi, OmniRoute, headroom-desktop (приложение), serena (для Odoo),
rtk и codebase-memory-mcp (отложены после пилотов), Firecrawl и Context7
(ждут ключей) — см. `catalog/INDEX.md`.
