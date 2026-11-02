from odoo import api, fields, models


class TdRepairOrder(models.Model):
    _name = 'td.repair.order'
    _description = 'Repair Order'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(required=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In progress'), ('done', 'Done')],
        default='draft', tracking=True,
    )
    line_ids = fields.One2many('td.repair.line', 'order_id', string='Lines')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id, required=True,
    )

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})


class TdRepairLine(models.Model):
    _name = 'td.repair.line'
    _description = 'Repair Line'

    order_id = fields.Many2one('td.repair.order', required=True, ondelete='cascade')
    product_name = fields.Char(required=True)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='order_id.currency_id')
    subtotal = fields.Monetary(compute='_compute_subtotal', store=True, currency_field='currency_id')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
