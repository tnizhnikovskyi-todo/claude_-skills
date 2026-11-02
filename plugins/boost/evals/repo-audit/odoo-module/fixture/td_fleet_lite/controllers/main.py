from odoo import http
from odoo.http import request


class FleetController(http.Controller):

    @http.route('/fleet/vehicles', type='jsonrpc', auth='public', csrf=False)
    def vehicles(self, plate=None):
        domain = []
        if plate:
            domain = [('license_plate', 'ilike', plate)]
        vehicles = request.env['td.fleet.vehicle'].sudo().search(domain)
        return [{
            'name': v.name,
            'plate': v.license_plate,
            'driver': v.driver_id.name,
            'driver_phone': v.driver_phone,
            'odometer': v.odometer,
        } for v in vehicles]
