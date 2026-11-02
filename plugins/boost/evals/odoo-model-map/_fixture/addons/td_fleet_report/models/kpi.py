from odoo import api, fields, models


class MileageKpi(models.Model):
    _inherit = ['td.vehicle']
    _order = 'odometer desc, name'

    km_per_service = fields.Float(compute='_compute_km_per_service')

    @api.depends('odometer', 'service_ids')
    def _compute_km_per_service(self):
        for vehicle in self:
            count = len(vehicle.service_ids)
            vehicle.km_per_service = vehicle.odometer / count if count else 0.0


class ServiceLogKpi(models.Model):
    _inherit = 'td.vehicle.service'

    vehicle_odometer = fields.Float(related='vehicle_id.odometer', store=True)
    km_since_service = fields.Float(compute='_compute_km_since_service')

    @api.depends(
        'vehicle_id.odometer',
        'odometer_at',
    )
    def _compute_km_since_service(self):
        for log in self:
            log.km_since_service = log.vehicle_odometer - log.odometer_at
