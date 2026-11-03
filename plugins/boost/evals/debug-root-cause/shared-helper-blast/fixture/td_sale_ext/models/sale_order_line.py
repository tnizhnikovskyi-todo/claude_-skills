from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line', 'td.amount.mixin']

    td_bonus_points = fields.Integer(compute='_compute_td_bonus_points', store=True)

    @api.depends('price_subtotal')
    def _compute_td_bonus_points(self):
        for line in self:
            # 1 point per 10 units of subtotal; negative for discount lines
            line.td_bonus_points = line._td_round_half_up(line.price_subtotal / 10)
