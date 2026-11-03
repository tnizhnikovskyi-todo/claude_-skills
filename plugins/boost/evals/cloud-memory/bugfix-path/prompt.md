---
max_turns: 12
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
---
Запиши в память проекта, что мы выяснили про баг с дублями партнёров при импорте CSV. Сначала думали, что дело в кодировке файла: перекодировали CSV в UTF-8 — дубли остались. Настоящая причина: `_find_partner` в `td_import/models/partner.py` сравнивает VAT как есть, а в CSV у VAT бывают пробелы. Починили нормализацией в `_norm_vat` (коммит a1b2c3d), проверили тестом `test_import_vat_spaces`.
