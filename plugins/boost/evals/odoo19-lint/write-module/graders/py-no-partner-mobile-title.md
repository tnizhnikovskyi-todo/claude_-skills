---
type: regex
target: { source: file, path: td_rental/models/rental_order.py }
match: not_contains
flags: m
weight: 5
---
^(?![ \t]*#).*(\.mobile["\x27]|\w+\.title["\x27])
