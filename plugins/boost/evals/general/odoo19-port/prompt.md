---
name: general/odoo19-port
description: Порт модуля Odoo 16 → 19; шесть ловушек устаревшего API в одном кейсе, результат в файлах
tags: [general, hard, odoo, code]
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Переносим наш модуль `td_vehicle` с Odoo 16 на Odoo 19. Вот текущие файлы.

`td_vehicle/models/td_vehicle.py`:

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TdVehicle(models.Model):
    _name = "td.vehicle"
    _description = "Vehicle"
    _order = "name"
    _sql_constraints = [
        ("plate_uniq", "unique(company_id, plate)", "Plate must be unique per company."),
    ]

    name = fields.Char(required=True)
    plate = fields.Char(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    driver_id = fields.Many2one("res.partner")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("sold", "Sold")],
        default="draft",
    )
    odometer = fields.Float(group_operator="max")
    cost_ids = fields.One2many("td.vehicle.cost", "vehicle_id")
    total_cost = fields.Monetary(
        compute="_compute_total_cost", store=True, currency_field="currency_id"
    )

    def name_get(self):
        return [(v.id, "%s [%s]" % (v.name, v.plate)) for v in self]

    @api.depends("cost_ids.amount")
    def _compute_total_cost(self):
        for v in self:
            v.total_cost = sum(v.cost_ids.mapped("amount"))

    def action_activate(self):
        self.write({"state": "active"})

    def action_sell(self):
        if not self.user_has_groups("fleet.fleet_group_manager"):
            raise UserError(_("Only fleet managers can sell vehicles."))
        self.write({"state": "sold"})


class TdVehicleCost(models.Model):
    _name = "td.vehicle.cost"
    _description = "Vehicle cost"

    vehicle_id = fields.Many2one("td.vehicle", required=True, ondelete="cascade")
    date = fields.Date(default=fields.Date.context_today)
    amount = fields.Float(group_operator="sum")
    note = fields.Char()
```

`td_vehicle/views/td_vehicle_views.xml`:

```xml
<odoo>
    <record id="td_vehicle_view_tree" model="ir.ui.view">
        <field name="name">td.vehicle.tree</field>
        <field name="model">td.vehicle</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="plate"/>
                <field name="state"/>
                <field name="odometer"/>
                <field name="total_cost" sum="Total"/>
            </tree>
        </field>
    </record>

    <record id="td_vehicle_view_form" model="ir.ui.view">
        <field name="name">td.vehicle.form</field>
        <field name="model">td.vehicle</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_activate" type="object" string="Activate" states="draft"/>
                    <button name="action_sell" type="object" string="Sell" states="active"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="plate" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
                        <field name="driver_id" attrs="{'invisible': [('state', '=', 'sold')]}"/>
                        <field name="odometer"/>
                        <field name="company_id" groups="base.group_multi_company"/>
                    </group>
                    <field name="cost_ids">
                        <tree editable="bottom">
                            <field name="date"/>
                            <field name="amount"/>
                            <field name="note"/>
                        </tree>
                    </field>
                </sheet>
            </form>
        </field>
    </record>

    <record id="td_vehicle_action" model="ir.actions.act_window">
        <field name="name">Vehicles</field>
        <field name="res_model">td.vehicle</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
```

Перепиши оба файла под Odoo 19 и запиши их по тем же путям
(`td_vehicle/models/td_vehicle.py`, `td_vehicle/views/td_vehicle_views.xml`).
Поведение должно остаться прежним. В ответе коротко перечисли изменения.
