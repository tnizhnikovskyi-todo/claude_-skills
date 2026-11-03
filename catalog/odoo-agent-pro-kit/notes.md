# Журнал разбора: odoo-agent-pro-kit

## 2026-11-03 — первичный разбор

**Источник:** https://github.com/infovpcs/odoo-agent-pro-kit, коммит `99515db`
(2026-10-29), Apache-2.0 (+ `NOTICE`, автор Vinay Rana / VPCS). Клон в
scratchpad вне репо; ничего не запускалось (ни `bootstrap.sh`, ни хуки, ни
MCP, ни тесты).

### Что смотрели

- `README.md`, `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`.
- `plugin/hooks/hooks.json`, `session_start.sh`, `save_progress.sh`,
  `cleanup_mcp.sh`, `odoo_hook.py`, `checks/{odoo_lint,guard,common,paths}.py`.
- Скиллы: `Odoo19CodingStandard`, `OdooTools19`, `Odoo19ExistingDependencyContext`,
  `OdooRequirementGapAnalysis` (SKILL.md до Phase 7), заголовки
  `CommandingSystem/plan_analysis_workflow.md`, `start_coding_workflow.md`.
- `plugin/commands/*.md` (5 команд, 98 строк).
- `plugin/odoo_mcp/` (список инструментов, конфиг хоста), `context_guard.py` (шапка).
- Сеть/телеметрия: grep по URL, `requests/urllib/httpx/socket`, `telemetry/analytics/sentry`,
  `curl | sh`, `pip install`.

Не читали целиком: 640–1117-строчные скиллы тестирования/скриншотов/браузера,
`sandbox/` (Docker microVM), `integrations/` (другие агенты), `docs/`.

### Цифры

- 200 коммитов с 2026-07-19 по 2026-10-29, один автор-организация, PR-процесс, CI, ~50 тест-файлов.
- 31 скилл, 7449 строк в `SKILL.md`; `description` всех скиллов ≈ 7.5 тыс. символов
  (≈ 2 тыс. токенов в каждой сессии, где плагин включён).
- Хуки на 7 событий: SessionStart, UserPromptSubmit, PreToolUse (Bash, Write|Edit|MultiEdit),
  PostToolUse (то же), PreCompact, Stop, SessionEnd. Python-процесс на каждый Bash/Write/Edit.

### Сверка фактов Odoo 19 с исходниками ветки 19.0 (raw.githubusercontent.com)

| Утверждение кита | Где у них | Проверка | Итог |
|---|---|---|---|
| `res.groups.category_id` → `privilege_id`, `users` → `user_ids`, модель `res.groups.privilege` | `Odoo19CodingStandard`, lint L5 | `odoo/addons/base/models/res_groups.py:17,36` | верно |
| В поисковом виде `<group>` без `expand`/`string` | `Odoo19CodingStandard`, lint L4 | `odoo/addons/base/rng/common.rng`, define `group`: атрибутов `expand`/`string` нет | верно |
| `type='json'` устарел, использовать `jsonrpc` | `Odoo19CodingStandard`, lint L3 | `odoo/http.py:812-818`: «Since 19.0, @route(type='json') is a deprecated alias» | верно для 19 |
| Lint L3: на **18** warn «Use type='jsonrpc' on Odoo 18+» | `checks/odoo_lint.py` | `18.0/odoo/http.py`: типы только `http` и `json` (`routing_type = 'json'`, стр. 2328) | **ошибка**: совет сломает код на 18 |
| `ir.cron` без `numbercall`/`doall` | `Odoo19CodingStandard` | в `ir_cron.py` 19.0 их нет | верно (убраны ещё раньше) |
| Методы для XML-RPC должны возвращать не `None` | `Odoo19CodingStandard` | `addons/rpc/controllers/xmlrpc.py:114` `allow_none=False` | верно, но не «новое в 19» и не касается кнопок из веб-клиента |
| `<act_window …>` как допустимый элемент `import_xml.rng`, `view_mode="tree,form"` | `Odoo19CodingStandard`, раздел RNG | `odoo/import_xml.rng` 19.0: `act_window` нет ни разу | **ошибка** (элемент убран давно; `tree` в 19 тоже нет) |
| `_sql_constraints` → `models.Constraint` | `Odoo19CodingStandard`, `DependencyContext` | `odoo/orm/model_classes.py:162-163`: «'_sql_constraints' is no longer supported» (warning, атрибут игнорируется) | верно; но lint L6 лишь warn «prefer @api.constrains» только для CHECK — недооценка: в 19 ограничение молча не создаётся |
| `compute_sql` только с 19.3+, в 19.0 нет | `Odoo19CodingStandard` | `odoo/orm/fields.py` 19.0: `compute_sql` не найдено | верно |
| `type='product'` убран, `is_storable` | `Odoo19CodingStandard` | не сверяли (по памяти это изменение 18.0) | UNVERIFIED |
| Поля `res.partner` `mobile`, `title` убраны | — (в ките нет) | `res_partner.py` 19.0: есть `phone`, нет `mobile`/`title` | кит **не ловит** нашу главную ловушку из `synthesis.md` |

Также `OdooTools19/SKILL.md` содержит раздел «Copilot Agent Integration (v4.0+)» со ссылками на
`copilot_odoo_agent.py`, `model_selector.py`, `gpt-4o`, `claude-3-5-sonnet` — таких файлов в
репозитории нет, текст устаревший/выдуманный. Тот же `copilot_odoo_agent.py` упоминается в
`plan_analysis_workflow.md` (шаг 10).

### Безопасность

- Сеть: только локальный Odoo (`ODOO_URL`, по умолчанию `http://odoo:8069` в песочнице).
  Телеметрии и внешних эндпоинтов в коде плагина нет.
- MCP-сервер `odoo_mcp`: 7 инструментов чтения метаданных (`search_models`, `get_fields`,
  `get_relationships`, `validate_field`, `get_model_info`, `get_version_info`, `list_all_models`).
  В `plugin.json` не регистрируется — запускается вручную через `manage_modules.sh mcp-start`.
  В режиме песочницы `MCP_SERVER_HOST=0.0.0.0` (`config.py:40`).
- Хуки fail-open (любая ошибка → exit 0), молчат вне Odoo-модуля, но **внутри** блокируют:
  `git push/merge/tag/rebase`, `commit --amend`, `gh pr create/merge` без `ODOO_KIT_ALLOW_VCS_WRITE=1`
  или `.sandbox/AUTHORIZED`; любой запуск `odoo-bin` вне `sandboxctl`; `./manage_modules.sh` без `bash`;
  запись файлов с Enterprise-лицензией, приватными ключами, токенами. В наших облачных сессиях
  (пуш в ветку обязателен) это ломает рабочий процесс.
- `Stop`-хук может один раз заблокировать завершение, требуя записать результат тестов в
  `sessions/<mod>_progress.json`.
- В текстах скиллов есть установщики: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  (`OdooHermesEnvironmentSetup`), `pip install playwright/Pillow` — как инструкции агенту.
- В корне репо `.claude/settings.json` с хуками `scripts/contributor_hook.py` — сработают у любого,
  кто откроет клон как проект Claude Code.

### Сравнение с нашими

Тексты `odoo19-mvp-build:scaffolding` и `:code-dev` в этом контейнере недоступны
(`~/.claude/plugins/synced/*/` пуст; подключить `todoltd/claude-methodology-marketplace`
классификатор не разрешил). Сравнение с ними — по назначению из `inventory/current.md`
и `proposals/odoo19-mvp-build/`; построчное — открытый вопрос.

### Открытые вопросы

1. Дать доступ к текстам `scaffolding`/`code-dev` (или положить снимок в `proposals/`) для
   построчного сравнения.
2. Разрешить A/B: детерминированный линтер ловушек 19 (наша версия) против базовой модели
   на 3–4 задачах «напиши модуль» — сколько ловушек ловит барьер, которые модель пропускает.
3. Odoo 20-правила (L7–L17: `ir.access`, удаление `ir.rule`, `get_param`) не сверяли —
   нам пока не нужно.

## 2026-11-03 — правило главной сессии о записи источников

Главная сессия сообщила новое правило (п. 5 в `CLAUDE.md`): в карточке URL, SHA, лицензия, дата; в «Что взять» — `путь@SHA`, что, куда, как (дословно / пересказ / идея), разрешает ли лицензия. Применено: шапка и таблица в `README.md`, ссылки из `items/`.
