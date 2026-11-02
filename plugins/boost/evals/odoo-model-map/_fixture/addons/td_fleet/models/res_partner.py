from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vehicle_ids = fields.One2many('td.vehicle', 'driver_id', string='Vehicles')
    vehicle_count = fields.Integer(compute='_compute_vehicle_count')

    def _compute_vehicle_count(self):
        for partner in self:
            partner.vehicle_count = len(partner.vehicle_ids)
