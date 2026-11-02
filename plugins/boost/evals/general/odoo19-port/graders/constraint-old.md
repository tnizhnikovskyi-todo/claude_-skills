---
type: regex
target: { source: file, path: td_vehicle/models/td_vehicle.py }
match: not_contains
flags: m
---
^[ \t]+_sql_constraints\s*=
