# Вопросы A/B и эталонные ответы

Эталон собран вручную: `odoo_map.py` + grep + чтение кода (в прогоны не
попадает: прогоны идут на копиях в scratchpad). Оценка 0 / 0.5 / 1 по
пунктам эталона, «ловушка» = штраф, если ответ её не различает.

Цели:
- **pilot** — копия `pilot/` (3 модуля, ~600 строк), отдельный `git init`.
- **pilot-diff** — та же копия с незакоммиченным диффом `diff-p4.patch`.
- **odoo19** — sparse-клон `odoo/odoo@19.0`: `addons/{sale,stock,account,product}`,
  `odoo/addons/base` (536 `.py`, 386 `.xml`, 229 МБ без `.git`).

## P1. Кто расширяет `td.workshop.order` (pilot)

> Какие модели и вью расширяют или наследуют модель `td.workshop.order`
> и кто на неё ссылается? Ответь списком с файлами.

Эталон:
1. Определена `td_workshop/models/workshop_order.py:5` (миксин `mail.thread`).
2. Расширяет `td_workshop_sale/models/workshop_order.py:5` (`_inherit` строкой, добавляет `sale_order_id`, `action_create_quotation`).
3. Вью `td_workshop_sale.view_workshop_order_form_sale` наследует `td_workshop.view_workshop_order_form` (`inherit_id`).
4. Ссылаются Many2one: `td.workshop.close.wizard.order_id`, `td.workshop.order.line.order_id`, `sale.order.workshop_order_id`.
5. `env['td.workshop.order']`: `res_partner.py:11`, портал `controllers/main.py:9` (+ тесты).

## P2. Что затронет переименование поля `discount` (pilot)

> Что сломается или изменит поведение, если переименовать поле `discount`
> модели `td.workshop.order`? Перечисли все места.

Эталон:
1. Определение `workshop_order.py:34`.
2. `_compute_amount_total` (`:48`) читает `order.discount`; в `@api.depends` его нет (K4) — стоит упомянуть.
3. Вью формы `workshop_order_views.xml:66` (`<field name="discount"/>`): переименование без правки вью роняет установку.
4. `td_workshop_sale/models/workshop_order.py:24`: `self.discount` в `action_create_quotation`.
5. Ловушка: ключ `"discount"` в словаре строки `sale.order.line` (там же, :24) — это поле ядра, переименовывать его нельзя.
6. Хранимое `amount_total` → миграция данных (колонка).

## P3. Кто вызывает `_format_phone` и `_legacy_recompute` (pilot)

> Кто вызывает методы `_format_phone` и `_legacy_recompute`? Есть ли
> мёртвый код?

Эталон:
1. `td.workshop.order._format_phone` (`workshop_order.py:66`) вызывают `create` (`:59`) и `_onchange_partner_id` (`:64`).
2. Отдельный `sale.order._format_phone` (`td_workshop_sale/models/sale_order.py:14`) вызывает `_prepare_workshop_note` (`:11`), который вызывается из `td.workshop.order.action_create_quotation` через `env["sale.order"]` (ловушка: не смешать две функции; дубль K6).
3. `_legacy_recompute` (`workshop_order.py:96`) не вызывается нигде (K5, мёртвый код, пишет в computed-поле).

## P4. Влияние диффа (pilot-diff)

> В рабочей копии есть незакоммиченные изменения (`git diff`). Что они
> затрагивают: какие методы, поля, вью, шаблоны, тесты и модули могут
> изменить поведение? Есть ли риск ошибки?

Дифф (`diff-p4.patch`): `_format_phone` возвращает номер с пробелами,
`_compute_subtotal` умножает на `(1 - order_id.discount / 100)`.

Эталон:
1. `_format_phone` → `create`, `_onchange_partner_id` → `customer_phone` → форма (`workshop_order_views.xml:41`) и портал (`workshop_status_templates.xml:9`).
2. Тест `test_phone_copied` (`tests/test_workshop_order.py:21`) упадёт.
3. Ловушка: `sale.order._format_phone` — отдельная копия, дифф её не трогает.
4. `subtotal` (хранимое) → `amount_total` (`@api.depends("line_ids.subtotal")`) → список (сумма), форма, портал (`:10`).
5. Ошибка: скидка применяется дважды (в `subtotal` и снова в `amount_total`).
6. В `@api.depends` у `_compute_subtotal` нет `order_id.discount`: при смене скидки subtotal не пересчитается.

## O1. Кто расширяет `product.template` (odoo19)

> В этом клоне Odoo 19 (аддоны sale, stock, account, product, base): какие
> модели расширяют или делегируют `product.template`? Укажи модуль, файл,
> способ (`_inherit`, `_inherits`).

Эталон (`odoo_map.py --model product.template`):
1. Определена: `product/models/product_template.py:18`.
2. Расширяют `_inherit`: `account/models/product.py:37`, `sale/models/product_template.py:10`, `stock/models/product.py:826`.
3. Делегирует `_inherits`: `product.product` (`product/models/product_product.py:16`, `product_tmpl_id`).
4. Оговорка: остальные аддоны (`sale_stock`, `purchase`, `mrp`…) не склонированы.

## O2. Кто вызывает `sale.order._action_confirm` (odoo19)

> Кто вызывает метод `_action_confirm` модели `sale.order` и кто его
> переопределяет в этих аддонах?

Эталон:
1. Определён `sale/models/sale_order.py:1237` (пустой хук с docstring).
2. Единственный вызов вне тестов: `action_confirm`, `sale_order.py:1196`.
3. Переопределений в склонированных аддонах нет (они в `sale_stock`, `sale_project` и др., которых нет в клоне).
4. Ловушка: `stock.move._action_confirm` (`stock/models/stock_move.py:1701`) и его вызовы из `stock_picking.py`, `stock_rule.py` — другой метод другой модели.
