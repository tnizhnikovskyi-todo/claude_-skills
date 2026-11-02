---
type: regex
target: { source: file, path: td_sale_pack/models/sale_order.py }
match: not_contains
weight: 5
---
(partner_id|partner|contact)\.title(?!\s*\()|["\x27]partner_id\.title|res\.partner\.title
