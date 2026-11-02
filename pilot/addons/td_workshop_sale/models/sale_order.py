from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    workshop_order_id = fields.Many2one("td.workshop.order", string="Repair Order", copy=False)

    @api.model
    def _prepare_workshop_note(self, workshop_order):
        phone = self._format_phone(workshop_order.partner_id.phone)
        return f"Repair {workshop_order.name}: {workshop_order.device}. Contact: {phone or '-'}"

    def _format_phone(self, phone):
        if not phone:
            return False
        return "".join(c for c in phone if c.isdigit() or c == "+")
