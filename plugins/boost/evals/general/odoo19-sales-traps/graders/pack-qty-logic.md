---
type: llm
weight: 2
focus: { source: file, path: td_sale_pack/models/sale_order.py }
---
Проверь вычисление `pack_qty` в sale.order.line (Odoo 19).
PASS, если количество строки переводится из единицы строки в единицу
«упаковка» через механизм единиц измерения (например,
`line.product_uom_id._compute_quantity(line.product_uom_qty, pack_uom)`),
`@api.depends` включает количество и единицу строки, поле `store=True`,
и значение присваивается для каждой строки (в том числе без товара/единицы).
FAIL, если делится на жёсткие 6 без учёта единицы строки, нет store, или
compute не присваивает значение в каких-то ветках.
