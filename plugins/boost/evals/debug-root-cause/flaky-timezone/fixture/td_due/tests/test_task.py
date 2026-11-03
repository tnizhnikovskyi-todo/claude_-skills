from datetime import date

from odoo.tests import TransactionCase


class TestDueTask(TransactionCase):

    def test_due_today(self):
        self.env.user.tz = 'Europe/Kyiv'
        task = self.env['td.due.task'].create({'name': 'Call client', 'days': 0})
        self.assertEqual(task.due_date, date.today())
