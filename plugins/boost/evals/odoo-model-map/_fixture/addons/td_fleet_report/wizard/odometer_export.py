import csv
import io
import base64

from odoo import fields, models


class OdometerExport(models.TransientModel):
    _name = 'td.odometer.export'
    _description = 'Export odometer readings'

    min_km = fields.Float(default=0.0)
    vehicle_ids = fields.Many2many(
        comodel_name='td.vehicle',
        string='Vehicles',
    )
    file_data = fields.Binary(readonly=True)

    def action_export(self):
        self.ensure_one()
        vehicles = self.vehicle_ids or self.env['td.vehicle'].search(
            [('odometer', '>=', self.min_km), ('state', '!=', 'sold')]
        )
        buf = io.StringIO()
        writer = csv.writer(buf)
        for row in vehicles.read(['name', 'license_plate', 'odometer']):
            writer.writerow([row['name'], row['license_plate'], row['odometer']])
        self.file_data = base64.b64encode(buf.getvalue().encode())
        return {'type': 'ir.actions.act_window_close'}
