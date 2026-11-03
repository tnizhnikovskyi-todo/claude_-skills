from odoo import api, fields, models


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'td.amount.mixin']

    td_refund_units = fields.Integer(compute='_compute_td_refund_units')

    @api.depends('amount_total_signed')
    def _compute_td_refund_units(self):
        for move in self:
            # amount_total_signed is negative for credit notes
            move.td_refund_units = move._td_round_half_up(move.amount_total_signed)
