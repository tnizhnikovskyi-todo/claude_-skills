from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rental_order_ids = fields.One2many('td.rental.order', 'customer_id')
    rental_count = fields.Integer(compute='_compute_rental_count')

    @api.depends('rental_order_ids')
    def _compute_rental_count(self):
        for partner in self:
            partner.rental_count = len(partner.rental_order_ids)
