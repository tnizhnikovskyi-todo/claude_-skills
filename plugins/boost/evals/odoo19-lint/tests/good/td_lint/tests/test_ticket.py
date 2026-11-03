from odoo.tests.common import TransactionCase


class TestTicket(TransactionCase):
    def test_create(self):
        self.assertTrue(self.env['td.ticket'].create({'name': 'x'}))
