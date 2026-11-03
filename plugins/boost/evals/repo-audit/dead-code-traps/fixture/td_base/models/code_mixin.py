from odoo import api, fields, models


class TdCodeMixin(models.AbstractModel):
    _name = 'td.code.mixin'
    _description = 'Internal code mixin'

    td_code = fields.Char(string='Code', index=True, copy=False)

    @api.constrains('td_code')
    def _check_td_code(self):
        for rec in self:
            if rec.td_code and ' ' in rec.td_code:
                raise models.ValidationError("Code must not contain spaces")
