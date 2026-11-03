# ivnvxd/mcp-server-odoo

- **Тип:** MCP-сервер (Python, stdio / Streamable HTTP) + платный/OPL Odoo-модуль `mcp_server` (отдельный продукт, не в репозитории)
- **Источник:** https://github.com/ivnvxd/mcp-server-odoo (★411, PyPI `mcp-server-odoo`)
- **Лицензия:** MPL-2.0 — сверено по файлу `LICENSE` (полный текст MPL 2.0), `pyproject.toml` (`license = MPL-2.0`), Dockerfile-лейблу; все файлы — один автор (Andrey Ivanov, 264 из 300 коммитов; остальное dependabot и 2 внешних контрибьютора). Модуль `mcp_server` на apps.odoo.com — **OPL-1**, автор much. Consulting, 7679 строк, кода в репозитории нет.
- **Версия / коммит:** 0.9.0, `64b52df7ae3bb13cd6e07bebaf36913a1141ac48` (main, 2026-10-10)
- **Дата разбора:** 2026-11-03
- **Вердикт:** **адаптировать** (идеи модели доступа в T3 / `odoo-connector`; сервер не ставить)

## Что делает

MCP-сервер для Odoo 16–20: 16 инструментов (+17-й `call_model_method` по
флагу) — поиск, чтение, поля, агрегация, создание/правка (одна запись и
пачкой до 100), удаление одной записи, чаттер, вложения — и ресурсы
`odoo://…`. Два режима: **стандартный** (через Odoo-модуль `mcp_server`,
который держит allowlist моделей и прав, аудит и rate limit) и **YOLO**
(прямой XML-RPC/JSON-2 без модуля: `read` — только чтение, `true` — всё).

## Какую слабость Claude закрывает

Живые данные Odoo и действия в нём. У нас это уже есть (`odoo-connector`,
наш `odoo-mcp`). Новое для нас — **модель доступа «модель × операция» и
проверки отношений** (вложенные x2many-команды, пути в доменах, вложения и
сообщения проверяются по владельцу-документу).

## Модель доступа и безопасность записи (главный вопрос)

| Вопрос | Стандартный режим (с модулем) | YOLO `read` | YOLO `true` |
|---|---|---|---|
| Где проверка | **на стороне Odoo** (модуль проверяет каждый вызов через свой прокси `/mcp/xmlrpc/object`) + дублирующая проверка в клиенте с кешем 5 мин | в клиенте | нет |
| Что разрешено | allowlist моделей, на каждую — флаги read/write/create/unlink + «Allow Method Calls» (по умолч. выкл.) | только read-операции | всё, в т. ч. `ir.cron`, `ir.actions.server` через CRUD |
| Произвольные методы | `call_model_method` — только при флаге модели (по описанию модуля) | нет | только при `ODOO_MCP_ENABLE_METHOD_CALLS=true`; блок-лист |
| Удаление | `delete_record` — **одна запись за вызов**, проверка `unlink` + существование | нет | да |
| Массовая запись | `create_records`/`update_records` ≤ 100, одна транзакция; при несуществующем id — ничего не пишется | нет | так же |
| Вложенные x2many | `[0]`→create, `[1]`→write, `[2]`→unlink на связанной модели; для one2many `[4]`→write, `[3]/[5]/[6]`→write+unlink (`tools.py:185`) | — | — |
| Чтение через связи | пути `a.b.c`, `any`, `order` и `groupby` по x2many требуют read на каждой пройденной модели (`access_control.py:755`) | — | — |
| Вложения/сообщения/активности | право по документу-владельцу (`_gate_document_records`, `tools.py:1371`) | — | — |
| Подтверждение человеком | **нет** (ни elicitation, ни токена, ни preview/diff); только MCP-аннотации `destructive_hint` | — | — |
| Аудит | **в модуле** (каждый вызов, отказ, логин; хранение 30 дней по умолч.); в клиенте — только `logger.info` для `call_model_method` без значений | лог процесса | лог процесса |
| Rate limit | в модуле, на пользователя | нет | нет |
| Ключи | личный ключ пользователя; у модуля есть scope «MCP only», OAuth 2.1 и группа MCP User (снятие группы отзывает ключи) | любой | любой |
| Несколько баз | **одна база на процесс** (`ODOO_DB`); несколько — отдельными записями сервера; модуль различает базы по host/`X-Odoo-Database` | так же | так же |
| Компании | `ODOO_ALLOWED_COMPANIES` — контекст, «не граница безопасности» (сам автор) | так же | так же |

Честные оговорки самого автора (README «How standard mode applies the model
allowlist»): проверки не покрывают записываемые related-поля и `_inherits`
(запись `email` у `res.users` меняет партнёра; поля компании живут в
`res.partner`), many2one/many2many-ссылку можно поставить на запись
невключённой модели.

### Блок-лист `call_model_method` (YOLO)

`tools.py:120–180`, `_validate_method_call` (`tools.py:518`): модели
`ir.actions.*`, `ir.cron`; методы `run`, `method_direct_trigger` на любой
модели; все `web_*`; ORM-примитивы (`create`, `write`, `unlink`, `read`,
`search*`, `copy`, `sudo`, `with_user`, `with_context`, `load`,
`export_data`, `name_create`, `get_views`…); имена только публичные ASCII
(`_`-префикс запрещён). Результат-список обрезается до 100.

## Сравнение с нашим

| | `odoo-connector` (F1) | наш `odoo-mcp` | erpipe | **mcp-server-odoo** |
|---|---|---|---|---|
| Проверки на сервере | нет | `user_confirmed` на деструктивное (ставит модель) | write-флаг, allowlist `model.method`, токен | **модуль в Odoo**: модель × CRUD, method-флаг, аудит, rate limit |
| Удаление | любое `unlink` | с `user_confirmed` | через гейт | только 1 id за вызов |
| Предел ids | нет | ? | create ≤100, write/unlink без предела | create/update ≤100, delete = 1 |
| Вложенные команды/связи | нет | ? | нет | **да** (лучшее из виденного) |
| Человек в контуре | текст SKILL.md | флаг модели | elicitation (опц.) | нет |
| Аудит | нет (только аудит Odoo) | ? | JSONL, без методов | в Odoo, все вызовы (модуль) |
| Несколько баз | одна | `connection_id` на каждом вызове | `instance`, дефолт молча | одна на процесс |
| Odoo 19 | XML-RPC | ? | XML-RPC/JSON-2 | стандарт — прокси модуля; YOLO — JSON-2 авто |

`odoo-connector` сравнивался по сверке кода в карточке `catalog/erpipe-mcp-odoo/`
(маркетплейс `@7acde05`); доступ к приватному маркетплейсу в этой сессии
получить не удалось (см. `notes.md`). Состояние T3 (в работе) не учтено.

С `dooservice-odoo-skills` (`connect.md`: dry-run с откатом, «да» до записи,
архив вместо удаления) и `odoo-agent-pro-kit` пересечение только по теме:
у mcp-server-odoo нет ни dry-run, ни диалога подтверждения — его сила в
серверной модели прав, а не в процедуре.

## Odoo 19 — сверка по `odoo/odoo@19.0` (`e0b25b7`)

| Утверждение репо | Проверка | Итог |
|---|---|---|
| JSON-2: `POST /json/2/<model>/<method>`, bearer-ключ, база в `X-Odoo-Database` | `addons/rpc/controllers/json2.py:48–55` (`auth='bearer'`), `odoo/http.py:1827` | верно |
| `/web/version` без логина | `addons/rpc/controllers/__init__.py:24` (`auth='none'`) | верно |
| `web_save_multi` есть с 19 | `addons/web/models/models.py:99` | верно |
| `formatted_read_group` — метод 19 | `addons/web/models/models.py:800–803` (`@api.model @api.readonly`) | верно |
| XML-RPC в 19 | `addons/rpc/controllers/__init__.py:6–8`: `/xmlrpc`, `/xmlrpc/2`, `/jsonrpc` устарели, удаление в 22 | репо уходит на JSON-2 в YOLO — правильно; стандартный режим зависит от прокси модуля |
| Пример `user_ids.groups_id.name` в README | `odoo/addons/base/models/res_users.py:257`: в 19 поле `group_ids` | мелкая неточность документации (имя до 19) |

Для нашего `odoo-connector` важно: он ходит XML-RPC, а в 19 это
устаревший путь с удалением в 22 — повод перейти на JSON-2 вместе с T3.

## Проверка

Сервер и тесты не запускали (недоверенный код, разрешения не было).
Разбор по коду: `access_control.py`, `tools.py` (обработчики записи,
блок-лист), `field_security.py`, `config.py`, `json2_client.py`,
`user_context.py`, README, страница модуля на apps.odoo.com.

| Задача | Без него | С ним |
|---|---|---|
| A/B не делали | — | — |

## Оценка

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | Как сервер дублирует наш `odoo-mcp`; ценны идеи модели доступа |
| Частота | 2 | Odoo-данные нужны еженедельно, но канал уже есть |
| Надёжность | 3 | ~1550 тестов, CI, ruff/ty, аккуратные ошибки (`Unavailable` ≠ `Denied`, fail-closed) |
| Стоимость контекста | 2 | 16–17 схем инструментов + блок инструкций при подключении |
| Безопасность | 2 | Код прочитан, сеть только к Odoo, телеметрии нет; но гарантии стандартного режима — в закрытом OPL-модуле (не читали), YOLO снимает всё, нет человека в контуре |
| Поддержка | 3 | Активно (90 коммитов с августа, релиз 0.9.0 от 2026-10-10), один основной автор |
| **Итого** | **13/18** | |

## Что взять

Лицензия MPL-2.0 — файловый копилефт: дословный код потянет MPL на наш
файл. Поэтому всё ниже — **своими словами / только идея**, без копирования
кода. Приёмник у всех пунктов — `odoo-connector` (задача T3, маркетплейс) и
наш `odoo-mcp`.

| # | Идея | Исходный файл | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| 1 | Политика «модель × операция» (read/write/create/unlink) + отдельный флаг «методы» на модель, всё не перечисленное — отказ; ошибка проверки ≠ отказ, но тоже fail-closed | `mcp_server_odoo/access_control.py@64b52df` (`ModelPermissions`, `check_operation_allowed`, `AccessControlUnavailableError`) | `odoo-connector`: файл политики рядом с allowlist `model.method` из erpipe | своими словами | MPL-2.0, идея — да |
| 2 | Вложенные x2many-команды проверять как операции на связанной модели (`0`→create, `1`→write, `2`→unlink, one2many `3/5/6`→write+unlink, `4`→write) | `mcp_server_odoo/tools.py@64b52df` (`_nested_operations`, стр. 185) | `odoo-connector`: `odoo_write`/`odoo_create` | своими словами (таблица соответствия — факт Odoo) | MPL-2.0, идея — да |
| 3 | Чтение через связи: точечные пути, `any`, `order`, `groupby` по x2many требуют права на каждой модели пути; несбалансированный префиксный домен — ошибка | `mcp_server_odoo/access_control.py@64b52df` (`check_related_paths`, `check_domain_balance`) | `odoo-connector`: `odoo_search_read` | только идея | MPL-2.0, да |
| 4 | Вложения, сообщения, активности, фолловеры — право по документу-владельцу (`res_model/res_id`), не по `ir.attachment` | `mcp_server_odoo/tools.py@64b52df` (`_gate_document_records`), `access_control.py` (`document_owners`) | `odoo-connector` | только идея | MPL-2.0, да |
| 5 | Удаление — только по одному id; массовые create/update ≤ 100 и атомарно; перед update проверка существования всех id | `mcp_server_odoo/tools.py@64b52df` (`MAX_BATCH_RECORDS`, `_handle_delete_record_tool`) | `odoo-connector`: лимит ids (дополняет erpipe-идею 2 — у него unlink без предела) | только идея | MPL-2.0, да |
| 6 | Блок-лист для «произвольного метода»: `ir.actions.*`, `ir.cron`, `run`/`method_direct_trigger` везде, `web_*`, ORM-примитивы, `_`-методы | `mcp_server_odoo/tools.py@64b52df` (стр. 120–180, `_validate_method_call` стр. 518) | `odoo-connector`: `odoo_execute` — как второй рубеж после allowlist | список имён своими словами | MPL-2.0, да |
| 7 | Скрывать поля-секреты (`*_password`, `*_token`, `*_secret`, `pin`, `otp`…) из массового чтения, явный запрос — отдавать | `mcp_server_odoo/field_security.py@64b52df` | `odoo-connector`: `odoo_search_read` | только идея | MPL-2.0, да |
| 8 | «Custom Tools» модуля: вместо общего write — именованные глаголы (`confirm_sale_order`) на серверных действиях, со своей схемой, группами и флагом read-only | страница apps.odoo.com `mcp_server` 19.0 (описание, кода нет) | дорожная карта: на будущее для `odoo-connector`, если понадобятся частые бизнес-действия | только идея | OPL-1 — код не брать |
| 9 | Ключ со scope «только MCP» — утёкший ключ не открывает весь RPC (scope у ключей в 19.0: `odoo/addons/base/models/res_users.py:1527`, проверка `scope='rpc'` стр. 389) | страница модуля (описание) | инструкция установки `odoo-connector` | только идея | — |

**Чего здесь нет и брать у erpipe/dooservice:** подтверждение человеком
(elicitation), preview с diff «было → стало», dry-run с откатом, локальный
JSONL-аудит без модуля.

## Риски и заметки

- **Безопасность стандартного режима держится на закрытом модуле** (OPL-1,
  нельзя распространять). Клиентская проверка с кешем 5 минут — лишь
  дубль; без модуля остаётся YOLO, где `true` = права администратора.
- Нет защиты от «агент сам решил удалить»: подтверждения нет вообще.
- Одна база на процесс — хуже нашего `odoo-mcp` (`connection_id`).
- Устанавливается через `uvx`/pip с PyPI (Trusted Publishing из GitHub
  Actions) или Docker (`python:3.12-slim`, пользователь без root).
- HTTP-транспорт на `0.0.0.0` без `ODOO_MCP_ALLOWED_HOSTS` — без проверки
  Host/Origin (автор предупреждает).
