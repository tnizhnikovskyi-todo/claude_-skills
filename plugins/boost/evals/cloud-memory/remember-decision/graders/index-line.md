---
type: regex
pattern: "decision.*(вторник|вт).*14:00.*\\.md"
flags: i
target:
  source: file
  path: memory/INDEX.md
weight: 1
---
В memory/INDEX.md есть строка индекса с типом, сутью и ссылкой на файл записи
