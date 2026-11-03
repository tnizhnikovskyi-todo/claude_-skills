---
type: regex
target: { source: file, path: td_rental/models/rental_order.py }
match: not_contains
flags: m
weight: 3
---
^(?![ \t]*#).*_sql_constraints
