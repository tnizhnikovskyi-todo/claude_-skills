from datetime import timedelta

from odoo import api, fields, models


class TdDueTask(models.Model):
    _name = 'td.due.task'
    _description = 'Task with due date'

    name = fields.Char(required=True)
    days = fields.Integer(default=0)
    due_date = fields.Date(compute='_compute_due_date', store=True)

    @api.depends('days')
    def _compute_due_date(self):
        for task in self:
            task.due_date = (fields.Datetime.now() + timedelta(days=task.days)).date()
