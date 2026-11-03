from odoo import api, fields, models


class RentalOrder(models.Model):
    _name = 'td.rental.order'
    _description = 'Rental Order'
    _inherit = ['mail.thread']
    _order = 'date_start desc, id desc'

    _sql_constraints = [
        ('code_uniq', 'unique(code, company_id)', 'Rental code must be unique per company.'),
    ]

    code = fields.Char(required=True, copy=False, default='/')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    customer_id = fields.Many2one('res.partner', required=True, tracking=True)
    customer_phone = fields.Char(related='customer_id.phone')
    customer_mobile = fields.Char(related='customer_id.mobile')
    date_start = fields.Date(required=True, default=fields.Date.context_today)
    date_end = fields.Date()
    daily_rate = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='company_id.currency_id')
    amount_total = fields.Monetary(compute='_compute_amount_total', store=True, currency_field='currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('done', 'Returned'),
    ], default='draft', required=True, tracking=True)

    _date_check = models.Constraint(
        'CHECK(date_end IS NULL OR date_end >= date_start)',
        'The end date cannot be earlier than the start date.',
    )

    @api.depends('date_start', 'date_end', 'daily_rate')
    def _compute_amount_total(self):
        for order in self:
            days = (order.date_end - order.date_start).days + 1 if order.date_end else 0
            order.amount_total = days * order.daily_rate

    def name_get(self):
        return [(order.id, f'{order.code} - {order.customer_id.name}') for order in self]

    def action_start(self):
        self.filtered(lambda o: o.state == 'draft').write({'state': 'ongoing'})

    def action_return(self):
        self.filtered(lambda o: o.state == 'ongoing').write({'state': 'done'})

    @api.model
    def _cron_close_overdue(self):
        today = fields.Date.context_today(self)
        overdue = self.search([('state', '=', 'ongoing'), ('date_end', '<', today)])
        if self._context.get('rental_dry_run'):
            return overdue
        overdue.action_return()
        return overdue
