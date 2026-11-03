# odoo-migrate-to-20 — рабочий журнал

Дата: 2026-11-03. Сессия анализа, ветка `analysis/odoo-migrate-to-20`.

## Что смотрели

- Клон `tanim913/odoo-migrate-to-20` в scratchpad, HEAD `a5507bf82fb65d80bfeb8ace4607f3fbf630c580`
  (2026-10-15, v1.9.0). 12 коммитов с 2026-09-23 по 2026-10-15, один автор
  (`tanim913`). GitHub: ★13, 9 форков, 0 открытых issue.
- Прочитаны целиком: `SKILL.md` (356 строк), `README.md`, `install.sh`, `LICENSE`,
  `scripts/install_test.sh`, `references/python-orm.md`, `field-model-renames.md`,
  `manifest-and-modules.md`, `views-xml-data.md`, `controllers-http.md`,
  `upgrade-code-tool.md`, начало `security-ir-access.md`, `lessons-learned.md`,
  `smoke_test.py`; `scan.py` — структура правил, вызовы `subprocess`, список правил.
  Остальные references (JS/Owl 3, website, SCSS, тесты) — по оглавлению.
- Ничего из чужого репозитория не запускалось (ни `install.sh`, ни `doctor.sh`,
  ни `scan.py`). Список правил `scan.py` посчитан grep'ом по тексту.
- Исходники Odoo для сверки: `odoo/odoo`, ветки `18.0@f0ef96d`, `19.0@e0b25b7`,
  `20.0@b9823b8` (sparse-клоны в scratchpad, только чтение).

## Лицензия и происхождение

- `LICENSE`: MIT, «Copyright (c) 2026 tanim913». Совпадает с найденной поиском.
- Происхождение: тексты и скрипты написал автор. Внутри нет копий кода Odoo
  (LGPL-3). Есть только ссылки на `odoo/upgrade_code/*` и на `$ODOO20_SERVER/skills/`,
  которые запускаются или читаются на машине пользователя. Отдельных файлов
  под другими лицензиями нет. `assets/` — свои SVG-баннеры.
- Вывод: можно брать текст с атрибуцией (сохранить copyright и текст MIT).

## Права, сеть, телеметрия, что ставится

- Сеть: сами скрипты в сеть не ходят, телеметрии нет. Сеть упоминается только
  в подсказках (`git clone … odoo`, `pip install websocket-client`, `npx skills add`).
- `install.sh` пишет в `~/.agents/skills/`, `~/.claude/skills/`, `~/.codex/skills/`,
  `~/.copilot/skills/`, `~/.cursor/{rules,commands}`, `~/.gemini/commands`, а с
  `--project` — ещё в `.cursor/`, `.antigravity/`, `.agent/workflows/`,
  `.github/prompts/` и секцию в `AGENTS.md` проекта. Есть `--dry-run` и `--uninstall`.
  Хуков и MCP нет.
- В README есть раздел «For AI agents», где агенту велено самому склонировать и
  запустить `install.sh`, а затем `doctor.sh`. Это данные, а не команда для нас, и
  не выполнялось. Для разработчиков это лишний повод не ставить пакет «по просьбе агента».
- Исполнение кода: `install_test.sh` запускает `odoo-bin -i <module>`, то есть
  исполняет код мигрируемого модуля (так и задумано). `scan.py` запускает
  `$ODOO20_PYTHON -c`, чтобы импортировать сторонние библиотеки и модули `odoo.*`;
  код самого модуля он не импортирует. `xpath_check.py:30` делает `eval()` манифеста
  модуля с комментарием «local trusted file».
- **Риск:** `install_test.sh --db NAME` берёт любое имя базы и в конце делает
  `dropdb --if-exists` (если нет `--keep`). Защита «только `mig20_*`» есть в тексте
  `SKILL.md`, но не в коде. Если агент передаст имя рабочей базы, он её удалит.

## Как доказывается установка (`install_test.sh`, шаги 5–8 `SKILL.md`)

Итог `RESULT: CLEAN` ставится, только если выполнены все три условия:
1. `odoo-bin` завершился с кодом 0;
2. в логе нет ни одного шаблона ошибок: `ERROR|CRITICAL`, `Traceback`,
   `incompatible version`, `not installable`, `ParseError`, `ValidationError`,
   `Element … cannot be located`, ошибка сборки бандла, `N failed`. Отдельно
   ловится пропуск браузерных тестов («skipped … Chrome/websocket»);
3. в `ir_module_module` у каждого модуля `state = installed` (проверка через `psql`).

Сверх этого: `--tests` (с демо), смоук-модуль с clickbot по меню модуля и всем
страницам website (под public и admin), отдельный «flow tour» главного сценария,
повторный `-u` для проверки идемпотентности данных, `registry_check.py` (мёртвые
`super()` и несуществующие compute по реальному MRO), `xpath_check.py`,
`qweb_if_chain_check.py`. В конце: хэш-дерево исходника не изменилось,
`git status` ядра пуст, баз `mig20_*` не осталось. Главное правило: **никогда не
комментировать код, ассеты и xpath ради установки**. Что не перенесено, записывается
в «Not migrated» с причиной.

Ловушка, которую они явно учли: HttpCase **пропускается, а не падает**, если нет
Chrome или `websocket-client`, и «0 failed» может значить «ничего не запускалось»
(`lessons-learned.md`, раздел Tooling).

## Сверка таблицы изменений API с `odoo/odoo`

Выборка из 62 утверждений, в первую очередь 18→19 и 19→20, из `python-orm.md`,
`field-model-renames.md`, `manifest-and-modules.md`, `views-xml-data.md`,
`controllers-http.md`, `upgrade-code-tool.md`, `SKILL.md`.

**Итог: фактических ошибок 0 из 62, но в 13 строках неверна версия.** Названо
«Since 20», а изменилось уже в 19 или раньше. В одном случае наоборот: «18», а
на деле 19. Само утверждение «в 20 так нельзя» в этих строках верно, но для таблицы
по версиям, где важен столбец «с какой версии», это дефект: кто мигрирует 18→19,
не узнает, что ловушка касается и его.

### Версия указана неверно (13)

| # | Их утверждение (`файл:строка`@`a5507bf`) | Как на деле | Источник `odoo/odoo` |
|---|---|---|---|
| V1 | `python-orm.md:46` «20: `_login(cls, db, …)` → `_login(self, credential, …)`» | В 18 `@classmethod _login(cls, db, credential, …)`, в 19 уже `def _login(self, credential, user_agent_env)` → изменение 18→19 | `18.0:odoo/addons/base/models/res_users.py:925`; `19.0:…/res_users.py:760` |
| V2 | `python-orm.md:51` «20: `group_expand(self, values, domain, order)` → `(values, domain)`» | Уже в 18 зовётся `group_expand(self, groups, domain)` | `18.0:odoo/models.py:2381` |
| V3 | `python-orm.md:42` «20: `odoo.registry(db)` убран» | `def registry` есть в 18 `odoo/__init__.py:30`; в 19 файла `odoo/__init__.py` нет (`odoo/init.py`) → 18→19 | `18.0:odoo/__init__.py:30`; дерево `19.0:odoo/` |
| V4 | `python-orm.md:49` «20: `fields.datetime.now()` / `fields.date.today()`» | В 18 `odoo/fields.py:8` импортирует `date, datetime`; в 19 `odoo/fields/__init__.py` их не экспортирует → 18→19 | `18.0:odoo/fields.py:8`; `19.0:odoo/fields/__init__.py` |
| V5 | `python-orm.md:50` «20: `models.NewId` → `from odoo.api import NewId`» | В 18 `odoo/models.py:56` импортирует `NewId`; `19.0:odoo/models/__init__.py` его не экспортирует → 18→19 | `18.0:odoo/models.py:56` |
| V6 | `python-orm.md:54` «20: `readonly=1` предупреждение "should be a boolean"» | Предупреждение есть уже в 18 | `18.0:odoo/fields.py:540` |
| V7 | `python-orm.md:55` «20: `mail.mail.send(…)` + `post_send_callback`» | Параметр есть уже в 18 | `18.0:addons/mail/models/mail_mail.py:619` |
| V8 | `python-orm.md:150` «20: `default_get(self, fields_list)` → `fields`» | В 18 `fields_list`, в 19 `fields` → 18→19 | `18.0:odoo/models.py:1639`; `19.0:odoo/orm/models.py:1271` |
| V9 | `field-model-renames.md:45` «20: `signup_url` удалён» | В `auth_signup` 18 поля `signup_url` уже нет, есть `_get_signup_url()` | `18.0:addons/auth_signup/models/res_partner.py:29` |
| V10 | `field-model-renames.md:46` «20: `base.default_user` → `base.default_user_group`» | В 18 `base.default_user` (`res_users.py:367`), в 19 уже `default_user_group` → 18→19 | `19.0:odoo/addons/base/models/res_users.py:209` |
| V11 | `field-model-renames.md:50` «20: `digits='Product Unit of Measure'` → `'Product Unit'`» | В 19 ядро уже везде пишет `'Product Unit'` (48 мест), запись точности `Product Unit` в `uom_data.xml:6`. Старое имя молча даёт 2 знака (`precision_get` → `2`, если записи нет) → 18→19, SILENT | `19.0:addons/uom/data/uom_data.xml:6`; `19.0:odoo/addons/base/models/decimal_precision.py:23–27` |
| V12 | `field-model-renames.md:23` «18: `res.partner.title` удалён» | В 18 поле есть (`res_partner.py:227`, модель `res.partner.title` строка 185), удалено в 19. Внутреннее противоречие: строка 59 того же файла правильно говорит «19» | `18.0:odoo/addons/base/models/res_partner.py:185,227` |
| V13 | `views-xml-data.md:50` «20 RNG запрещает атрибуты у `<group>` в `<search>`» | `expand`/`string` убраны из `define name="group"` в `common.rng` при переходе 18→19; в 19 и 20 определение одинаковое | diff `18.0`↔`19.0:odoo/addons/base/rng/common.rng` (атрибуты `expand`, `string`); `19.0` = `20.0` |

### Подтверждено (49)

Python/ORM:
- `@api.returns` убран в 19 — `def returns` есть в `18.0:odoo/api.py:359`, в 19/20 нет.
- `_sql_constraints` игнорируется с предупреждением с 19 — `19.0:odoo/orm/model_classes.py:162–163`, `20.0:…:175–176`; `upgrade_code` `18.1-00-sql-constraint`.
- `group_operator`: в 18–19 устаревший алиас (`19.0:odoo/orm/fields.py:485–487`), в 20 удалён.
- `check_access_rights/_rule`, `_filter_access_rules`: в 19 ещё есть (`19.0:odoo/orm/models.py:4168`), в 20 нет; замены есть с 18 (`18.0:odoo/models.py:4442–4466`).
- `self._cr/_uid/_context` устарели с 19 — `20.0:odoo/orm/models.py:5399–5410` (`@deprecated("Deprecated since 19.0…")`).
- `odoo.osv` удалён в 20 — дерево `20.0:odoo/` без `osv/`; в 19 есть.
- `read_group`: устарел в 19 (`19.0:odoo/orm/models.py:2754`), в 20 `@typing.final` с новой сигнатурой (`20.0:…:1930–1940`); `formatted_read_group` — `20.0:addons/web/models/models.py:1022`.
- `ormcache_context` удалён в 20 (в `19.0:odoo/tools/cache.py:179` есть); `ormcache` из `odoo.api` (`20.0:odoo/api/__init__.py:5`), старый путь с предупреждением (`20.0:odoo/tools/__init__.py:24–25`).
- `registry.clear_cache` → `env.transaction.invalidate_ormcache` — `20.0:odoo/orm/environments.py:833`; `19.0:odoo/orm/registry.py:999`.
- `toggle_active`, `_check_recursion` удалены в 20 (`19.0:odoo/orm/models.py:5809,5707`); `action_archive`, `_has_cycle` — `20.0:…:5282,5125`.
- `lazy_property`, `pycompat`, `odoo/tools/query.py` удалены в 20; `Query` — `20.0:odoo/models/__init__.py:26`.
- `mod10r`, `street_split` → `odoo.tools.business_data` — `20.0:odoo/tools/business_data.py:88,101` (в 19 `misc.py:477,1955`).
- `env.clear()` устарел в 20 — `20.0:odoo/orm/environments.py:379`.
- `PG_CONCURRENCY_*` → `odoo.sql_db` — `20.0:odoo/sql_db.py:87`; в 19 `odoo/service/model.py:28–29`.
- `ir.config_parameter.get_param/set_param` удалены в 20, есть `get_str/get_bool/get_int/set_str` — `20.0:odoo/addons/base/models/ir_config_parameter.py:78–124`; в 19 `get_param` `:60`.
- `pytz` убран из `requirements.txt` 20 (в `19.0:requirements.txt:80` есть).
- `BinaryBytes`/`BinaryValue`, `bytes` отвергается — `20.0:odoo/tools/binary.py:9,74`, `20.0:odoo/orm/fields_binary.py:112`.

Поля и модели:
- 19: `groups_id` → `group_ids` (`19.0:…/res_users.py:257`); `res.groups.users` → `user_ids`, `category_id` → `privilege_id` (`19.0:…/res_groups.py:17,36`); `res.partner.mobile` удалён (`18.0:…/res_partner.py:285`, в 19 нет); `res.partner.title` удалён (строка 59 их файла); `uom.uom` `category_id/factor_inv` → `relative_factor/relative_uom_id` (`19.0:addons/uom/models/uom_uom.py:36,41`); `sale.order.line` `tax_id/product_uom` → `tax_ids/product_uom_id` (`19.0:addons/sale/models/sale_order_line.py:132,162`); `purchase.order.line` `taxes_id/product_uom` → `tax_ids/product_uom_id` (`19.0:addons/purchase/models/purchase_order_line.py:34,43`).
- 20: `stock.move.product_uom`, `stock.move.line.product_uom_id` → `uom_id` (`20.0:addons/stock/models/stock_move.py:68`, `stock_move_line.py:34`); `purchase.order.line.uom_id` (`…:49`); `res.partner.company_type` удалён (`19.0:…/res_partner.py:282`); `res.country.zip_required` → `zip_applicability` (`20.0:…/res_country.py:101`); `uom.uom.rounding` удалён (в 19 compute `:39`); `account.move.checked` → `review_state` (`20.0:addons/account/models/account_move.py:320`); `sale.order.require_payment` удалён (`19.0:addons/sale/models/sale_order.py:117`).

Безопасность, HTTP, окружение:
- 20: нет `ir.model.access` и `ir.rule`, одна модель `ir.access` с полями `model_id/group_id/operation/domain` — `20.0:odoo/addons/base/models/ir_access.py:64–110`; `ir_rule.py` в 20 отсутствует; скрипт `upgrade_code` `19.4-00-ir-access.py`.
- `type='json'` — устаревший алиас с 19 — `20.0:odoo/http/routing_map.py:189–191`.
- `auth='none'` → `readonly` по умолчанию — `20.0:odoo/http/routing_map.py:355`.
- `odoo.http` в 20 — пакет (`odoo/http/{requestlib,router,session,stream,…}.py`).
- `get_current_website()` удалён в 20 (`19.0:addons/website/models/website.py:1377`), используется `self.env.website` (`20.0:addons/website/models/ir_http.py:275`).
- Odoo 20: Python 3.12–3.14, PostgreSQL ≥ 16 — `20.0:odoo/release.py:39–41`, `version_info = (20, 0, 0, FINAL…)` `:15`. (В 19: 3.10–3.14, PG ≥ 13.)
- Owl 3 в 20 — `20.0:addons/web/static/lib/owl/owl.js:1808` `version = "3.0.0-alpha.50"` (в 19 `2.8.4`). В ядре 20 стоит альфа-версия Owl 3.
- Список скриптов `upgrade_code` совпадает с деревом `20.0:odoo/upgrade_code/`; в 19.0 скрипты кончаются на `18.5-*`.
- `odoo/odoo@20.0:skills/` — `odoo-guidelines`, `odoo-web-guidelines`, `odoo-security`, `odoo-review` (+ `odoo-git`, которого `SKILL.md` не называет).
- Модули: в 20 удалены `website_sale_wishlist`, `website_sale_comparison`, `website_sale_stock_wishlist`, `website_sale_autocomplete`, `website_sale_mondialrelay`, `base_vat`, `base_iban`, `stock_picking_batch`, `hr_org_chart`, `hr_hourly_cost`, `hr_work_entry_holidays`; в 19 удалены `web_editor` (есть `html_editor` + `html_builder`), `hr_contract`, `membership`, `website_jitsi` (проверено по `__manifest__.py` в деревьях 18/19/20).
- Проверка `@api.private` (с 18: `18.0:odoo/api.py:448`), `try_lock_for_update` (19: `19.0:odoo/orm/models.py:5611`), `tools.hmac`/`consteq` (`19.0:odoo/tools/misc.py:1786,1673`) — для пунктов ревью.

### Не проверено

- `res.partner.team_id`, `mobile_blacklisted`, `property_payment_method_id`, `sla_ids`
  «удалены в 20»: в `res_partner.py` модулей `sale/crm/sales_team/account*/mail*` 18–20
  этих определений нет, поля могут жить в миксинах (`mail.thread.phone`) или в
  enterprise. Отсутствие поиском не доказано (№28), в счёт не идёт.
- Строки 14–17, платёжный движок, Owl 3/JS, website, SCSS, иконки: не сверял (это
  вне фокуса 18→19 / 19→20, а для JS нужен полный `addons/web`).
- Работу `scan.py` и `install_test.sh` вживую не проверял: в облаке нет Odoo 20,
  PostgreSQL 16 и Chrome, а запускать чужие скрипты без разрешения нельзя.

## Сравнение с нашим

- **`boost:source-check`**: принцип тот же («не писать API по памяти, а подтверждать
  в исходниках»). У них это grep по локальному `$ODOO20_SERVER`, у нас цитата с URL.
  У нас нет требования к столбцу «с какой версии» — их 13 ошибок показывают, что
  такая проверка нужна.
- **`boost:odoo-model-map`**: не пересекается. Их `override-signature` и
  `registry_check.py` (реальный MRO) — близкая идея к режиму «трасса» (T4), но
  требует живой базы.
- **`odoo19-mvp-build:code-dev` (`references/odoo-version-notes.md`, F2)**: приватный
  маркетплейс недоступен (`add_repo` отклонён классификатором), сравниваю по описанию F2
  в `roadmap.md` и карточкам dooservice/unclecatvn. Новое наблюдение: «Python 3.12+ /
  PG 16+», которые F2 приписывает 19.0, — это ровно требования **20.0**
  (`20.0:odoo/release.py:39–41`). Вероятно, в наш раздел 19 попали факты 20. Это ещё
  один довод вести таблицу с `файл:строка` по каждой ветке.
- **`odoo19-implementation`** (миграция): по описи — миграция данных и go-live, а не
  перенос кода модуля между версиями. Сравнить по тексту не удалось (приватный репо).
- **`dooservice-odoo-skills`** (`odoo-upgrade`, LGPL): у dooservice при сверке ~20
  фактов 19.0 расхождений 0. Здесь фактов 0 ошибок из 62, но 13 ошибок в версии.
  Сильнее dooservice в части «доказательства» (скрипты установки и смоука), слабее в
  охвате (только 20 как цель).
- **`odoo-lens`** (без лицензии): ~15 правил 17–19 и правила связности. Здесь 123
  regex-правила + проверки импорта, xml-id и сигнатур, лицензия MIT, но правила
  нацелены на 20.
- **`mart337i-odoo-skills`**: справочник 20 там почти копия 19, 9 ошибок из 19 фактов.
  Здесь картина обратная: факты 20 верны и подтверждены исходниками.

## Решения и открытые вопросы

- `add_repo` на `todoltd/claude-methodology-marketplace` отклонён правами классификатора.
  Из приватного репо ничего не читалось и не копировалось.
- A/B не делали: нужна установленная Odoo 20 + PG 16 + Chrome и разрешение на
  запуск чужих скриптов. Без A/B вердикт «взять» по `criteria.md` невозможен.
- Открыто: ставить ли скилл разработчикам локально для миграций на 20 (после
  правки защиты `--db` и пина коммита) — решение пользователя, когда начнутся проекты на 20.
