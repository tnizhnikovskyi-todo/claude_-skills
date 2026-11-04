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
| `odoo19-lint` (+ `odoo19_lint.py`, 40 правил) | факты — [odoo/odoo](https://github.com/odoo/odoo) @ `e0b25b7` (19.0) и `f0ef96d` (18.0), цитаты `файл:строка`, ссылки на `odoo/upgrade_code`; идеи линтера — [infovpcs/odoo-agent-pro-kit](https://github.com/infovpcs/odoo-agent-pro-kit) (`checks/odoo_lint.py`), [ChengyanOo/odoo-lens](https://github.com/ChengyanOo/odoo-lens); правила второго круга — [panusbodee-owen/odoo-dev-skill](https://github.com/panusbodee-owen/odoo-dev-skill) @ `76e8b87`, [tanim913/odoo-migrate-to-20](https://github.com/tanim913/odoo-migrate-to-20) @ `a5507bf`, [focuz-ai/odoo-spec-kit](https://github.com/focuz-ai/odoo-spec-kit) @ `23df08b`; сверенные факты — unclecatvn, mart337i, dooservice | LGPL-3 (только ссылки); Apache-2.0; нет лицензии; нет лицензии; MIT; MIT | идея (код и текст свои) | `plugins/boost/skills/odoo19-lint/references/attribution.md` |
| `odoo-model-map`: правило `_inherit` списком (F5) и режим «трасса» | odoo/odoo `odoo/orm/models.py@19.0:240–249`, `odoo/models.py@18.0:245–250`; идея трассы — odoo-lens, mart337i/odoo-skills | LGPL-3 (ссылки); нет лицензии | идея | `plugins/boost/skills/odoo-model-map/references/attribution.md` |
| `interview-me`: радиус поражения, чекпоинт, стоп «дешевле потом», флаг противоречия | [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills) @ `ca5696a`, `skills/interview-me/SKILL.md`, `skills/brainstorm-prototypes/SKILL.md`; [MadurangaDev/requirement-engineer](https://github.com/MadurangaDev/requirement-engineer) @ `b728406`, `skill/references/reasoning-framework.md` | MIT; MIT | перевод/адаптация; идея; пересказ | `plugins/boost/skills/interview-me/references/attribution.md` |
| `source-check`: проверка на стенде; цитата вместо подтверждения в WebFetch | finding-unknowns @ `ca5696a`, `skills/assumption-test/SKILL.md`; [salespeak-ai/buyer-eval-skill](https://github.com/salespeak-ai/buyer-eval-skill) @ `ebb0e06`, `references/evidence-model.md` | MIT; MIT | перевод/адаптация; пересказ | `plugins/boost/skills/source-check/references/attribution.md` |
| `repo-audit`: `references/odoo-dead-code.md`, «утверждение — доказательство» | [focuz-ai/odoo-spec-kit](https://github.com/focuz-ai/odoo-spec-kit) @ `23df08b` (← jeffrigby/somepulp-agents @ `e56195b`); [garrytan/gstack](https://github.com/garrytan/gstack) @ `7caca33`, `investigate/sections/preamble.md`, `review/SKILL.md` | MIT; MIT; MIT | пересказ | `plugins/boost/skills/repo-audit/references/attribution.md` |
| `debug-root-cause` | gstack @ `7caca33`, `investigate/SKILL.md`; [cursor/plugins](https://github.com/cursor/plugins) @ `99b609a7`, `pstack/skills/blast-radius/SKILL.md` (© Lauren Tan) | MIT; MIT | перевод/адаптация | `plugins/boost/skills/debug-root-cause/references/attribution.md` |
| `skill-feedback`: формат правила (триггер-ситуация, тест точки решения, тавтологии), сигналы поправки, путь успеха | [ReflexioAI/reflexio](https://github.com/ReflexioAI/reflexio) @ `49659eb` (движок claude-smart), `reflexio/server/prompt/prompt_bank/playbook_extraction_context/v4.6.1.prompt.md` | Apache-2.0 | пересказ, изменено | `plugins/boost/skills/skill-feedback/references/attribution.md` |
| `skill-feedback`: `confidence` + доказательства, общее правило при повторе в 2+ проектах | [affaan-m/ECC](https://github.com/affaan-m/ECC) @ `b38be6a`, `skills/continuous-learning-v2/SKILL.md` | MIT | идея | там же |
| `weekly-review.md`: отложенные кейсы, no-regression по кейсу, ≤ 4 правки, правка ≠ грейдер | [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) @ `bc0a392` | MIT | пересказ / идея | там же |
| `weekly-review.md`: парное A/B версий, ничья = не сливать, лимит роста `SKILL.md`, режим `eval`/`manual`/`none` | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) @ `8a8b662`, `SKILL.md` | MIT | пересказ | там же |
| `weekly-review.md` / `evals/README.md`: A/B по `git diff`, стоп по плато, антипаттерны, leave-one-out, правило принятия | [huggingface/upskill](https://github.com/huggingface/upskill) @ `eec8ab4` | Apache-2.0 | идея / пересказ | там же; `plugins/boost/evals/README.md` |
| `cloud-memory`: «когда записывать», путь успеха для `bugfix`/`discovery` | reflexio @ `49659eb`, `playbook_should_generate/v3.0.0.prompt.md` | Apache-2.0 | пересказ, изменено | `plugins/boost/skills/cloud-memory/references/attribution.md` |
| `cloud-memory`: `memory/PLAN.md`, 3 неудачи → к пользователю, 5 вопросов handoff | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) @ `0fa6c79` | MIT | пересказ | там же |
| `evals/README.md` «Методика A/B»: 4 вопроса, активация и соседи, «сигнал → что чинить», контроль, шум, шапка окружения | [edonadei/caliper](https://github.com/edonadei/caliper) @ `89ab3b0` | MIT | пересказ | `plugins/boost/evals/README.md` |
| там же: пререгистрация, приманки для судьи; кейс «конкурирующий промпт» | [garrytan/gstack](https://github.com/garrytan/gstack) @ `7caca33`, `eval-plan/SKILL.md`; ECC @ `b38be6a`, `skills/skill-comply/` | MIT; MIT | идея | там же |
| `independent-check` (**отклонён**, ветка-архив) | agent-skills (`doubt-driven-development`), [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill), [usestrix/strix](https://github.com/usestrix/strix) | MIT; MIT; Apache-2.0 | идея | ветка `build/independent-check`, `references/attribution.md` |

## Процесс и критерии

| Что у нас | Источник | Лицензия | Как взято |
|---|---|---|---|
| `criteria.md` «Чек-лист безопасности скилла/плагина»; `catalog/_TEMPLATE.md` разделы «Условия использования / Отклонённые подозрения / Что не проверено» | [Consensys/repo-security-review](https://github.com/Consensys/repo-security-review) @ `d5128b0`; [berabuddies/Semia](https://github.com/berabuddies/Semia) @ `379bc25` | нет лицензии; Apache-2.0 | идея своими словами |
| там же: признаки supply-chain риска | Trail of Bits `supply-chain-risk-auditor` через [waybarrios/opencode-power-pack](https://github.com/waybarrios/opencode-power-pack) @ `c3328ad` | CC BY-SA 4.0 | только идея |

## Скрипты (`scripts/`)

| Что у нас | Источник (репозиторий @ коммит, файл) | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `scripts/skill-prescan.py`: 14 регулярок (`inj-*`, `sh-*`, помечены `[janitor]`), идея правил `uni-hidden`, `md-htmlcomment` | [khendzel/skills-janitor](https://github.com/khendzel/skills-janitor) @ `4b42f39`, `scripts/security.sh` стр. 93–134 | MIT | дословно (регулярки) с атрибуцией; остальное своё | docstring скрипта, `scripts/README.md`, `scripts/tests/skill-prescan/LICENSE-skills-janitor` |
| `skill-prescan.py`: дубли триггеров, lint frontmatter | skills-janitor @ `4b42f39`, `scripts/detect_dupes.sh`, `scripts/lint.sh` | MIT | идея, код свой (Unicode, стем, RU/UK) | `scripts/README.md` |
| `skill-prescan.py`: канал наружу, «заявление против поведения», закодированный мёртвый код, слепые зоны описи | [berabuddies/Semia](https://github.com/berabuddies/Semia) @ `379bc25` через `catalog/semia/items/skill_prescan.py` | Apache-2.0 | пересказ, код свой | docstring скрипта, `scripts/README.md` |
| `skill-prescan.py`: исключение для справок | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) @ `8a8b662` | MIT | идея | `scripts/README.md` |
| `skill-prescan.py`: поверхности исполнения (хуки, MCP, манифесты) | [Consensys/repo-security-review](https://github.com/Consensys/repo-security-review) @ `d5128b0` | нет лицензии | только идея | `scripts/README.md` |

## Правки плагинов продаж (`tnizhnikovskyi-todo/sale_todo_claude`, `6c4b4af`)

| Что у нас | Источник | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| Humizer: `check-humizer.py`, `shared/registers.md` §3/§7 (русизмы, кальки, бот-хвосты, апостроф `ʼ`) | [panchlab/humanizer-uk](https://github.com/panchlab/humanizer-uk) @ `849f329`; [git-voitenko/anti-ai-slop-writing](https://github.com/git-voitenko/anti-ai-slop-writing) @ `6f706e9` | MIT; MIT | списки с атрибуцией, код свой | `HUMIZER_PASS4_REPORT.md`, `shared/attribution.md` |
| `shared/buyer_diligence.md`, `defence-brief`, `demo-*`, `offer-finalizer`, `loss-pattern-analyzer`, `data-completeness-scorer`, `preliminary-estimate` | buyer-eval @ `ebb0e06`; LMTYdotcom/skills @ `18667e0`; mastering-technical-sales @ `8717c96` (книга — только идея); AI-PreSales-Skills @ `ab0752b`; claude-sow-creation @ `a2c4f18`; finding-unknowns @ `ca5696a`; ai-first-estimation @ `6a492dc`; software-estimation-skills @ `e5a989a` | MIT; MIT; MIT; MIT; нет; MIT; MIT; MIT | идея / пересказ | `shared/attribution.md`, `SALES_PASS4_REPORT.md` |

## Шаблоны (`templates/`)

| Что у нас | Источник | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `CLAUDE.md`: «Пол качества» | agent-skills, `constraint-driven-development` | MIT | пересказ | `templates/README.md` |
| `CLAUDE.md`: `shortcut:` и «Не проверено / риск» | ponytail, `skills/ponytail` | MIT | пересказ | `templates/README.md` |
| `CLAUDE.md`: «Отсутствие не доказывается поиском» | one-skill, принцип №28 | CC BY 4.0 | пересказ | `templates/README.md` |
| `CLAUDE.md`: правило Context7; `mcp.json` | upstash/context7 | MIT | идея | `templates/README.md` |
| `CLAUDE.md`: «Стиль и субагенты»; `CLAUDE-style.md` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (`caveman`, `cavecrew`) | Apache-2.0 | пересказ | `templates/README.md` |

## Правки плагинов `odoo19-*` и `odoo-connector` (влиты в `todoltd/claude-methodology-marketplace`: `e4c70d8`, выпуск 2026-11-03 — `206bb33`)

| Что у нас | Источник | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `odoo19-mvp-build:security-review`: counterevidence, калибровка severity, ворота фикса, скоуп диффа | usestrix/strix @ `6b7ae2e`, knowledge packs (`counterevidence.md`, `severity_calibration.md`, `fix_verification.md`, `diff.md`) | Apache-2.0 | перевод/адаптация | `plugins/odoo19-mvp-build/skills/security-review/references/ATTRIBUTION.md` в маркетплейсе |
| `odoo19-mvp-build:pr-review`: 4-частная находка, «пол» качества, мутации, Prove-It | ponytail (`ponytail-review`); agent-skills (`constraint-driven-development`, `code-review-and-quality`) | MIT; MIT | перевод/адаптация | `plugins/odoo19-mvp-build/skills/pr-review/references/ATTRIBUTION.md` в маркетплейсе |
| `odoo19-mvp-build` 0.9.3: таблица фактов Odoo 19 (`code-dev` и копии `odoo-version-notes.md`), F2–F4, M12 | `odoo/odoo` @ `e0b25b7` (19.0) и `f0ef96d` (18.0), цитаты `файл:строка`; подсказки — dooservice, unclecatvn, odoo-lens, mart337i, odoo-migrate-to-20, panus-odoo-dev-skill | LGPL-3 (только ссылки); MIT / нет лицензии | идея; факты сверены сами | `plugins/odoo19-mvp-build/skills/code-dev/references/ATTRIBUTION.md`, `T1_REPORT.md` (маркетплейс @ `206bb33`) |
| `odoo-connector` 0.2.1: allowlist, блок-листы моделей и методов, x2many/`default_*`/`load`, лимиты, JSONL-аудит, `odoo_preview`, `expected_marker` | [erpipe-org/mcp-odoo](https://github.com/erpipe-org/mcp-odoo); [AlanOgic/odoo-mcp-19](https://github.com/AlanOgic/odoo-mcp-19) `safety.py`; [ivnvxd/mcp-server-odoo](https://github.com/ivnvxd/mcp-server-odoo); [xmglord/odoo-functional-agent](https://github.com/xmglord/odoo-functional-agent) (маркер стенда); dooservice `connect.md` | MIT; MIT; MPL-2.0; MIT; LGPL-3 | идея, код свой | `plugins/odoo-connector/server/references/ATTRIBUTION.md`, `T3_REPORT.md` |
| `odoo19-mvp-build` 0.9.4: `security-review` (12 вопросов, барьер покрытия, insecure-defaults, fingerprint), `pr-review` (Gate Integrity, Evidence, scope ТР↔дифф, маховик), `testing` (ценность теста, G1–G4, доказательство установки), `architecture` (связность), `build-orchestrator` (`BUILD_STATE.md`) | cloudflare/security-audit-skill, gstack @ `7caca33`, ECC @ `b38be6a`, claude-sdlc-skills @ `49ef0b3`, security-harness @ `68748d5`, opencode-power-pack @ `c3328ad` (Trail of Bits), dooservice (`odoo/odoo:skills/odoo-security`), odoo-migrate-to-20 @ `a5507bf`, odoo-spec-kit @ `23df08b`, vladikk/modularity, planning-with-files | MIT; MIT; MIT; MIT; MIT; CC BY-SA 4.0; LGPL-3; MIT; MIT; CC BY-NC-SA 4.0; MIT | пересказ; идея (CC BY-SA, NC, LGPL) | `references/ATTRIBUTION.md` каждого скилла, `MVP_BUILD_PASS4_REPORT.md` |
| `odoo19-implementation` 0.3.0: `uat-test-book`; fail-closed в `acceptance-act-builder`; отчёт в `hypercare-tracker` | [Androbito/generate-test-book](https://github.com/Androbito/generate-test-book) @ `1aa864c`; [naodeng/awesome-qa-skills](https://github.com/naodeng/awesome-qa-skills) @ `fc10ba1`; odoo-functional-agent | нет лицензии; PolyForm Noncommercial 1.0.0; MIT | только идея своими словами | `plugins/odoo19-implementation/skills/uat-test-book/references/attribution.md`, `UAT_TEST_BOOK_REPORT.md` |
| Дискавери (initiation 0.12.0, sessions 0.7.0, closeout 0.5.0): скрытые требования, метки спикеров, «Розвідка», реестр `L-N`, gap/scope/SOW | requirement-engineer @ `b728406`; [s1vanov/follow-up](https://github.com/s1vanov/follow-up) @ `7f48598`; ba-skills @ `214f852`; finding-unknowns @ `ca5696a`; ECC @ `b38be6a` (context-and-decisions, © Matt Pocock); kevinlin/skills @ `0d3e083`; claude-sow-creation | MIT; CC BY 4.0 (изменено); MIT; MIT; MIT; MIT; нет лицензии | пересказ; идея | `references/` скиллов, `DISCOVERY_PASS4_REPORT.md` |
| `odoo19-tr-authoring` 0.7.0: «Повнота», AC «Не повинно / Перевірка», G1–G4, Runtime Contract, `trace_lint.py`, `tr-effort-instruction` | claude-sdlc-skills @ `49ef0b3`; generate-test-book @ `1aa864c`; awesome-qa-skills @ `fc10ba1`; finding-unknowns @ `ca5696a`; ECC @ `b38be6a`; ITSalt/NaCl @ `20fe4c6`; kevinlin/skills @ `0d3e083`; ai-first-estimation, software-estimation-skills | MIT; нет; PolyForm NC; MIT; MIT; MIT; MIT; MIT | пересказ; идея (без лицензии / NC) | `references/ATTRIBUTION.md` пяти скиллов, `TR_PASS4_REPORT.md` |
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
