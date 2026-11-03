from odoo import fields, models


class RentalKpi(models.Model):
    _inherit = ['td.rental.order']

    margin_percent = fields.Float(help='Planned margin, %')

    def kpi_by_customer(self):
        return self.read_group([], ['amount_total:sum'], ['customer_id'])
