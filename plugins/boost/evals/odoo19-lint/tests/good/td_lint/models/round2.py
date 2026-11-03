from datetime import date

from odoo import api, fields, models
from odoo.api import NewId
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.modules.registry import Registry


class TdTicket(models.Model):
    _name = 'td.ticket'
    _description = 'Ticket'

    name = fields.Char()
    qty = fields.Float(digits='Product Unit')
    deadline = fields.Date(default=lambda self: fields.Date.today())
    started = fields.Date(default=lambda self: date.today())

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if not rec.name:
                raise ValidationError('name')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('name', '/')
        return super().create(vals_list)

    @api.model
    def default_get(self, fields):
        return super().default_get(fields)

    @api.model
    def _search_open(self):
        return self.search([('qty', '>', 0)])

    def _domain(self):
        return Domain('name', '!=', False) & Domain('qty', '>', 0)

    def _is_new(self):
        return isinstance(self.id, NewId)

    def _registry(self):
        return Registry(self.env.cr.dbname), self.env.registry

    def _template_group(self):
        return self.env.ref('base.default_user_group')


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _login(self, credential, user_agent_env):
        return super()._login(credential, user_agent_env)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _taxes(self):
        return self.tax_ids


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _taxes(self):
        return self.tax_ids


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _taxes(self):
        # у товара поле taxes_id осталось
        return self.taxes_id
