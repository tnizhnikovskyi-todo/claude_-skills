from odoo import http


class Api(http.Controller):
    @http.route('/td/api', type='jsonrpc', auth='user')
    def api(self):
        return {}
