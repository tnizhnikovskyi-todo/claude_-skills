from odoo import fields, models


class TdDepotZone(models.Model):
    _name = 'td.depot.zone'
    _description = 'Depot zone'

    name = fields.Char(required=True)
    legacy_ref = fields.Char()

    def _ensure_default_zone(self):
        if not self.search_count([]):
            self.create({'name': 'Main'})
