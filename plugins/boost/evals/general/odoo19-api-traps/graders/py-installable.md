---
type: regex
target: { source: file, path: td_vehicle/models/td_vehicle.py }
match: not_contains
weight: 5
---
\.mobile["\x27]|groups_id|\)\.users\b
