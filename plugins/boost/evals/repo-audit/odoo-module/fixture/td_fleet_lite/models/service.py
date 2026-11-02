import logging
import re

from odoo import api, fields, models

from .cost_strategy import get_cost_strategy

_logger = logging.getLogger(__name__)


class TdFleetService(models.Model):
    _name = 'td.fleet.service'
    _description = 'Service visit'

    vehicle_id = fields.Many2one('td.fleet.vehicle', required=True, ondelete='cascade')
    date = fields.Date(default=fields.Date.context_today)
    plate = fields.Char(compute='_compute_plate')
    labor_hours = fields.Float()
    hourly_rate = fields.Float(default=40.0)
    parts_cost = fields.Float()
    cost = fields.Float(compute='_compute_cost', store=True)
    state = fields.Selection([('planned', 'Planned'), ('done', 'Done')], default='planned')

    @api.depends('vehicle_id.license_plate')
    def _compute_plate(self):
        for service in self:
            service.plate = self._format_plate(service.vehicle_id.license_plate)

    @api.depends('labor_hours', 'hourly_rate', 'parts_cost')
    def _compute_cost(self):
        strategy = get_cost_strategy()
        for service in self:
            service.cost = strategy.compute(service)

    @staticmethod
    def _format_plate(plate):
        return re.sub(r'\s+', '', plate or '').upper()

    @api.model
    def _cron_close_past_services(self):
        services = self.search([('state', '=', 'planned'), ('date', '<', fields.Date.today())])
        for service in services:
            try:
                service.write({'state': 'done'})
                service.vehicle_id.odometer += 0  # обновить write_date машины
            except Exception:
                pass
