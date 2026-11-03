from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    td_pallets = fields.Integer(compute='_compute_td_pallets')

    @api.depends('product_uom_qty')
    def _compute_td_pallets(self):
        helper = self.env['td.amount.mixin']
        for move in self:
            # product_uom_qty is never negative on stock moves
            move.td_pallets = helper._td_round_half_up(move.product_uom_qty / 40)
