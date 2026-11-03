from odoo import http
from odoo.http import request


class RentalApi(http.Controller):
    @http.route('/td_rental/ongoing', type='jsonrpc', auth='user')
    def ongoing(self):
        orders = request.env['td.rental.order'].search([('state', '=', 'ongoing')])
        return [{'id': o.id, 'code': o.code} for o in orders]
