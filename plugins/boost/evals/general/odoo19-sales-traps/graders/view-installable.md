---
type: regex
target: { source: file, path: td_sale_pack/views/sale_order_views.xml }
match: not_contains
weight: 5
---
name=["\x27](product_uom|mobile)["\x27]|//tree|<tree[\s>]
