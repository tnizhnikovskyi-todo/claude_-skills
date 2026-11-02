---
type: regex
target: { source: file, path: td_vehicle/models/td_vehicle.py }
match: not_contains
flags: m
weight: 5
---
^(?![ \t]*#).*(\.mobile["\x27]|groups_id|\)\.users\b)
