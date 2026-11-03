from odoo import fields, models


class TdDepot(models.Model):
    _name = 'td.depot'
    _description = 'Depot'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    manager_id = fields.Many2one('res.users')

    def action_report(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'td.depot',
            'view_mode': 'list',
            'domain': [('manager_id', '=', self.env.uid)],
        }
