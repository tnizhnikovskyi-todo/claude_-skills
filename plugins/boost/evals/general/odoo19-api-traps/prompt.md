---
name: general/odoo19-api-traps
description: Обычная доработка Odoo 19, где естественный код использует API, изменённый в 18–19 (сверено по исходникам 19.0)
tags: [general, hard, odoo, code]
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Модуль `td_vehicle`, Odoo 19. Текущая модель
`td_vehicle/models/td_vehicle.py`:

```python
from odoo import api, fields, models


class TdVehicle(models.Model):
    _name = "td.vehicle"
    _description = "Vehicle"

    name = fields.Char(required=True)
    plate = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    driver_id = fields.Many2one("res.partner")
    cost_ids = fields.One2many("td.vehicle.cost", "vehicle_id")
    total_cost = fields.Float(compute="_compute_total_cost", store=True)

    @api.depends("cost_ids.amount")
    def _compute_total_cost(self):
        for vehicle in self:
            vehicle.total_cost = sum(vehicle.cost_ids.mapped("amount"))


class TdVehicleCost(models.Model):
    _name = "td.vehicle.cost"
    _description = "Vehicle cost"

    vehicle_id = fields.Many2one("td.vehicle", required=True, ondelete="cascade")
    amount = fields.Float()
```

Нужно:

1. Файл `td_vehicle/security/td_vehicle_security.xml`: две группы,
   «Пользователь автопарка» и «Менеджер автопарка», в одном разделе прав
   «Автопарк». Менеджер включает права пользователя, пользователь включает
   `base.group_user`. Администратора (`base.user_admin`) сразу добавить в
   менеджеры.
2. В модель `td.vehicle` добавить:
   - `get_fleet_managers()` — пользователи из группы менеджеров;
   - `cost_by_driver()` — словарь `{partner_id: сумма amount}` по всем
     затратам, одним запросом с группировкой в БД;
   - `_cron_recompute_costs()` — пересчитывает `total_cost` у всех машин
     пачками по 100 и фиксирует прогресс, чтобы при таймауте крон продолжил
     с того же места;
   - кнопку `action_toggle_archive()` — архивирует выбранные активные машины
     и возвращает из архива выбранные архивные;
   - поле `driver_mobile` — мобильный телефон водителя, только для показа на
     форме.

Запиши оба файла (`td_vehicle/models/td_vehicle.py` целиком,
`td_vehicle/security/td_vehicle_security.xml`). В ответе коротко: что сделано.
