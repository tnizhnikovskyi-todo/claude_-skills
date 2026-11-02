---
type: regex
target: { source: file, path: td_sale_pack/models/sale_order.py }
match: not_contains
flags: m
weight: 5
---
^(?![ \t]*#).*\.mobile["\x27]
