---
type: regex
target: { source: file, path: td_vehicle/data/ir_cron.xml }
match: not_contains
weight: 5
---
name=["\x27](numbercall|doall)["\x27]
