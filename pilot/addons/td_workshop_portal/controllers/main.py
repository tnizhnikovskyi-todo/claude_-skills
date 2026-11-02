from odoo import http
from odoo.http import request


class WorkshopStatus(http.Controller):

    @http.route("/repair/<int:order_id>", type="http", auth="public")
    def repair_status(self, order_id, **kwargs):
        order = request.env["td.workshop.order"].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()
        return request.render(
            "td_workshop_portal.workshop_status_page",
            {"order": order},
        )
