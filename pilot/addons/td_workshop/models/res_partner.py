from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    workshop_order_count = fields.Integer(compute="_compute_workshop_order_count")

    def _compute_workshop_order_count(self):
        for partner in self:
            partner.workshop_order_count = self.env["td.workshop.order"].search_count(
                [("partner_id", "=", partner.id)]
            )

    def action_view_workshop_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "td.workshop.order",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "name": "Repair Orders",
        }
