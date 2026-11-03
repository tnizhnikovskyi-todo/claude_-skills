from odoo import api, fields, models


class TdDepot(models.Model):
    _name = 'td.depot'
    _inherit = ['td.code.mixin', 'mail.thread']
    _description = 'Depot'

    name = fields.Char(required=True)
    zone_id = fields.Many2one('td.depot.zone', required=True)
    capacity = fields.Integer()
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], default='open')

    @api.depends('name', 'td_code')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.td_code}] {rec.name}" if rec.td_code else rec.name

    def action_close(self):
        self.write({'state': 'closed'})

    def _cron_check_capacity(self):
        for depot in self.search([('state', '=', 'open')]):
            if depot.capacity <= 0:
                depot.message_post(body="Capacity is not set")

    def _old_capacity_calc(self):
        total = 0
        for depot in self:
            total += depot.capacity * 2
        return total
