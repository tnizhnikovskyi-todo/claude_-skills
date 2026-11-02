---
name: general/odoo19-sales-traps
description: Доработка продаж в Odoo 19, где естественный код ломает установку (поля и значения, удалённые в 18–19; сверено по исходникам 19.0)
tags: [general, hard, odoo, code]
max_turns: 14
timeout_seconds: 450
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Новый модуль `td_sale_pack` для Odoo 19 (зависит от `sale_stock`). Нужно:

1. `td_sale_pack/data/uom_data.xml`: единица измерения «Упаковка (6 шт)»,
   6 штук (`uom.product_uom_unit`) в одной упаковке.
2. `td_sale_pack/data/product_data.xml`: товар «Набор фильтров» —
   складской (с учётом остатков), продаётся в этих упаковках, цена 120.
3. `td_sale_pack/models/sale_order.py`:
   - в строке заказа (`sale.order.line`) хранимое поле `pack_qty` —
     количество строки, пересчитанное в упаковки (строка может быть в любой
     единице: штуки, упаковки, дюжины);
   - в заказе (`sale.order`) поле `customer_mobile` — мобильный телефон
     клиента, только для показа.
4. `td_sale_pack/views/sale_order_views.xml`: в строках заказа на форме
   `sale.view_order_form` показать `pack_qty` сразу после единицы измерения
   строки; `customer_mobile` — после клиента.

Запиши все четыре файла. Манифест и `__init__.py` не нужны. В ответе
коротко: что сделано.
