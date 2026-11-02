---
type: regex
target: { source: file, path: td_vehicle/models/td_vehicle.py }
match: not_contains
---
(?<![\w_])toggle_active\(
