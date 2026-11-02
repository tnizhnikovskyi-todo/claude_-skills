from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Vehicle(models.Model):
    _name = 'td.vehicle'
    _inherit = ['mail.thread']
    _description = 'Vehicle'
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    license_plate = fields.Char(string='Licence Plate')
    odometer = fields.Float(string='Odometer (km)', tracking=True)
    driver_id = fields.Many2one('res.partner', string='Driver')
    tag_ids = fields.Many2many('td.vehicle.tag', string='Tags')
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )
    state = fields.Selection(
        [('active', 'Active'), ('repair', 'In repair'), ('sold', 'Sold')],
        default='active',
    )

    _plate_uniq = models.Constraint(
        'UNIQUE(license_plate, company_id)',
        'License plate must be unique per company.',
    )

    @api.constrains('odometer')
    def _check_odometer(self):
        for vehicle in self:
            if vehicle.odometer < 0:
                raise ValidationError('Odometer cannot be negative.')

    def action_reset_odometer(self):
        self.write({'odometer': 0.0})


class VehicleTag(models.Model):
    _name = 'td.vehicle.tag'
    _description = 'Vehicle Tag'

    name = fields.Char(required=True)
    color = fields.Integer()
