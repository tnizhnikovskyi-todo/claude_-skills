from odoo import api, fields, models


class WorkshopOrderLine(models.Model):
    _name = "td.workshop.order.line"
    _description = "Workshop Repair Order Line"

    order_id = fields.Many2one("td.workshop.order", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product")
    name = fields.Char(required=True)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float()
    currency_id = fields.Many2one(related="order_id.currency_id")
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True)

    _quantity_positive = models.Constraint(
        "CHECK(quantity > 0)", "Quantity must be positive."
    )

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
