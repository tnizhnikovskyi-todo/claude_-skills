from odoo import api, fields, models

SERVICE_INTERVAL_KM = 15000.0


class FleetMaintenance(models.Model):
    _inherit = "td.vehicle"

    service_ids = fields.One2many("td.vehicle.service", "vehicle_id")
    next_service_km = fields.Float(compute="_compute_next_service_km", store=True)

    @api.depends("odometer", "service_ids.odometer_at")
    def _compute_next_service_km(self):
        for vehicle in self:
            last = max(vehicle.service_ids.mapped("odometer_at") or [0.0])
            vehicle.next_service_km = last + SERVICE_INTERVAL_KM

    def action_reset_odometer(self):
        res = super().action_reset_odometer()
        self.service_ids.write({'note': 'Reset'})
        return res


class ServiceLog(models.Model):
    _name = "td.vehicle.service"
    _description = "Vehicle Service"
    _order = "date desc"

    vehicle_id = fields.Many2one(
        comodel_name="td.vehicle",
        required=True,
        ondelete="cascade",
    )
    date = fields.Date(required=True, default=fields.Date.context_today)
    odometer_at = fields.Float(string="Odometer at service")
    driver_id = fields.Many2one(related="vehicle_id.driver_id", store=True)
    cost = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    note = fields.Text()

    def action_tag_as_repair(self):
        tag = self.env["td.vehicle.tag"].search([("name", "=", "Repair")], limit=1)
        if not tag:
            tag = self.env["td.vehicle.tag"].create({"name": "Repair"})
        self.vehicle_id.write({"tag_ids": [(4, tag.id)], "state": "repair"})


class ServiceCard(models.Model):
    _name = "td.service.card"
    _description = "Service Card"
    _inherits = {"td.vehicle": "vehicle_id"}

    vehicle_id = fields.Many2one("td.vehicle", required=True, ondelete="cascade")
    card_no = fields.Char(required=True)
    valid_until = fields.Date()
