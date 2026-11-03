# odoo-spec-kit: рабочий журнал

Дата: 2026-11-03. Сессия анализа, ветка `analysis/odoo-spec-kit`.

## Что смотрели

- Клон `https://github.com/focuz-ai/odoo-spec-kit` в scratchpad (вне нашего репо).
  Ничего не запускали: ни `scripts/setup_assistant.py`, ни `pre-commit`, ни `openspec`.
- Ветки и SHA:
  - `main` = `e7d6e37b733bf5fe58402105fb97c62261029f52` (2026-11-03, forward-port 19.0 → main);
  - `19.0` = `23df08b4c1be58b632f8e77f163e5d2256925f9a` (**разобран этот**);
  - `18.0` = `e66b45a`, `17.0` = `bd04c73`, `16.0` = `5571652`;
  - `feature/16.0-sync-config-scripts` (другое дерево, не разбирали).
- **Главный факт:** у `16.0`, `17.0`, `18.0`, `19.0` и `main` одно и то же дерево
  `86c4484990cf9b7044c677343cd1aaf667bbf4fa` (`git rev-parse origin/<b>^{tree}`).
  Ветки «под версию» — это слияния без изменений; содержимое написано под 16.0
  (коммит `eceb604` «[FIX] docs: align version values with Odoo 16.0»).
  В «19.0» прямо стоит `ODOO_TARGET_VERSION: "16.0"` (`docs/base-standards.md:9`),
  `valid-odoo-versions=16.0` (`.pylintrc:10`, `.pylintrc-mandatory:10`),
  `--branch=16.0` (`.pre-commit-config.yaml:39`).
- Для сверки: sparse-клон `odoo/odoo@19.0` = `e0b25b7032aacb5bf711a119c40a466888e2fc16`
  (2026-11-03), только нужные файлы.
- Для лицензий/происхождения: `jeffrigby/somepulp-agents@e56195b` (MIT),
  `OCA/odoo-pre-commit-hooks@v0.1.6` (`3f66e31`, AGPL-3).
- Приватный маркетплейс `todoltd/claude-methodology-marketplace`: `add_repo` на чтение
  **отклонён классификатором прав**. Сравнение с `odoo19-mvp-build:spec-writer`/`code-dev`/
  `pr-review` — по описаниям скиллов в этой сессии (`anthropic-skills:odoo-spec-writer`,
  `security-review`), по `proposals/odoo19-mvp-build/` и по карточкам
  `catalog/odoo-agent-pro-kit`, `catalog/dooservice-odoo-skills`. Из приватного ничего не копировали.

## Лицензия и происхождение

- `LICENSE`: MIT, «Copyright (c) 2026 Focuz AI» (сверено по файлу). README: «Focuz AI S.A.C.».
- Не всё в репозитории — работа Focuz:
  - `ai-specs/skills/writing-skills/`, `using-git-worktrees/` — из `obra/superpowers` (MIT, по README кита;
    сам superpowers не клонировали).
  - `writing-skills/anthropic-best-practices.md` (1244 строки) — копия страницы документации Anthropic
    «Skill authoring best practices» (ссылки `mintcdn.com/anthropic-claude-docs`). Под MIT Focuz она не
    подпадает; брать нельзя и не нужно (у нас есть `skill-creator`).
  - `meta-prompt`, `show-spec-working`, `sync-agent-symlinks` — `author: LIDR.co` во фронтматтере;
    репозиторий-источник и его лицензию не нашёл (поиск `search/repositories` по `LIDR-academy` дал 422),
    **не проверено**.
  - `odoo-code-auditing` — адаптация `jeffrigby/somepulp-agents` `plugins/codebase-health/skills/code-auditing`
    (MIT, проверено клоном). Odoo-часть (`references/dead-code-methodology.md`) переписана Focuz под Odoo:
    в оригинале JS-примеры и инструменты, в ките — чек-лист точек входа Odoo.
  - `.pre-commit-config.yaml`, `.pylintrc*`, `.ruff.toml`, `prettier.config.cjs` — почти дословно шаблон OCA
    (`oca-addons-repo-template`); лицензию шаблона не проверял, брать конфиг не собираемся.

## Состав (19.0 = 16.0)

| Компонент | Что | Строк |
|---|---|---|
| `docs/base-standards.md` (= `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `codex.md` симлинками) | Главные правила: SDD, языки, workflow OpenSpec | 138 |
| `docs/backend-standards.md`, `frontend-standards.md`, `coding-guidelines.md`, `rpc-and-controllers.md`, `odoo-core-topology.md`, `git-guidelines.md`, `development-guide.md`, `documentation-standards.md`, `openspec-tasks-mandatory-steps.md`, `data-models/account.md` | Стандарты; 4 файла с `alwaysApply: true` | ~1550 |
| `ai-specs/agents/` (3) | `odoo-module-developer` (`model: sonnet`), `odoo-owl-developer`, `product-strategy-analyst` | ~280 |
| `ai-specs/skills/` (16) | workflow: `odoo-enrich-us`, `odoo-build-and-qa`, `odoo-adversarial-review`, `odoo-security-audit`, `odoo-ship`, `odoo-commit`; утилиты: `odoo-scaffold`, `odoo-test-runner`, `odoo-explain`, `odoo-code-auditing`, `update-docs`, `show-spec-working`, `meta-prompt`, `sync-agent-symlinks`, `using-git-worktrees`, `writing-skills` | ~3800 (из них writing-skills ~2850) |
| Линтеры | `pre-commit`: OCA maintainer-tools, OCA odoo-pre-commit-hooks v0.1.6, prettier+xml, eslint, ruff v0.13, pylint-odoo v9.3.15 (`.pylintrc` warn, `.pylintrc-mandatory` gate) | ~300 |
| `scripts/setup_assistant.py` | Локальный мастер путей Community/Enterprise → `config/local.paths.json`. Stdlib, без сети | 193 |
| `openspec/config.yaml` | Пустой шаблон OpenSpec | 20 |

Права/сеть/телеметрия:
- Хуков Claude Code, `.claude/settings.json`, MCP-конфигов, телеметрии нет. `.claude/` и `.agents/` в `.gitignore`,
  создаются симлинками по скиллу `sync-agent-symlinks`.
- На машину ставится: `npm install -g @fission-ai/openspec@latest` (README, без пина), `pre-commit` тянет 6 внешних
  репозиториев (теги/SHA пинованы) и npm-пакеты (prettier, eslint — пинованы).
- Побочные эффекты при `cp -rn odoo-spec-kit/* your-project/`: хук `oca-fix-manifest-website` с аргументом
  `https://github.com/focuz-ai/odoo-spec-kit` (`.pre-commit-config.yaml:34-35`) перепишет `website` в манифестах
  проекта на репозиторий Focuz; `oca-gen-addon-readme --org-name=focuz-ai --repo-name=odoo-spec-kit` (`:36-44`);
  `odoo-scaffold` ставит `'author': 'Focuz AI'`, `'website': 'https://focuz.ai'` (`SKILL.md:56-57`); в проект
  копируется `LICENSE` MIT Focuz, если своего нет.
- Автономные действия: `odoo-build-and-qa` — цикл «без вмешательства человека» (`SKILL.md:15-17`);
  `odoo-commit` делает `git push` и `gh pr create` (`SKILL.md:51-61`); `openspec-tasks-mandatory-steps.md:44-45`
  запрещает отдавать запуск тестов пользователю; `show-spec-working` выполняет `curl` к окружению с «restore».

Активность: 124 коммита, один автор (Harrison Chumpitaz), две вспышки — 2026-05-26…28 и 2026-11-02…03; ★2.

## Сверка утверждений кита с `odoo/odoo@19.0` (`e0b25b7`)

Кит формально предлагает ветку 19.0; ниже, что агент получит в 19.0-проекте.

| # | Утверждение кита (файл:строка @ `23df08b`) | Что в 19.0 | Источник 19.0 |
|---|---|---|---|
| 1 | «Обязательно `attrs`/`states`; булевы выражения `invisible="…"` не поддерживаются» (`docs/backend-standards.md:139-143`, пример `:160`; `ai-specs/agents/odoo-module-developer.md:55-59`, чек-лист `:102-103`) | Вью с `attrs`/`states` — ValidationError «Since 17.0, the "attrs" and "states" attributes are no longer used» | `odoo/addons/base/models/ir_ui_view.py:495-497` |
| 2 | Пример списка `<tree>` (`docs/backend-standards.md:190`) | Тип вью `list`, `tree` в selection нет; есть официальный кодмод `17.5-01-tree-to-list.py` | `ir_ui_view.py:149`; `ir_actions.py:401-402`; `odoo/upgrade_code/17.5-01-tree-to-list.py` |
| 3 | `type='json'` для RPC (`backend-standards.md:207`, `rpc-and-controllers.md:323`, пример `:358`) | Устаревший алиас, логируется, заменяется на `jsonrpc` | `odoo/http.py:812-818` |
| 4 | Внешние интеграции «предпочтительно XML-RPC/JSON-RPC» (`rpc-and-controllers.md:9-11`, `:15-16`) | `/xmlrpc`, `/xmlrpc/2`, `/jsonrpc` устарели в 19 и будут удалены в 22; есть JSON-2 (`json2.py`) | `addons/rpc/controllers/__init__.py:6-11`, `addons/rpc/controllers/json2.py` |
| 5 | «Для группировки используйте `read_group()`» (`backend-standards.md:98-99`; `odoo-code-auditing/SKILL.md:66`) | `read_group` помечен deprecated, надо `_read_group`/`formatted_read_group` | `odoo/orm/models.py:2754-2755` |
| 6 | `_sql_constraints` в порядке атрибутов модели (`coding-guidelines.md:79`) | Атрибут больше не поддерживается (только warning), нужен `models.Constraint` | `odoo/orm/model_classes.py:162-164`; `odoo/orm/table_objects.py:79` |
| 7 | `hr.contract` — модель контрактов (`docs/odoo-core-topology.md:20`) | В community 19.0 аддона `hr_contract` нет, контракты — `hr.version` (enterprise не проверяли) | `addons/hr/models/hr_version.py:34-35`; `git ls-tree HEAD addons/` без `hr_contract` |
| 8 | Тесты `TransactionCase` / `SavepointCase` (`odoo-enrich-us/SKILL.md:52`) | `SavepointCase` в `odoo/tests/` нет (есть `TransactionCase`, `SingleTransactionCase`, `HttpCase`) | `odoo/tests/common.py:990, 1186, 2211`; grep `SavepointCase` по `odoo/tests/` — 0 |
| 9 | Чаттер `<div class="oe_chatter">` с полями (`backend-standards.md:176-180`) | Форм-компилятор чаттера срабатывает на тег `chatter` | `addons/mail/static/src/chatter/web/form_compiler.js:46-48` |
| 10 | PostgreSQL 12+ (`backend-standards.md:12`) | `MIN_PG_VERSION = 13`; Python 3.10–3.14 (кит: 3.10+ — верно) | `odoo/release.py:39-41` |
| 11 | Сервисы `useService("rpc")`, `useService("user")` (`frontend-standards.md:165, 169`) | `rpc` — функция-импорт, `user` — объект-импорт. Регистрации сервисов в этих файлах нет (по всему `web` не искал) | `addons/web/static/src/core/network/rpc.js:93`; `addons/web/static/src/core/user.js:254` |
| 12 | Регистрация виджета поля классом: `registry.category("fields").add("x", MyColorField)` (`frontend-standards.md:344-351`) | Реестр полей валидирует объект `{ component, supportedTypes, … }` | `addons/web/static/src/views/fields/field.js:65-75` |
| 13 | QUnit + хелперы `@web/../tests/helpers/mock_env`, `…/helpers/utils` (`frontend-standards.md:27, 249-317`) | Новые тесты — Hoot (`static/lib/hoot`, `tests/_framework/*.hoot.js`); в `tests/helpers/` только `dom_test_helpers.test.js`, QUnit — в `tests/legacy/` | `git ls-tree HEAD addons/web/static/tests/helpers/` и `…/lib/` |
| 14 | `t-raw` «устарел и опасен» (`odoo-security-audit/SKILL.md:47`) | Верно: warning и компиляция как `t-out` | `odoo/addons/base/models/ir_qweb.py:2497-2506` |
| 15 | «Вместо `sudo()` всегда `with_user(SUPERUSER_ID)`» (`backend-standards.md:128-131`) | `with_user(SUPERUSER_ID)` тоже даёт режим суперпользователя (и меняет `env.user` на OdooBot) — не безопаснее `sudo()` | `odoo/orm/models.py:5999-6007` |
| 16 | Типы `api.Self`, `api.ValuesType` (`odoo-module-developer.md:91`) | В 19.0 есть (`odoo/orm/types.py:14-23`); для 16.0, под которую написан кит, — не проверял | `odoo/orm/types.py:14-23` |
| 17 | `@api.model_create_multi`, `Command`, `check_company`, `precompute` | Верно | `odoo/orm/decorators.py:357` (model_create_multi) |

Итог: из 17 проверенных утверждений 14 неверны или устарели для 19.0 (1–13 и 15; п. 10 частично: Python верно, PostgreSQL нет), 3 верны (14, 16, 17).
Для 16.0, под которую кит написан, утверждения 1–9, 11–13 в основном корректны — кит просто не адаптирован.

## Внутренние противоречия кита

- Язык кода: `base-standards.md:38-48` — код, комментарии, UI-строки на английском; `.cursor/rules/use-base-rules.mdc:15-16`
  и README «Estricto Español» — комментарии и имена переменных на испанском.
- Язык коммитов: `base-standards.md:49-50` — английский; `odoo-commit/SKILL.md:211`, `odoo-ship/SKILL.md:33-34` — испанский.
- Переводы: `coding-guidelines.md:183-184, 226-227` — «правильно `_("…%s") % x`», а их же `.pylintrc` включает
  `translation-not-lazy` (`.pylintrc:77`), которое ловит именно это.
- Шаблон `odoo-scaffold` пишет `# -*- coding: utf-8 -*-` (`SKILL.md:49, 90, 95`), а `.pylintrc-mandatory:92`
  включает `unnecessary-utf8-coding-comment`.
- `"use strict";` в каждом JS (`coding-guidelines.md:131`) при ES-модулях `@odoo/owl` из их же примеров.
- `odoo-security-audit`: «у каждой модели ровно одна строка в CSV» (`SKILL.md:23-24`) — обычно строк несколько (по группам).
- `odoo-test-runner` отдаёт traceback в «цикл авторемонта `/odoo-adversarial-review`» (`SKILL.md:66`), а
  adversarial-review по README и `SKILL.md:73` код не чинит.
- «Модель уровня Claude 3 Opus» для планирования (`base-standards.md:84`).

## Линтеры: что ловят сверх нашего T2

План T2 (`roadmap.md`): `<tree>`, `attrs=`, `type='json'`, `_sql_constraints`, `res.partner.mobile/title`,
`groups_id`, `_inherit=[…]` без `_name`, `numbercall`… с цитатой 19.0.

- В ките **нет своих правил**: только стандартные OCA-инструменты, настроенные на 16.0.
- OCA `odoo-pre-commit-hooks` v0.1.6 (список проверок из `src/` по тегу): из версионных — `xml-deprecated-oe-chatter`
  (только при версии модуля ≥ 18), `xml-deprecated-tree-attribute` (атрибуты `colors`/`fonts`/`string` у `<tree>`,
  не сам тег), `xml-deprecated-qweb-directive`, `xml-deprecated-data-node`/`openerp-node`. Не ловит `attrs`/`states`,
  `<tree>`, `type='json'`, `_sql_constraints`, `read_group`, `hr.contract`, `groups_id`.
- pylint-odoo v9.3.15 (`.pylintrc-mandatory`): `deprecated-name-get`, `deprecated-odoo-model-method`,
  `attribute-deprecated`, `sql-injection`, `invalid-commit`, `external-request-timeout`, `translation-*`,
  `no-write-in-compute`. Какие именно методы/атрибуты считаются устаревшими в v9.3.15 — **не проверено** (пакет не
  клонировали).
- Следствие конфигурации (не запускали): с `valid-odoo-versions=16.0` проверка `manifest-version-format` из
  обязательного гейта должна падать на манифестах `19.0.x.y.z`, т.е. на 19.0 гейт либо красный, либо его отключат.
- Сверх T2 из этого разбора (кандидаты правил, все сверены выше): `read_group(` (deprecated в 19.0), `hr.contract`,
  `SavepointCase`, `div.oe_chatter`, JS: `useService("rpc")`, `useService("user")`, `registry.category("fields").add(<Class>)`,
  `@web/../tests/helpers/` (QUnit-хелперы), `/xmlrpc`·`/jsonrpc` в интеграционном коде (warn, удаление в 22).
- Побочная находка: в `odoo@19.0` есть официальные кодмоды `odoo-bin upgrade_code` (`odoo/upgrade_code/`:
  `17.5-01-tree-to-list.py`, `18.1-00-sql-constraint.py`, `18.1-02-route-jsonrpc.py`, … LGPL-3). Для T2: в сообщении
  правила можно ссылаться на кодмод как на авто-исправление; код не копировать (LGPL), только идея.

## Формат спецификации против `spec-writer`

- `odoo-enrich-us` (`SKILL.md:62-73`): 8 разделов «Enhanced (Odoo Spec)» — контекст, ORM, вью, безопасность, логика,
  техсоображения, тесты/доки, DoD (Given/When/Then «предпочтительно»). Нет ID критериев, нет трассировки
  AC → код → тест, нет статуса утверждения, источник требований — тикет Jira/Plane.
- Наш `odoo-spec-writer` (по описанию): SPEC.md только из утверждённого ТР, `AC-01` ID дословно, без перенумерации,
  нет ТР — назад в `tr-*`. Наш формат строже; брать формат не нужно.
- Сильное у них: **ранний выход** (`SKILL.md:39-43`): перед проектированием искать в Community/Enterprise/своих
  аддонах; если покрывается стандартом или настройкой — остановиться и дать модуль/настройку, спецификацию не писать.
  У нас эта развилка — в дискавери (gap-анализ); на уровне `tr-odoo-tech-design` явного шага не видели (текст скилла
  не читали — только описание).
- **Правило запроса изменений** (`base-standards.md:106-116`): изменение после начала кода — сначала спецификация и
  `tasks.md`, потом код, потом снова verify/security/adversarial. У нас аналог для ТР-цепочки есть (Формат C в
  `tr-review`), для стадии сборки — не видели.
- **Правило завершённости задач** (`openspec-tasks-mandatory-steps.md:108-113`, `:44-47`): `[x]` только после
  выполненной команды проверки, результаты в отчёт рядом с изменением. Подходит для T13 (`PLAN.md`/`BUILD_STATE.md`).

## Шаблон `CLAUDE.md`

- Их `CLAUDE.md` = `docs/base-standards.md` (138 строк) + 4 документа `alwaysApply: true` (~550 строк) → в контексте
  постоянно ~700 строк, часть неверна для 19.0. Наш `templates/CLAUDE.md` — ~45 строк, только поведение.
- Идея «одна переменная версии наверху» (`base-standards.md:7-11`, коммиты `e6ff53e…` «centralize Odoo version
  definition») провалилась: версия не дошла ни до линтеров, ни до примеров, ни до веток. Вывод для нас: версию
  пишет человек в `CLAUDE.md`, а проверяет барьер (линтер сверяет префикс `version` манифеста с целевой версией).
- Мультикопилотные симлинки (`AGENTS.md`/`GEMINI.md`/`codex.md` → один файл) нам не нужны: работаем в Claude Code.

## Сравнение с соседними разборами

- `odoo-agent-pro-kit` (9/18): у них свой линтер версионных ловушек на 17–20 — у spec-kit своих правил нет.
- `dooservice-odoo-skills` (14/18): ~20 фактов 19.0 без расхождений, плагин на версию. У spec-kit на 19.0 — 14 из 17
  неверны, ветки версий фиктивные.
- spec-kit — пример того самого «справочника, который ошибается в ловушках версии» из `synthesis.md` (третий проход, п. 2),
  только хуже: ошибка не в отдельных фактах, а в целой версии.

## Решения и открытые вопросы

- Вердикт: **отклонить** как кит; взять 4 идеи (см. `README.md` «Что взять»).
- Открыто: лицензия `LIDR.co`-скиллов; реальный вывод pylint-odoo v9.3.15 на 19.0-модуле (не запускали — чужие
  инструменты без разрешения не запускаем); текст `tr-odoo-tech-design`/`code-dev` (приватный маркетплейс не подключён).
