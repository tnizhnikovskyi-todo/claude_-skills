---
type: regex
target: { source: file, path: td_sale_pack/data/uom_data.xml }
match: not_contains
weight: 5
---
name=["\x27](category_id|uom_type|factor_inv)["\x27]
