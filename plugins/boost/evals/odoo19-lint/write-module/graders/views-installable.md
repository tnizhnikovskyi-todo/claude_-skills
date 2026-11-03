---
type: regex
target: { source: file, path: td_rental/views/rental_views.xml }
match: not_contains
weight: 5
---
<tree[\s>/]|//tree|\s(attrs|states)=|view_mode["\x27]?>[^<]*\btree\b
