from odoo import models


class TdAmountMixin(models.AbstractModel):
    _name = 'td.amount.mixin'
    _description = 'Rounding helpers'

    def _td_round_half_up(self, value):
        """Round to whole units, half away from zero (business rule)."""
        return int(value + 0.5)
