# odoo-mcp-19: JSON-2 клиент (`odoo_client.py` + `arg_mapping.py`)

- **Тип:** часть MCP-сервера (транспорт)
- **Источник:** `AlanOgic/odoo-mcp-19@aea8542`, `src/odoo_mcp/odoo_client.py`, `src/odoo_mcp/arg_mapping.py`
- **Лицензия:** MIT
- **Вердикт:** адаптировать (как образец второго транспорта нашего коннектора)

## Что делает

Шлёт каждый вызов как `POST {url}/json/2/{model}/{method}` с
`Authorization: Bearer <API key>` и `X-Odoo-Database` (кроме `*.odoo.com`),
переводит позиционные аргументы в именованные по подписям `odoo@19.0`,
разбирает JSON-ошибку Odoo без пересылки traceback, повторяет 429 только для
чтения.

## Что даёт JSON-2 против XML-RPC (проверено по `odoo@19.0`, подробно в `../notes.md`)

| Тема | XML-RPC/JSON-RPC (`/xmlrpc/2`, `/jsonrpc`) | JSON-2 (`/json/2`) |
|---|---|---|
| Статус в 19.0 | deprecated, удаление в Odoo 22 (`addons/rpc/controllers/__init__.py:6-11`) | основной API |
| В 18.0 | есть | **нет** |
| Аутентификация | логин + пароль **или** API-ключ в поле пароля (`res_users.py:386-393`) | только Bearer API-ключ; scope `NULL`/`rpc`, срок действия (`ir_http.py:212-252`, `res_users.py:1725-1750`) |
| Состояние | `authenticate` → uid, далее uid+пароль в каждом вызове | stateless, без сессии (`save_session=False`) |
| Аргументы | позиционные `args` + `kwargs`; ошибка позиции даёт «тихо другой» вызов | только именованные, `signature.bind` → 422 (`json2.py:80-84`) |
| Ответ | XML-RPC не умеет `None` (`cannot marshal None`) | JSON, `null` нормально; recordset → ids |
| Ошибки | `Fault` со строкой | HTTP-код по типу исключения (422/403/404/409/500) + JSON `{name, message, arguments, context, debug}` |
| Приватные методы | `_…` запрещены | `_…`, `@api.private`, classmethod → 403 (`service/model.py:45-70`) |
| Транзакции | вызов = транзакция | так же: вызов = транзакция, повтор до 5 раз при serialization failure; цепочек нет |
| Права | ACL/record rules пользователя | те же; `@api.readonly` → read-only курсор/реплика |

Вывод: по **правам и транзакциям разницы нет**. Реальная польза JSON-2 —
жизнь после Odoo 22, ошибки с кодами, проверка имён аргументов, `None` без
фокусов, нет пароля в конфиге.

## Корректность

Подписи в `V2_ARG_MAPPING` совпали со всеми, что проверили
(`odoo/orm/models.py`: `search_read` 5767, `search` 1376, `search_count` 1360,
`read_group` 2755, `default_get` 1271, `name_search` 1527, `export_data` 880,
`load` 895, `create` 4617). Отказ на непереводимый позиционный аргумент
(`arg_mapping.py:232-235`) и на дубль позиционный/именованный (`:241-247`) —
правильная защита. Fallback «первый аргумент список int → `ids`» (`:226-230`)
эвристичен: метод `@api.model`, принимающий список id первым параметром,
получит 422 — это видно, не опасно.

## Что взять

| Идея | Исходный файл | Куда у нас | Как | Лицензия |
|---|---|---|---|---|
| Второй транспорт JSON-2 для баз ≥ 19.0 (Bearer, `X-Odoo-Database`, голое тело, ошибка по коду) | `src/odoo_mcp/odoo_client.py@aea8542:90-168` | `odoo-connector/server/odoo_client.py` (маркетплейс) | пересказ, код свой | MIT, можно |
| Таблица подписей «позиция → имя» и отказ вместо молчаливого пропуска | `src/odoo_mcp/arg_mapping.py@aea8542:30-255` | там же | идея; подписи берём из `odoo@19.0` сами | MIT; факты — из исходника Odoo |
| Не повторять побочный вызов при 429 | `odoo_client.py@aea8542:177-201` | там же | идея | MIT |
