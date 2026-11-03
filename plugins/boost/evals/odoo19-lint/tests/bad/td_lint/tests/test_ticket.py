from odoo.tests.common import SavepointCase


class TestTicket(SavepointCase):
    def test_create(self):
        self.assertTrue(self.env['td.ticket'].create({'name': 'x'}))
