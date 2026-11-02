---
type: regex
target: { source: file, path: td_sale_pack/models/sale_order.py }
match: not_contains
flags: m
weight: 5
---
^(?![ \t]*#).*((partner_id|partner|contact)\.title(?![ \t]*\()|["\x27]partner_id\.title)
