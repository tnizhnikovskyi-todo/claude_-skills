import odoo
from odoo import api, fields, models
from odoo.osv import expression


class TdTicket(models.Model):
    _name = 'td.ticket'
    _description = 'Ticket'
    _constraints = [(lambda self: True, 'never checked', ['name'])]

    name = fields.Char()
    qty = fields.Float(digits='Product Unit of Measure')
    deadline = fields.Date(default=lambda self: fields.date.today())

    @api.model
    def create(self, vals):
        vals.setdefault('name', '/')
        return super().create(vals)

    @api.model
    def default_get(self, fields_list):
        return super().default_get(fields_list=fields_list)

    def _domain(self):
        return expression.AND([[('name', '!=', False)], [('qty', '>', 0)]])

    def _is_new(self):
        return isinstance(self.id, models.NewId)

    def _registry(self):
        return odoo.registry(self.env.cr.dbname)

    def _template_user(self):
        return self.env.ref('base.default_user')


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, credential, user_agent_env):
        return super()._login(db, credential, user_agent_env)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _taxes(self):
        return self.tax_id


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _taxes(self):
        return self.taxes_id
