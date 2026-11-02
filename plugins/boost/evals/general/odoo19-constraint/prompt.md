---
description: Код Odoo 19 с ловушкой устаревшего API (_sql_constraints → models.Constraint)
tags: [general, odoo, code]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Пишем модуль под Odoo 19. Есть модель:

```python
from odoo import fields, models

class TdListing(models.Model):
    _name = "td.listing"
    _description = "Listing"

    partner_id = fields.Many2one("res.partner", required=True)
    code = fields.Char(required=True)
    qty = fields.Integer()
```

Добавь ограничения на уровне базы данных: пара (partner_id, code) уникальна,
qty не может быть отрицательным. Дай полный итоговый код модели.
