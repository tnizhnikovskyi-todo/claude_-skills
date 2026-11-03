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

## Чего правила не видят

Поля из аддонов вне проверяемых путей и enterprise, JS/OWL, код,
собранный строками, данные в БД. Отсутствие находок не доказывает, что
модуль установится.
