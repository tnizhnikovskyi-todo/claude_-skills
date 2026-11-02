---
type: regex
target: { source: file, path: td_vehicle/security/td_vehicle_security.xml }
match: not_contains
---
name=["\x27](users|groups_id)["\x27]
