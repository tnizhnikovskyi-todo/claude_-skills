# Рабочий журнал: erpipe-org/mcp-odoo

## 2026-11-03, первичный разбор

**Что сделано.** Клон в scratchpad (вне репо), коммит `76ec136` (2026-08-25),
пакет `odoo-mcp` 1.3.2, MIT. Только чтение: сервер не запускали, к Odoo не
подключали, установщики/скрипты/примеры не трогали.

**Прочитано полностью:** `write_policy.py`, `audit.py`, `tools_write.py`,
нужные куски `agent_tools.py` (токен, preview/validate), `server_core.py`
(хранилище одобрений, TTL, аннотации), `diagnostics.py` (классификация
методов), `tool_helpers.normalize_domain_input`, начало `auth.py`,
`odoo_mcp_policy.json.example`, `odoo_config.multi.json.example`,
`SECURITY.md`, README (таблицы инструментов и env), один из 4 SKILL.md.
**Не читали построчно:** `odoo_client.py` (1010 строк), `diagnostics.py`
целиком, `tools_read.py`, `field_policy.py`, `cross_instance.py`,
`data_quality.py`, примеры и тесты. Выводы о них — по README и grep.

**Сеть/телеметрия.** grep по `src/`: исходящих вызовов, кроме Odoo
(XML-RPC/JSON-2) и опционального OAuth-introspection (`auth.py`, httpx2),
нет; упоминаний posthog/sentry/analytics/erpipe.com в коде нет. README
активно рекламирует хостинг ERPipe (`mcp.erpipe.com`) — это отдельный
продукт, в коде сервера не зашит.

**Активность.** 118 коммитов с 2025-03, 101 за последние полгода, последний
2026-08-25 (≈2.5 мес. назад). Один основной автор (Lê Anh Tuấn), репо
переехал из `tuanle96/mcp-odoo`.

## Ключевые наблюдения по безопасности записи

1. **«Подтверждение» по умолчанию — не человек.** Токен
   `odoo-write:<sha256[:32]>` — детерминированный хеш payload, не секрет.
   Цепочка preview → validate (живой `fields_get`, запись в память
   процесса на 10 мин) → execute(`confirm=true`) целиком выполняется
   агентом. Человек появляется только при `ODOO_MCP_ELICIT_WRITES=1` и
   клиенте с MCP elicitation; иначе — тихий фолбэк на токены.
   Реальная защита по умолчанию: `ODOO_MCP_ENABLE_WRITES=0` (запись
   выключена вовсе) + привязка токена к инстансу и точному payload.
2. **Нет предела на число записей для `write`/`unlink`.** Лимит 100 есть
   только для пакетного `create` (`values_list`). `record_ids` любой длины.
3. **Preview не показывает текущие значения** (нет diff «было → стало»,
   нет `display_name` затрагиваемых записей) — только запрошенные
   значения. «Diff summary» в README = список новых значений.
4. **`execute_method` не пишет в аудит.** `record_write_event` вызывается
   для preview/validate/execute/chatter/cross-instance, но не для
   `execute_method` (проверено grep). Значит `action_confirm`,
   `button_validate` и т.п. из allowlist проходят без журнала.
5. **Классификация методов по имени.** `create/write/unlink` запрещены в
   `execute_method`; `action_*`, `button_*`, `*send*`, `*post*`,
   `*validate*`, `message_post` → side_effect; остальное unknown. И то и
   другое блокируется, пока точное `model.method` не внесено в allowlist
   (env или `odoo_mcp_policy.json` с `reviewed_by/date/reason`, читается
   на каждый вызов, битый файл = пустой список, fail-closed). Слабое
   место: `get_*`/`_get_*` считаются read-only (кастомный `get_` может
   писать). Флаг `ODOO_MCP_ALLOW_UNKNOWN_METHODS=1` снимает всё.
6. **Невалидный домен больше не превращается в «все записи»** (фикс
   2026-08-14, `normalize_domain_input`): непарсимый домен — ошибка,
   а не `[]`. У нас стоит проверить то же самое.
7. **XML-RPC `cannot marshal None`**: метод, вернувший None, уже
   закоммичен; сервер отвечает success+warning, чтобы агент не повторил
   побочное действие. Полезная мелочь (№16 «прерванная операция частична»).
8. **Chatter** по умолчанию через тот же токен; `MCP_CHATTER_DIRECT=1`
   снимает гейт.
9. **Field ACL** на чтение (deny/allow по модели и инстансу) — убирает
   поля из всех read-путей. Кода не читали построчно.
10. **Cross-instance** чтение по всем базам: участие по умолчанию
    *включено* (`cross_instance` opt-out) — для клиентских баз минус.
11. **Ключи** в JSON-конфиге/env на машине, где запущен сервер (общий
    бот-пользователь на инстанс), не per-user. HTTP-транспорт без
    встроенной аутентификации (есть опциональный OAuth resource server),
    по умолчанию bind только localhost.

## Сравнение с нашим

- `odoo-mcp` (наш, инструкции в системном промпте этой сессии, схемы
  инструментов загружены): `odoo_search_read/create/write/execute/get_fields`,
  `connection_id` на каждом вызове, ответ всегда несёт `connection`,
  базы добавляются через админ-страницу, «уточни перед действием»,
  удаление/архивация/деструктивные методы требуют `user_confirmed=true`
  после явного «да» в чате. `odoo_create`/`odoo_write` (не архивация) —
  без гейта. Код нашего сервера не видели — только описания.
- `odoo-connector`: текст плагина в `~/.claude/plugins/synced/*/` в этой
  сессии не найден (папка пустая). Сравнение — по `inventory/current.md`
  и брифу (XML-RPC, per-user API-ключ). Отметить как непроверенное.
- `ivnvxd/mcp-server-odoo` (MPL-2.0): не клонировали; пересечение —
  тоже Odoo MCP с read-first подходом. Не разбирали.

## Открытые вопросы

- Есть ли у нашего `odoo-mcp` аудит-журнал записей и лимит на число ids?
  (нужен код сервера или его автор).
- Поддерживает ли наш клиент (Claude Code / claude.ai) MCP elicitation —
  тогда человеко-подтверждение можно сделать на стороне сервера, а не
  флагом `user_confirmed`, который ставит сама модель.
- Практический прогон erpipe-сервера на тестовой базе — только с
  разрешения пользователя.
