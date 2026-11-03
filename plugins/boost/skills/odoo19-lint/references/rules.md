# Правила odoo19-lint (для проверки без скрипта)

Каждое правило сверено с исходниками `odoo/odoo` ветки `19.0`, коммит
`e0b25b7` (2026-11-03). Источник — `репозиторий@ветка:путь:строки`.
Тот же список печатает `python3 -I scripts/odoo19_lint.py --rules`.

**ERROR** — модуль не установится, упадёт, или поведение молча пропадёт.
**WARN** — устарело в 19.0 (DeprecationWarning), работает.

Как проверять без Bash: Read каждого изменённого файла и сверка по
разделам ниже; или Grep по рецепту правила (`-n`, тип файла указан).
Попадание в комментарии или docstring не считается.

## Вью и действия (XML, иногда Python)

### `view-tree` — ERROR
`<tree>` или xpath на `tree` (`//tree`, `field[@name='x']/tree`).
Тип вью в 19.0 — `list`; `<tree>` даёт «Invalid view type».
Нужно: `<list>`, `//list`.
Источник: `odoo/odoo@19.0:odoo/addons/base/models/ir_ui_view.py:149-156`
(selection `type` без `tree`), `:610-617` (Invalid view type).
Grep (`*.xml`): `<tree[\s>/]|expr="[^"]*\btree\b`

### `view-mode-tree` — ERROR
`view_mode` с `tree` в `ir.actions.act_window` (XML или dict в Python),
`(False, 'tree')` в `views`. Вида `tree` нет: «No default view of type
'tree'».
Нужно: `list,form`; `(False, 'list')`.
Источник: `odoo/odoo@19.0:odoo/addons/base/models/ir_actions.py:318`
(default `list,form`), `:401-408` (`VIEW_TYPES`);
`odoo/addons/base/models/ir_ui_view.py:3054-3058`.
Grep: `view_mode[^\n]*\btree\b|['"]tree['"]\s*\)`

### `tree-view-ref` — WARN
Ключ контекста `tree_view_ref` не читается: ищется
`<тип>_view_ref`, тип — `list`. Нужное вью молча не применится.
Нужно: `list_view_ref`.
Источник: `odoo/odoo@19.0:odoo/addons/base/models/ir_ui_view.py:3024-3026`.

### `view-attrs-states` — ERROR
Атрибуты `attrs="…"`, `states="…"` во вью, `<attribute name="attrs">`
в xpath. С 17.0 вью с ними не проходит проверку.
Нужно: `invisible="state != 'draft'"`, `readonly="…"`, `required="…"`,
`column_invisible="…"` (выражения Python над полями).
Источник: `odoo/odoo@19.0:odoo/addons/base/models/ir_ui_view.py:495-499`.
Grep (`*.xml`): `\s(attrs|states)=|name="(attrs|states)"`

## Модели (Python)

### `sql-constraints` — ERROR
`_sql_constraints = [...]` в 19.0 игнорируется целиком (только warning
в логе) — ограничения в БД нет, дубли пройдут.
Нужно: атрибут класса
`_plate_uniq = models.Constraint('UNIQUE(plate)', 'Номер должен быть уникален')`;
индексы — `models.Index(...)`, `models.UniqueIndex(...)`.
Источник: `odoo/odoo@19.0:odoo/orm/model_classes.py:159-164`.

### `inherit-list-no-name` — ERROR / `inherit-list-implicit-name` — WARN
`_inherit = ['x', ...]` **списком** без `_name`: в 19.0 строка-`_inherit`
даёт `_name = _inherit`, а список — нет; `_name` выводится из имени класса
(`TdVehicleKpi` → `td.vehicle.kpi`). Если имя не совпало с `x` — это
НОВАЯ модель (ERROR); совпало — работает, но с warning (WARN).
Нужно: расширение — `_inherit = 'x'` строкой; с миксинами — явно
`_name = 'x'` и `_inherit = ['x', 'mail.thread']`.
Источник: `odoo/odoo@19.0:odoo/orm/models.py:241-249`.

### `name-get` — ERROR
`name_get` в 19.0 нет: переопределение не вызывается, вызов
`rec.name_get()` — AttributeError.
Нужно: `@api.depends(...)` + `_compute_display_name`, читать `display_name`.
Источник: `odoo/odoo@19.0:odoo/orm/models.py:1438`; `name_get` в `odoo/`
19.0 не определён (grep — 0).

### `api-returns` — ERROR
`@api.returns(...)`: декоратора нет, AttributeError при импорте.
Источник: `odoo/odoo@19.0:odoo/api/__init__.py:5-17` (список экспорта).

### `user-has-groups` — ERROR
`self.user_has_groups('…')`: метода нет.
Нужно: `self.env.user.has_group('mod.group')` или `has_groups('a,!b')`.
Источник: `odoo/odoo@19.0:odoo/addons/base/models/res_users.py:1034,1066`.

### `read-group` — WARN
`read_group(...)` устарел. Нужно: `_read_group(domain, groupby, aggregates)`
(возвращает кортежи) или `formatted_read_group` для UI.
Источник: `odoo/odoo@19.0:odoo/orm/models.py:2754-2755`.

### `private-env` — WARN
`self._context`, `self._cr`, `self._uid`. Нужно: `self.env.context`,
`self.env.cr`, `self.env.uid`.
Источник: `odoo/odoo@19.0:odoo/orm/models.py:5930-5943`.

### `toggle-active` — WARN
`toggle_active()`. Нужно: `action_archive()` / `action_unarchive()`.
Источник: `odoo/odoo@19.0:odoo/orm/models.py:5807-5813`.

### `notify-progress` — WARN
`ir.cron._notify_progress(...)`. Нужно:
`self.env['ir.cron']._commit_progress(processed=n, remaining=m)` — он же
коммитит, чтобы крон после таймаута продолжил с того же места.
Источник: `odoo/odoo@19.0:odoo/addons/base/models/ir_cron.py:823-824, 846`.

### `group-operator` — WARN
`fields.X(group_operator='sum')`. Нужно: `aggregator='sum'`.
Источник: `odoo/odoo@19.0:odoo/orm/fields.py:485-487`.

## Поля, которых нет у модели в 19.0

Где искать: `related='…'`, `@api.depends('…')`, обращения `rec.x.y`,
ключи `create`/`write`, `<field name="…">` в записях XML и вью этой
модели, заголовки CSV `<модель>.csv`.

### `partner-mobile-title` — ERROR
`res.partner.mobile`, `res.partner.title` удалены (ни один аддон
community 19.0 их не возвращает). `related='partner_id.mobile'`,
`partner_id.title.name`, `<field name="mobile"/>` во вью партнёра —
модуль не установится.
Нужно: `phone`; обращения нет — без него или своё поле (если модуль сам
добавляет `mobile`/`title` в `res.partner`, это не ошибка).
Источник: `odoo/odoo@19.0:odoo/addons/base/models/res_partner.py:184-313`
(поля `ResPartner`; `phone` — `:276`).
Grep (`*.py`, `*.xml`): `partner\w*\.(mobile|title)\b(?!\s*\()|name="(mobile|title)"`

### `groups-fields` — ERROR
- `res.groups`: `users` → `user_ids`; `category_id` → `privilege_id`
  (запись `res.groups.privilege` с `name` и `category_id`).
- `res.users`, `ir.ui.menu`, `ir.ui.view`, `ir.actions.act_window`,
  `ir.actions.server`, `ir.actions.report`: `groups_id` → `group_ids`.
  Атрибут `groups="…"` у `<menuitem>`/элементов вью не трогать — он верный.

Источник: `odoo/odoo@19.0:odoo/addons/base/models/res_groups.py:17,36`;
`res_groups_privilege.py:13`; `res_users.py:257`; `ir_ui_menu.py:29`;
`ir_actions.py:329,661`; `ir_actions_report.py:183`; `ir_ui_view.py:175`
(все в `odoo/addons/base/models/`).
Grep: `groups_id|name="(users|category_id)"|\.users\b`

### `cron-numbercall` — ERROR
`ir.cron`: `numbercall`, `doall` удалены. Крон бессрочный, пока `active`.
Источник: `odoo/odoo@19.0:odoo/addons/base/models/ir_cron.py:99-122`.

### `uom-fields` — ERROR
`uom.uom`: нет `category_id`, `uom_type`, `factor_inv` (категорий
единиц нет). Нужно: `relative_factor` + `relative_uom_id`
(«упаковка 6 шт» = 6 × `uom.product_uom_unit`).
Источник: `odoo/odoo@19.0:addons/uom/models/uom_uom.py:34-44`.

### `product-type` — ERROR
`detailed_type` нет; `type='product'` нет (выбор `consu`/`service`/`combo`).
Складской товар: `type='consu'` + `is_storable=True` (поле модуля `stock`).
Источник: `odoo/odoo@19.0:addons/product/models/product_template.py:58-65`;
`addons/stock/models/product.py:834`.

### `line-product-uom` — ERROR
`sale.order.line`, `purchase.order.line`: `product_uom` → `product_uom_id`.
У `stock.move` поле по-прежнему `product_uom` — не путать.
Источник: `odoo/odoo@19.0:addons/sale/models/sale_order_line.py:132`;
`addons/purchase/models/purchase_order_line.py:43`;
`addons/stock/models/stock_move.py:67`.

## Манифест и контроллеры

### `manifest-hook-path` — ERROR
`'pre_init_hook': 'my_module.hooks.pre_init'`: загрузчик делает
`getattr(модуль_аддона, значение)` — нужно просто имя функции, импортированной
в `__init__.py` аддона.
Источник: `odoo/odoo@19.0:odoo/modules/loading.py:182-185`.

### `route-type-json` — WARN
`@http.route(..., type='json')` — устаревший алиас. Нужно: `type='jsonrpc'`.
Источник: `odoo/odoo@19.0:odoo/http.py:812-818`.

## Второй круг (сверено с 19.0 `e0b25b7` и 18.0 `f0ef96d`)

Источник — `odoo/odoo@19.0:` если не указано иное; «в 18.0» — где было
раньше (`odoo/odoo@18.0:`).

### `api-model-create` — ERROR
`@api.model` + `def create(self, vals)`: в 19.0 декоратор молча делает из
такого `create` `model_create_multi`, и метод получает **список** словарей
(`vals.get(...)` → AttributeError, `vals['x'] = …` → TypeError).
Нужно: `@api.model_create_multi` + `def create(self, vals_list)` и цикл.
Источник: `odoo/orm/decorators.py:322-323`, `:364-369`.

### `old-constraints` — ERROR
`_constraints = [...]` игнорируется (warning), проверки нет.
Нужно: `@api.constrains('поле')` + `ValidationError`.
Источник: `odoo/orm/model_classes.py:159-161`.

### `fields-date-alias` — ERROR
`fields.date.today()`, `fields.datetime.now()`: в 18.0 `odoo/fields.py`
импортировал модуль `datetime` (`18.0:odoo/fields.py:8`), в 19.0 `fields` —
пакет без этих имён → AttributeError.
Нужно: `fields.Date.today()`, `fields.Datetime.now()` или `from datetime import date`.
Источник: `odoo/fields/__init__.py:5-22`.

### `models-newid` — ERROR
`models.NewId`, `from odoo.models import NewId`: не экспортируется в 19.0.
Нужно: `from odoo.api import NewId`.
Источник: `odoo/models/__init__.py:7-30`, `odoo/api/__init__.py:4`; в 18.0 `odoo/models.py:56`.

### `odoo-registry` — ERROR
`odoo.registry(db)`: в 18.0 был deprecated (`18.0:odoo/__init__.py:30-41`),
в 19.0 его нет.
Нужно: `from odoo.modules.registry import Registry; Registry(db)` или `self.env.registry`.
Источник: `odoo/init.py:33-43` (ярлыки пространства `odoo`).

### `savepoint-case` — ERROR
`SavepointCase` нет (ни в 18.0, ни в 19.0): ImportError, тесты не грузятся.
Нужно: `TransactionCase`.
Источник: `odoo/tests/common.py:990,1186`.

### `search-group-attrs` — ERROR
`<group expand="0" string="Group By">` внутри `<search>`: в 19.0 RNG
убрал у `group` атрибуты `expand` и `string` (в 18.0 были), вью не
проходит проверку. В `<form>` `<group string=…>` по-прежнему верен.
Нужно: `<group>` без атрибутов.
Источник: `odoo/addons/base/rng/common.rng:295-313`;
`odoo/addons/base/models/ir_ui_view.py:509-515`.
Grep (`*.xml`, внутри `<search>`): `<group[^>]*\b(expand|string)=`

### `digits-uom` — ERROR (молча)
`digits='Product Unit of Measure'`: точность в 19.0 называется
`Product Unit`; по несуществующему имени `precision_get` возвращает 2,
настройка точности молча не применяется.
Нужно: `digits='Product Unit'`.
Источник: `addons/uom/data/uom_data.xml:5-8`;
`odoo/addons/base/models/decimal_precision.py:23-27`; в 18.0
`addons/product/data/product_data.xml:36`.

### `default-user` — ERROR
xml-id `base.default_user` (шаблон пользователя) в 19.0 нет: `ref`/`env.ref` падает.
Нужно: группа `base.default_user_group`.
Источник: `odoo/addons/base/security/base_groups.xml:114`,
`odoo/addons/base/models/res_users.py:209`; в 18.0 `odoo/addons/base/data/res_users_data.xml:31`.

### `login-classmethod` — ERROR
Переопределение `res.users._login` как `@classmethod def _login(cls, db, credential, user_agent_env)`:
в 19.0 это метод записи `def _login(self, credential, user_agent_env)` — вход падает TypeError.
Источник: `odoo/addons/base/models/res_users.py:760`; в 18.0 `:924-925`.

### `default-get-kwarg` — ERROR
`default_get(fields_list=...)` по имени: параметр в 19.0 — `fields`.
Позиционный вызов и переопределение `def default_get(self, fields_list)` работают.
Источник: `odoo/orm/models.py:1271`; в 18.0 `odoo/models.py:1639`.

### `line-tax-ids` — ERROR
`sale.order.line.tax_id` и `purchase.order.line.taxes_id` → `tax_ids`
(у `product.template` `taxes_id` остался).
Источник: `addons/sale/models/sale_order_line.py:162`,
`addons/purchase/models/purchase_order_line.py:34`; в 18.0 `:159` и `:33`.

### `removed-module` — ERROR
`depends` на аддон, которого нет в community 19.0: модуль пропускается.
46 каталогов `addons/` 18.0 (`f0ef96d`) отсутствуют в 19.0 (`e0b25b7`),
среди них `web_editor` (→ `html_editor`), `hr_contract` (→ `hr`),
`membership`, `website_jitsi`, `website_event_meet`, `product_images`, `hw_*`.
Список целиком — `REMOVED_MODULES` в скрипте. Enterprise не проверялся.
Источник: `odoo/modules/module_graph.py:257-269`.

### `oe-chatter` — ERROR (молча)
`<div class="oe_chatter">` на форме: в 19.0 компилируется только
`<chatter/>`, старый блок молча не показывает чаттер.
Источник: `addons/mail/static/src/chatter/web/form_compiler.js:46-48`
(`oe_chatter` в `mail`/`web` 19.0 не встречается).

### `osv-expression` — WARN
`from odoo.osv import expression`: модуль устарел.
Нужно: `from odoo.fields import Domain`.
Источник: `odoo/osv/__init__.py:4`.

### `js-use-service` — ERROR
`useService("rpc")`, `useService("user")`: сервисов нет, компонент падает
«Service rpc is not available».
Нужно: `import { rpc } from "@web/core/network/rpc"`, `import { user } from "@web/core/user"`.
Источник: `addons/web/static/src/core/utils/hooks.js:142-147`,
`network/rpc.js:93`, `user.js:254`.

### `manifest-version` — ERROR (молча)
`'version'` из 4–5 частей не с `19.0.` (например `18.0.1.0.0`): загрузчик
ставит `installable=False` с warning, модуль не виден.
Нужно: `19.0.x.y.z` (или короткая `x.y.z`, префикс добавится).
Источник: `odoo/modules/module.py:465-467`, `:550-566`.

## Официальные кодмоды 19.0 (автозамена)

`odoo-bin upgrade_code --script <имя> [--dry-run]` (`odoo/cli/upgrade_code.py:168-174`)
запускает один скрипт из `odoo/upgrade_code/`. Скрипт печатает их в строке
«автозамена»; запускать — только с согласия пользователя (переписывает файлы).

| Правило | Кодмод (`odoo/upgrade_code/…`) |
|---|---|
| `view-tree`, `view-mode-tree` | `17.5-01-tree-to-list.py` |
| `sql-constraints` | `18.1-00-sql-constraint.py` |
| `route-type-json` | `18.1-02-route-jsonrpc.py` |
| `private-env` | `18.5-00-deprecated-properties.py` |

## Справочники не проверяются

Скрипт читает только `.py`/`.xml`/`.csv` (и `.js` в `static/`) внутри
каталога модуля с `__manifest__.py`. Этот файл, `SKILL.md`, заметки вроде
`odoo-version-notes.md` и любые `*.md` не читаются вовсе; Python-скрипты
вне модулей пропускаются (`--all-files` — проверить всё). При ручной
проверке тоже не считай находкой перечисление запрещённого в справочнике.

## Чего правила не видят

Поля из аддонов вне проверяемых путей и enterprise, JS/OWL, код,
собранный строками, данные в БД. Отсутствие находок не доказывает, что
модуль установится.
