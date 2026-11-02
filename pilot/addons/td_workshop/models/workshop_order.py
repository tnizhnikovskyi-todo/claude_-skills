from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WorkshopOrder(models.Model):
    _name = "td.workshop.order"
    _description = "Workshop Repair Order"
    _inherit = ["mail.thread"]
    _order = "date_received desc, id desc"

    name = fields.Char(default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)
    customer_phone = fields.Char()
    customer_mobile = fields.Char(related="partner_id.mobile")
    device = fields.Char(required=True)
    serial_number = fields.Char()
    date_received = fields.Date(default=fields.Date.context_today)
    date_deadline = fields.Date()
    technician_id = fields.Many2one("res.users", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    line_ids = fields.One2many("td.workshop.order.line", "order_id")
    discount = fields.Float("Discount (%)")
    currency_id = fields.Many2one(related="company_id.currency_id")
    amount_total = fields.Monetary(compute="_compute_amount_total", store=True)
    note = fields.Text()

    _serial_company_uniq = models.Constraint(
        "UNIQUE(serial_number, company_id)",
        "This serial number is already registered in this company.",
    )

    @api.depends("line_ids.subtotal")
    def _compute_amount_total(self):
        for order in self:
            total = sum(order.line_ids.mapped("subtotal"))
            order.amount_total = total * (1 - order.discount / 100)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("td.workshop.order") or "New"
                )
            if vals.get("partner_id") and not vals.get("customer_phone"):
                partner = self.env["res.partner"].browse(vals["partner_id"])
                vals["customer_phone"] = self._format_phone(partner.phone)
        return super().create(vals_list)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.customer_phone = self._format_phone(self.partner_id.phone)

    def _format_phone(self, phone):
        if not phone:
            return False
        return "".join(c for c in phone if c.isdigit() or c == "+")

    def action_start(self):
        for order in self:
            if order.state != "draft":
                raise UserError(_("Only draft orders can be started."))
            order.state = "in_progress"

    def action_done(self):
        for order in self:
            if not order.line_ids:
                raise UserError(_("Add at least one line before closing the order."))
            order.state = "done"

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_open_close_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "td.workshop.close.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }

    def _legacy_recompute(self):
        for order in self:
            total = 0.0
            for line in order.line_ids:
                total += line.quantity * line.price_unit
            order.amount_total = total

    @api.model
    def _cron_notify_overdue(self):
        orders = self.search(
            [
                ("state", "=", "in_progress"),
                ("date_deadline", "<", fields.Date.context_today(self)),
            ]
        )
        for order in orders:
            try:
                order.message_post(
                    body=_("Order %s is overdue.", order.name),
                    partner_ids=order.technician_id.partner_id.ids,
                )
            except Exception:
                pass
