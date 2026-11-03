# odoo-mcp-19: слой безопасности (`safety.py`, гейт в `server.py`)

- **Тип:** часть MCP-сервера (серверные барьеры записи)
- **Источник:** `AlanOgic/odoo-mcp-19@aea8542`, `src/odoo_mcp/safety.py`, `src/odoo_mcp/safety_profile.py`, `src/odoo_mcp/server.py:91-423`
- **Лицензия:** MIT
- **Вердикт:** адаптировать (в T3 `odoo-connector`)

## Как устроен

1. Чтение = закрытый список `SAFE_METHODS` (11 имён, `safety.py:44-57`); всё
   остальное — побочный эффект (fail-closed, `:222-243`). `default_get`
   сознательно не чтение: в 19.0 `sale.order.line.default_get` создаёт
   `sale.order` (`addons/sale_project/models/sale_order_line.py:27-61`).
2. `BLOCKED_MODELS` (`:92-147`): права, группы, пользователи, API-ключи,
   параметры, модули, и **прокси** — `ir.model.data`, `res.config.settings`,
   мастера пароля, `base_import.import`, `ir.mail_server`, `fetchmail.server`,
   OAuth/LDAP, portal-мастера, 2FA/сессии.
3. `PRIVILEGED_MODELS` (`:168-178`: server actions, automation, cron,
   `ir.model(.fields)`, `ir.default`, `ir.ui.view`) — только админ и всегда с
   подтверждением.
4. **Проверка связанной записи** (`:366-559`): x2many-команды в разрешённой
   модели, которые создают/меняют записи заблокированной (`res.partner.user_ids`),
   включая `null/false` = clear, голый dict = новая запись, ключи `default_*` в
   context, пути колонок `load` (`user_ids/login`); на many2many пропускает
   только link/unlink/set; если схему не получить — отказ.
5. Режимы `permissive`/`strict`/`locked`; `locked` = только чтение + allowlist
   `model.method` + bind localhost + проверка payload по `fields_get`.
6. Токен подтверждения: одноразовый, 120 с, привязан к хешу payload
   (`server.py:91-140`).

## Слабые места

- Подтверждение проводит агент (токен в `hint`), человек не нужен.
- Аудит: stderr, по флагу, без ids/payload/пользователя, «executed» до вызова.
- Нет лимита числа записей и diff «было → стало».

## Что взять

| Идея | Исходный файл | Куда у нас | Как | Лицензия |
|---|---|---|---|---|
| Список заблокированных моделей вместе с прокси-моделями | `src/odoo_mcp/safety.py@aea8542:92-147` | `odoo-connector/server/guard.py` (T3, маркетплейс) | идея; список собираем и сверяем с `odoo@19.0` сами (часть имён — из saas-19.x, например `ir.access`) | MIT |
| Проверка x2many/`default_*`/`load`-путей в заблокированную модель, fail-closed без схемы | `safety.py@aea8542:366-559` | там же | пересказ, код свой | MIT |
| `default_get` (и под вопросом `onchange`) — не чтение | `safety.py@aea8542:38-57`; факт — `sale_project/models/sale_order_line.py@19.0:27-61` | там же (сейчас в T3 они в списке чтений) | идея + наша проверка | MIT; LGPL-3 исходник только цитируем ссылкой |
| Привязка подтверждения к хешу payload (если оставляем агентское подтверждение) | `server.py@aea8542:91-140` | там же, вместе с elicitation из erpipe | идея | MIT |
| Отдельная категория «privileged»: код и схема (`ir.actions.server`, `ir.cron`, `ir.ui.view`…) — запрет по умолчанию | `safety.py@aea8542:160-189` | там же | идея | MIT |
