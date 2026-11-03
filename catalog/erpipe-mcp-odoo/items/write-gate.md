# Гейт записи erpipe `odoo-mcp` (детально)

Источник: https://github.com/erpipe-org/mcp-odoo, коммит `76ec136e0c89c414811a12629eb2903d2dc27357`, лицензия MIT. Файлы: `src/odoo_mcp/tools_write.py`, `agent_tools.py`, `server_core.py`,
`write_policy.py`, `audit.py`, `diagnostics.py`. Описание своими словами, код не скопирован; набросок ниже — наш.

## Поток

1. `preview_write(model, operation, values|values_list, record_ids, context, instance)`
   — проверки формы (операция ∈ create/write/unlink, ids обязательны для
   write/unlink, `values_list` только для create, ≤100), canonical payload,
   токен `odoo-write:` + первые 32 hex `sha256(canonical_json)`. Ничего не
   исполняет, в Odoo не ходит.
2. `validate_write(...)` — берёт живой `fields_get`; если метаданные
   переданы извне или пустые, одобрение **не сохраняется**. Иначе запись
   `{payload, expires_at=now+600}` в `app_context.write_approvals[token]`.
3. `execute_approved_write(approval, confirm)` — по порядку: токен совпадает
   с хешем payload → есть сохранённая валидация в этом процессе и не
   истекла → payload совпадает с сохранённым → `confirm=true` →
   `ODOO_MCP_ENABLE_WRITES=1`. Затем RPC, токен удаляется (одноразовый).
   Перед этим, если `ODOO_MCP_ELICIT_WRITES=1`, MCP elicitation с текстом
   «операция, модель, ids, новые значения (до 80 симв.), инстанс».
4. Каждый шаг пишет строку в JSONL-аудит (если включён).

## Что это защищает и что нет

- Защищает: от подмены значений/ids/базы между проверкой и исполнением;
  от записи без живой схемы; от записи вообще (env-выключатель).
- Не защищает: от агента, который сам решил изменить данные (все три шага
  он вызывает сам; `confirm=true` — его же параметр); от массового
  `write`/`unlink` (нет предела ids); от побочных действий allowlist-методов
  без аудита.

## `execute_method`

- `create/write/unlink` — отказ.
- Классификация по имени: read-only (`search*`, `read`, `fields_get`,
  `name_*`, `context_get`, `get_*`, `_get_*`), side_effect (`action_*`,
  `button_*`, `*send*`, `*post*`, `*validate*`, `message_post`), остальное
  unknown. side_effect и unknown блокируются, если нет точного
  `model.method` в env `ODOO_MCP_ALLOWED_SIDE_EFFECT_METHODS` или в
  `odoo_mcp_policy.json` (перечитывается на каждый вызов; ошибка файла =
  пустой список). `ODOO_MCP_ALLOW_UNKNOWN_METHODS=1` снимает блок.
- Домены в аргументах нормализуются; невалидный домен — ошибка.
- `cannot marshal None` → success + warning «уже закоммичено».
- Rate-limit опционален. **Аудита нет.**

## Как перенести к нам (набросок)

```
odoo_write / odoo_execute:
  if len(ids) > MAX_IDS: reject("разбей на партии, покажи список")
  if method not in allowlist[connection]: reject("метод не одобрен")
  before = read(ids, fields=values.keys() + ["display_name"])
  if client.supports_elicitation:
      ask_human(diff(before, values), connection, ids)   # человек, не модель
  else:
      require user_confirmed + payload_hash из предыдущего preview
  audit(connection, user, model, method, ids, values, outcome)
```

Allowlist хранить в git (как `odoo_mcp_policy.json`: `method`,
`reviewed_by`, `date`, `reason`) — изменения через PR.
