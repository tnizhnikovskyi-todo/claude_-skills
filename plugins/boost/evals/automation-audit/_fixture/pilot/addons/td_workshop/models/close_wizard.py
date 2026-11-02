from odoo import fields, models


class WorkshopCloseWizard(models.TransientModel):
    _name = "td.workshop.close.wizard"
    _description = "Close Repair Order"

    order_id = fields.Many2one("td.workshop.order", required=True)
    note = fields.Text(required=True)

    def action_confirm(self):
        self.ensure_one()
        self.order_id.action_done()
        self.order_id.message_post(body=self.note)
        return {"type": "ir.actions.act_window_close"}
