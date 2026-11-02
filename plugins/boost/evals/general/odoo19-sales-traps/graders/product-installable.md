---
type: regex
target: { source: file, path: td_sale_pack/data/product_data.xml }
match: not_contains
weight: 5
---
name=["\x27]detailed_type["\x27]|name=["\x27]type["\x27][^>]*>\s*product\s*<
