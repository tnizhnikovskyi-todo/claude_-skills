import re

from odoo import api, fields, models


class TdFleetVehicle(models.Model):
    _name = 'td.fleet.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_name', store=True)
    model_name = fields.Char(required=True)
    license_plate = fields.Char(required=True, tracking=True)
    driver_id = fields.Many2one('res.partner')
    driver_phone = fields.Char()
    odometer = fields.Float()
    service_ids = fields.One2many('td.fleet.service', 'vehicle_id')
    service_count = fields.Integer(compute='_compute_service_count')
    color = fields.Char()  # TODO: добавить в форму
    active = fields.Boolean(default=True)

    @api.depends('model_name', 'license_plate')
    def _compute_name(self):
        for vehicle in self:
            vehicle.name = f"{vehicle.model_name} / {self._format_plate(vehicle.license_plate)}"

    def _compute_service_count(self):
        for vehicle in self:
            vehicle.service_count = self.env['td.fleet.service'].search_count(
                [('vehicle_id', '=', vehicle.id)]
            )

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        self.driver_phone = self.driver_id.phone

    def write(self, vals):
        res = super().write(vals)
        if 'driver_id' in vals:
            for vehicle in self:
                vehicle.driver_phone = vehicle.driver_id.phone
        return res

    @staticmethod
    def _format_plate(plate):
        plate = re.sub(r'\s+', '', plate or '').upper()
        return plate

    def _legacy_recompute_odometer(self):
        # пересчёт пробега из старого формата (мили), использовался до 2024
        for vehicle in self:
            vehicle.odometer = vehicle.odometer * 1.60934

    def action_view_services(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'td.fleet.service',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
        }
