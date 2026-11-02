from odoo import _, fields, models
from odoo.exceptions import UserError


class WorkshopOrder(models.Model):
    _inherit = "td.workshop.order"

    sale_order_id = fields.Many2one("sale.order", string="Quotation", copy=False, readonly=True)

    def action_create_quotation(self):
        self.ensure_one()
        if self.sale_order_id:
            raise UserError(_("A quotation already exists for this order."))
        lines = []
        for line in self.line_ids:
            if not line.product_id:
                continue
            lines.append(
                (0, 0, {
                    "product_id": line.product_id.id,
                    "name": line.name,
                    "product_uom_qty": line.quantity,
                    "price_unit": line.price_unit,
                    "discount": self.discount,
                })
            )
        sale_order = self.env["sale.order"].create({
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "workshop_order_id": self.id,
            "order_line": lines,
            "note": self.env["sale.order"]._prepare_workshop_note(self),
        })
        self.sale_order_id = sale_order
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": sale_order.id,
            "view_mode": "form",
        }
