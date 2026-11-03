# odoo-mcp-19: рабочий журнал

Дата: 2026-11-03. Сессия анализа, ветка `analysis/odoo-mcp-19`.

## Что смотрели

- `AlanOgic/odoo-mcp-19` @ `aea8542de5bb549ca92e27681e7133d70163c6b9`
  (2026-11-02, v2.2.0), клон в scratchpad. Читали: `LICENSE`, `pyproject.toml`,
  `README.md`, `Dockerfile`, `run-docker.sh`, `.github/workflows/*`,
  `src/odoo_mcp/odoo_client.py`, `arg_mapping.py`, `safety.py` (целиком),
  `server.py` (гейт, токены, `execute_method`, `batch_execute`),
  `api_reference.py` (утверждения о JSON-2). `resources.py`, `prompts.py`,
  `module_knowledge.json`, `user_clients.py`, `__main__.py` — выборочно
  (поиск сети, `subprocess`, `eval`).
- `odoo/odoo@19.0` @ `e0b25b7032aacb5bf711a119c40a466888e2fc16` (sparse:
  `odoo/`, `addons/rpc`, `addons/web/controllers`, `addons/sale_project/models`).
- `odoo/odoo@18.0` @ `f0ef96d85606d076251515cbcdb69adb2c1b659e` (только дерево и
  `odoo/http.py`): есть ли JSON-2 в 18.0.
- Приватный `todoltd/claude-methodology-marketplace`: `add_repo` на чтение
  **сработал**. `main` @ `7acde05` (`plugins/odoo-connector`) и ветка T3
  `claude/odoo-connector-safety` @ `c1e5462`. Ничего оттуда не копируем,
  ниже только наши выводы своими словами.

Ничего чужого не запускали: ни сервер, ни тесты, ни `run-docker.sh`, ни Docker.

## Происхождение и лицензия

- `LICENSE`: MIT, «Copyright (c) 2026 Alan»; совпадает с `pyproject.toml`
  (`license = "MIT"`). Поиск не соврал.
- Не форк: первый коммит `04f4677` (2026-01-26) — «Initial release», 14 файлов
  с нуля; заголовков чужих копирайтов нет. 158 коммитов, ~95% от одного автора
  (`alanogic`/`Alan`), 1 внешний.
- Справочные тексты (`api_reference.py`, `orm_guides.py`) ссылаются на
  `odoo/documentation` (`external_api.rst`) и исходники Odoo (LGPL-3). Лицензию
  документации Odoo не проверяли — поэтому из этих текстов ничего дословно не
  берём; наши факты ниже сверены с исходником сами.

## JSON-2 против XML-RPC/JSON-RPC: проверено по `odoo@19.0`

| # | Утверждение | Источник `odoo@19.0` | Итог |
|---|---|---|---|
| 1 | Один маршрут `POST /json/2/<model>/<method>`, `auth='bearer'`, `type='json2'`, `save_session=False`; всё прочее под `/json/2` — 404 с подсказкой | `addons/rpc/controllers/json2.py:38-56` | верно |
| 2 | Тело — именованные аргументы + `ids` + `context`; сигнатура проверяется `inspect.signature().bind` → 422 при лишнем/недостающем имени | `json2.py:57-64`, `:80-84` | верно |
| 3 | `ids` к `@api.model`-методу → 422 | `json2.py:75-77` | верно |
| 4 | Неизвестная модель или метод → 404; приватный (`_…`, `@api.private`, classmethod) → `AccessError` 403 | `json2.py:65-74`; `odoo/service/model.py:45-70` | верно |
| 5 | Ответ — голое значение, без конверта `{"result":…}`; recordset → список id | `json2.py:86-90`; `odoo/http.py:2644-2663` | верно |
| 6 | Ошибка: JSON `{name, message, arguments, context, debug}`; `debug` — полный traceback | `odoo/http.py:468-478`, `:2665-2688` | верно (сервер `debug` клиенту не пересылает: `odoo_client.py:156-158`) |
| 7 | Коды: UserError/ValidationError 422, AccessError/AccessDenied 403, MissingError 404, LockError 409, прочее 500 | `odoo/exceptions.py:15,50,84,106,116`; `http.py:2669-2686` | верно |
| 8 | Невалидный домен → 500 `ValueError` (не молчаливый пустой результат) | `odoo/addons/test_http/tests/test_webjson2.py:156-170` | верно |
| 9 | Аутентификация: `Authorization: Bearer <API key>`; ключ активного пользователя, scope `NULL` или `rpc`, не просроченный; без ключа → 401 (или сессия браузера с `Sec-Fetch-*`) | `odoo/addons/base/models/ir_http.py:212-252`; `res_users.py:1725-1750` | верно; пароль JSON-2 не принимает |
| 10 | XML-RPC тоже принимает API-ключ вместо пароля | `res_users.py:386-393` | **да** — «вход по ключу» не преимущество JSON-2 само по себе; преимущество — что пароль не пройдёт вовсе |
| 11 | Транзакция: один вызов = одна транзакция; commit при успехе, rollback при ошибке; до 5 повторов при конфликте сериализации; цепочки вызовов в одной транзакции нет | `odoo/http.py:2266-2330`; `odoo/service/model.py:160-200` | верно; у XML-RPC так же |
| 12 | Методы с `@api.readonly` идут на read-only курсор (реплику); при попытке записи — повтор на RW | `json2.py:23-35`; `odoo/orm/decorators.py:345-353`; `http.py:2297-2311` | верно |
| 13 | Выбор базы: заголовок `X-Odoo-Database` (stateless), конфликт с cookie → 403 | `odoo/http.py:1827-1838`; `test_webjson2.py:42-78` | верно. «На `*.odoo.com` заголовок даёт 404» — по исходнику не проверить (SaaS), отмечено как утверждение автора |
| 14 | `/xmlrpc`, `/xmlrpc/2`, `/jsonrpc` устарели в 19.0, удаление запланировано в Odoo 22 | `addons/rpc/controllers/__init__.py:6-11`; `xmlrpc.py:144,159`; `jsonrpc.py:14` | верно (warning в лог на каждый вызов) |
| 15 | JSON-2 в 18.0 нет | `odoo@18.0`: нет `addons/rpc`, в `odoo/http.py` нет `json2` | верно → **наш дефолт `o18-artel-prod` по JSON-2 не работает** |
| 16 | Подписи `search_read`, `search`, `search_count(domain, limit)`, `read_group(…, orderby, lazy)`, `default_get(fields)`, `name_search`, `export_data(fields_to_export)`, `load(fields, data)`, `create(vals_list)` | `odoo/orm/models.py:5767, 1376, 1360, 2755, 1271, 1527, 880, 895, 4617` | `arg_mapping.py` совпадает со всеми |
| 17 | `read_group` deprecated в 19.0, `check_access_rights` deprecated с 18.0, `name_get` удалён | `models.py:2752-2755`, `:4166-4168`; `def name_get` нет | верно |
| 18 | `res.users.apikeys.generate` (выпуск ключа через RPC) — «с 19.1+» (комментарий в `safety.py:100-105`) | `res_users.py:1636-1637` — есть уже в **19.0**, за флагом `base.enable_programmatic_api_keys` или для админа (`:1631-1634`) | неточность комментария; модель всё равно заблокирована |
| 19 | `default_get` может писать (обоснование, почему он не в `SAFE_METHODS`) | `addons/sale_project/models/sale_order_line.py:27-61` — создаёт `sale.order` | верно |

Утверждения про saas-19.1…19.4 (scope `rpc` обязателен, `ir.access`, удаление
`toggle_active`, `get_param`) по 19.0 не проверить — у нас нет этих веток. Не
переносим без своей проверки.

## Корректность реализации

Хорошо:
- Клиент `odoo_client.py` — честный JSON-2: Bearer, `X-Odoo-Database`, голое
  тело, разбор ошибки без traceback клиенту (`:90-168`).
- `arg_mapping.py`: позиционные → именованные по точным подписям 19.0;
  непереводимый позиционный аргумент и один параметр дважды → ошибка, а не
  молчаливый пропуск (`:232-247`). Это прямо закрывает класс ошибок, который
  JSON-2 вскрывает (422).
- 429-повтор только для чтения: побочный вызов не повторяется
  (`odoo_client.py:144`, `:189-191`).
- `safety.py`: «всё, что не известное чтение, — побочный эффект»
  (`is_side_effect_method`, `:222-243`); `default_get` сознательно не чтение
  (`:41-43`); 40 заблокированных моделей, включая прокси (`ir.model.data`,
  `res.config.settings`, мастера пароля, `base_import.import`, `ir.mail_server`,
  OAuth/LDAP) (`:92-147`); проверка x2many-записи в заблокированную модель через
  разрешённую (`res.partner.user_ids` → `res.users`), включая `null/false` = clear,
  голый dict = new, ключи `default_*` в context, пути колонок `load`
  (`:366-559`); fail-closed, если схему не загрузить.
- Токен подтверждения: одноразовый, 120 с, привязан к model+method+**хешу
  payload** (`server.py:91-140`).

Слабо / ошибки:
- **Подтверждение проводит сам агент**: токен возвращается в `hint`
  (`server.py:400-405`), человек в контуре не нужен. Это защита от подмены
  payload и от «всегда `confirmed=true`», а не согласие пользователя (как и у
  erpipe без elicitation).
- Аудит только в stderr и только при `MCP_SAFETY_AUDIT=true`; без ids, payload и
  пользователя; `executed: true` пишется **до** вызова Odoo (`safety.py:824-854`,
  `server.py:421-422`) — неуспешный вызов тоже попадёт как выполненный.
- Нет предела числа записей: `record_count` считается, но в `strict` любой
  размер проходит после токена (`safety.py:722-736`).
- Нет diff «было → стало».
- `batch_execute`: каждая операция — отдельная транзакция, `atomic=True` лишь
  останавливает (честно написано в описании инструмента, `server.py:841-842`).
- `load_config` читает `.env` из текущего каталога с `override=True`
  (`odoo_client.py:338-351`); `run-docker.sh` делает `source .env`. Мелочь.
- README местами отстаёт от кода: «token bound to model+method» (код — ещё и
  payload), в документации «27 resources» против 38.

## Сравнение с нашим

`odoo-connector` @ `7acde05` (main): XML-RPC (`/xmlrpc/2`), один пользователь,
5 инструментов, без серверных проверок (F1).

Ветка T3 `claude/odoo-connector-safety` @ `c1e5462` (не слита): allowlist
`model.method` в `policy.json`, `max_records=20`, проверка домена, JSONL-аудит,
preview. По сравнению с odoo-mcp-19 в ней (пересказ, без кода):
1. **`default_get` и `onchange` в списке «чтений»** — проходят без allowlist,
   лимита и аудита. `default_get` в 19.0 может создать `sale.order`
   (строка 19 таблицы выше). `onchange` не проверяли — риск.
2. **`create`/`write` разрешены на `*`** — значит и на `res.users`,
   `res.groups`, `ir.rule`, `ir.model.access`, `ir.config_parameter`,
   `res.users.apikeys`… Защита только правами пользователя Odoo. Нет списка
   заблокированных моделей и нет проверки x2many-путей (`res.partner.user_ids`),
   ключей `default_*` в context, колонок `load`.
3. Сильнее odoo-mcp-19: лимит записей, JSONL-аудит, preview «было → стало».

erpipe-mcp-odoo: тоже agent-проводимое подтверждение (но умеет MCP
elicitation), allowlist, без лимита ids. odoo-mcp-19 сильнее erpipe в проверке
связанных записей и списке прокси-моделей; слабее в аудите.

dooservice `connect.md`: метод (dry-run с откатом, «да» до записи, архив вместо
удаления) — это поведение агента, у odoo-mcp-19 его нет.

## Вопросы и решения

- Пользователь в этой сессии вопросов не задавал; работал автономно по заданию.
- Решение: сервер не ставить (дублирует коннектор, 3 инструмента «любой метод»,
  подтверждение без человека, Docker/venv на машине). Переносим механику
  защиты в T3 и план перехода на JSON-2 с двумя транспортами.

## Открытые вопросы

- Есть ли `/web/version` в 18.0 (для выбора транспорта) — не проверяли, в 19.0
  есть (`addons/rpc/controllers/__init__.py:24`). Альтернатива без сомнений —
  `common.version()` по XML-RPC.
- Поведение `X-Odoo-Database` на Odoo.sh / `*.odoo.com` — живой проверки нет.
- `onchange` через RPC: пишет ли что-то в стандартных аддонах 19.0.
- Тесты автора (433 функции, офлайн, CI на py3.10–3.13) не запускали.
