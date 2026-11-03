# Рабочий журнал: mcp-server-odoo

## 2026-11-03

**Что смотрели**

- Клон `https://github.com/ivnvxd/mcp-server-odoo` в scratchpad, main
  `64b52df7ae3bb13cd6e07bebaf36913a1141ac48` (2026-10-10, v0.9.0), 305
  коммитов. Ветка `dev` = `0543b95` (позади main на merge-коммит). Только
  чтение: сервер, тесты, Docker, скрипты не запускали.
- Лицензия: `LICENSE` — полный текст MPL 2.0; `pyproject.toml`
  `license = MPL-2.0`; Dockerfile-лейбл MPL-2.0. Посторонних файлов с
  другими лицензиями нет (vendored-кода нет, зависимости `mcp`,
  `python-dotenv`, `pydantic`). Авторы: Andrey Ivanov 264, dependabot 31,
  2 внешних по 2–3 коммита. Совпадает с поиском (MPL-2.0).
- Прочитано: `access_control.py` (целиком ключевые классы), `tools.py`
  (регистрация инструментов, удаление, `call_model_method`, блок-листы,
  x2many), `field_security.py`, `config.py` (эндпоинты), `json2_client.py`,
  `user_context.py` (блок инструкций), README целиком по разделам,
  `.env.example`, Dockerfile, `publish.yml`.
- Сеть: только Odoo (`urllib`/`xmlrpc.client`/`http.client`); внешних
  хостов в коде нет, телеметрии нет (grep `sentry|posthog|telemetry|analytics`
  — пусто). Установка: `uvx mcp-server-odoo` с PyPI (Trusted Publishing)
  или Docker-образ.
- Страница модуля `mcp_server` на apps.odoo.com (19.0): OPL-1, much.
  Consulting, 7679 строк. Код модуля не читали.
- Odoo 19: частичный, затем полный checkout `odoo/odoo@19.0`
  `e0b25b7032aacb5bf711a119c40a466888e2fc16` в scratchpad. Сверены
  JSON-2 (`addons/rpc/controllers/json2.py:48–55`), `X-Odoo-Database`
  (`odoo/http.py:1827`), `/web/version` (`addons/rpc/controllers/__init__.py:24`),
  `web_save_multi` (`addons/web/models/models.py:99`), `formatted_read_group`
  (`addons/web/models/models.py:800–803`), устаревание XML-RPC с удалением
  в 22 (`addons/rpc/controllers/__init__.py:6–8`), scope API-ключей
  (`odoo/addons/base/models/res_users.py:389, 1527`), `group_ids`
  (`res_users.py:257`; в README репо — старое `groups_id`).

**Что не получилось**

- `add_repo` на `todoltd/claude-methodology-marketplace` (чтение) отклонён
  классификатором авто-режима. `odoo-connector` сравнивал по карточке
  `catalog/erpipe-mcp-odoo/` (там код сверен по маркетплейсу `@7acde05`) и
  по `roadmap.md` (F1). Из приватного репо ничего не копировалось.
  Текущее состояние T3 (ветка `claude/odoo-connector-safety`) не видел.
- Тексты плагинов продаж (`sale_todo_claude`) для этой задачи не нужны —
  разбор про коннектор, не открывал.
- Наш `odoo-mcp`: видны только инструкции сервера в системном промпте
  (`connection_id`, `user_confirmed`); код не видел.

**Решения**

- Вердикт «адаптировать», 13/18. Сервер не ставим: дублирует `odoo-mcp`,
  настоящая защита — в закрытом OPL-модуле, без модуля только YOLO.
- Идеи — своими словами (MPL-2.0 файловый копилефт, приёмник частный).
- Две карточки в `items/`: клиентская модель доступа и Odoo-модуль.

**Открытые вопросы**

- Что из идей 1–7 уже сделано в T3? Сверить при слиянии.
- Есть ли у `odoo-mcp` проверка вложенных x2many-команд и путей домена?
  (Скорее нет — по инструкциям только `user_confirmed` на деструктивное.)
- Стоит ли переводить `odoo-connector` на JSON-2 (XML-RPC в 19 устарел,
  удаление в 22)? Предлагаю включить в T3 или отдельной задачей.
- A/B не делали (нет Odoo с модулем и разрешения запускать сервер).
- Место: полный checkout odoo 19.0 (1.4 ГБ) в scratchpad удалён после
  сверки.
