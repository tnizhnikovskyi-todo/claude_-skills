# Рабочий журнал: odoo-functional-agent

Разбор 2026-11-03, сессия анализа. Репозиторий:
https://github.com/xmglord/odoo-functional-agent @ `084b6900027348b161d55442feb778829ff29fa2`
(2026-11-02, v0.1.3). Клон в scratchpad, вне нашего репо. **Ничего не запускали**:
ни `ofa`, ни хуки, ни тесты, ни Odoo-сервер, ни браузерный MCP. Только чтение.

## Что смотрели

- `LICENSE` — MIT, «Copyright (c) 2026 xmglord»; `plugin.json` и README тоже MIT.
  Происхождение: 81 коммит, все от одного автора (German Loredo Becerra),
  2026-10-26 → 2026-11-02; чужих файлов не нашли. Кода Odoo Enterprise в репо
  нет (правило проекта + `tests/test_repo_hygiene.py`). Справочник `knowledge/`
  ссылается на документацию Odoo (CC BY-SA 4.0), но в выборочной проверке
  (`down_payments.md`) текст свой, со ссылками на `файл@20.0`, а не копия доков.
- `README.md`, `docs/architecture.md`, `docs/guard.md`, `docs/plan_format.md`,
  `docs/scenario_format.md` (начало), `knowledge/README.md` (список «Known 20.0 drifts»).
- Скиллы: `skills/odoo-functional/SKILL.md` (215 строк) + `plan_md_template.md`,
  `skills/odoo-explain/SKILL.md`, `skills/help/SKILL.md`.
- Хуки: `hooks/hooks.json`, `hooks/ofa_guard.sh`; `hooks/ofa_guard_hook.py`
  (678 строк) — по описанию в `guard.md` и выборочно.
- Код: `src/ofa/guard.py`, `client.py` (весь), `executor.py` (начало),
  `source_index.py` (начало), поиск по `subprocess|urlopen|socket` во всём `src/`.
- Примеры: `examples/sales_crm_quote_to_cash/README.md`; список файлов остальных.

## Что проверили

- **Сеть/телеметрия.** HTTP только в `client.py` (`urllib`, JSON-2 на URL цели,
  который `guard.check_static` пускает лишь на loopback). Других хостов в `src/`,
  `hooks/`, `bin/` нет. Телеметрии нет. `subprocess`: запуск `odoo-bin`
  (`server.py`, `provision.py`), `psql`/`createdb` (`pg.py`), `git rev-parse/log`.
- **Что ставится на машину:** `bin/ofa`, `bin/ofa-check` в PATH сессии;
  `~/.config/ofa/config.toml` + файлы ключей; `~/.cache/ofa/` (индекс исходников);
  маркеры сессий в `${CLAUDE_PLUGIN_DATA}/active_sessions/`; локальный процесс
  Odoo; базы `ofa_demo_*` + шаблон в локальном Postgres.
- **Хуки во ВСЕХ сессиях машины:** `PreToolUse` на каждый `Bash` и `Skill` и
  `UserPromptSubmit` на каждый промпт запускают `sh` → `python3` (до 8 с,
  `onFailure: block`). До активации разрешают всё, но цена старта Python
  платится всегда. Это always-on — минус по `synthesis.md`.
- **Ссылки на прогоны битые:** README и README примеров ссылаются на
  `runs/<run_id>/report.md` и скриншоты, а `runs/` в `.gitignore` — в репо их
  нет. Заявленные результаты (37 ops, 4 сценария pass) проверить нельзя.
- **Факты Odoo, сверенные по `odoo/odoo`** (19.0 @ `e0b25b7`, 20.0 @ `b9823b8`):
  - `ir.config_parameter`: 19.0 — `get_param`/`set_param`
    (`odoo/addons/base/models/ir_config_parameter.py:60,82`); 20.0 — `set_str`/`get_str`
    (`:78,124`). Дрейф подтверждён.
  - `res.users.group_ids`/`all_group_ids` уже в 19.0 (`res_users.py:257-258`). Подтверждено.
  - `ir.access` есть только в 20.0 (`odoo/addons/base/models/ir_access.py:64-66`);
    в 19.0 — `ir.model.access` (`ir_model.py:2095-2096`) и `ir.rule` (`ir_rule.py:16`).
  - Курс валюты: 19.0 `('name', '<=', date)` (`res_currency.py:127`), 20.0
    `('name', '<', date)` (`:186`). Подтверждено.
  - `ir.attachment.datas` есть в 19.0 (`ir_attachment.py:473`), в 20.0 только `raw` (`:618`).
  - `product.template.store_by` только в 20.0 (`addons/stock/models/product.py:837`).
  - `stock.move.product_uom` (19.0, `stock_move.py:67`) → `uom_id` (20.0, `:68`);
    `purchase.order.line.product_uom_id` (19.0, `:43`) → `uom_id` (20.0, `:49`).
  - `account.tax.fiscal_position_ids`/`original_tax_ids` уже в 19.0 (`addons/account/models/account_tax.py:95,101`).
  - JSON-2 API есть и в 19.0: `addons/rpc/controllers/json2.py:49-53`
    (`/json/2/<model>/<method>`, `auth='bearer'`).
  - `fields_get` прячет поля, недоступные по группам (19.0 `odoo/orm/models.py:3364`),
    поэтому их линтер читает `ir.model.fields`. Подтверждено.
  - Cron не смотрит на `dbfilter`: 19.0 `odoo/service/server.py:99-100`
    (`cron_database_list` = `db_name` или `list_dbs`). Подтверждено.

## Сравнение с нашим

- `odoo19-sales-demo:demo-base-builder` — читали в публичном
  `tnizhnikovskyi-todo/sale_todo_claude` @ `2a7f7c1`
  (`plugins/odoo19-sales-demo/skills/demo-base-builder/SKILL.md`, `references/skill_conventions.md` §10).
  `demo-build-plan` в этом репо отдельным скиллом не найден (только упоминания);
  сравнивали по описанию в `demo-base-builder`.
- `odoo19-mvp-build:config-spec`/`config-runbook`/`config-review` и `odoo-connector` —
  **код не читали**: `add_repo` на `todoltd/claude-methodology-marketplace`
  отклонён классификатором режима auto. Сравнение по описаниям (`proposals/siblings-checked.md`,
  `proposals/odoo19-mvp-build/security-review/*`), по разбору `catalog/erpipe-mcp-odoo`
  (F1: у коннектора нет серверных проверок) и по инструкциям подключённого
  Odoo MCP в этой сессии (`connection_id` на каждый вызов, подтверждение удаления).
  Из приватного репо ничего не копировали.

## Решения

- Ставить как есть нельзя: только Odoo 20, только локальный Odoo+Postgres на loopback,
  always-on хуки; наши стенды удалённые (через Odoo MCP).
- Берём идеи и формат (MIT позволяет и перевод с атрибуцией): маркер стенда,
  правила одобрения + хеш плана, read-back и `pre_state`, «Test plan» с **Not tested**,
  роли-не-админы и негативные тесты, шаблон решения в плане, список дрейфов 19→20.

## Открытые вопросы

- Прочитать `config-spec`/`config-runbook`/`config-review` и `odoo-connector` в
  маркетплейсе (нужно разрешение на `add_repo` или главная сессия) и уточнить,
  что из пунктов «Что взять» там уже есть.
- A/B не делали: нужен прогон «план конфигурации с правилами / без» на 2–3
  требованиях Odoo 19 (разрешение пользователя).
- Маркер стенда: где хранить реестр «стенд → UUID» (в git маркетплейса? в
  конфиге коннектора?) — решить в T3.
