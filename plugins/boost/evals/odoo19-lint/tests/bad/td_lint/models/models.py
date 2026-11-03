from odoo import api, fields, models


class TdVehicle(models.Model):
    _name = 'td.vehicle'
    _description = 'Vehicle'
    _sql_constraints = [('plate_uniq', 'unique(plate)', 'Plate must be unique')]

    name = fields.Char()
    plate = fields.Char()
    partner_id = fields.Many2one('res.partner')
    driver_mobile = fields.Char(related='partner_id.mobile')
    driver_title = fields.Many2one(related='partner_id.title')
    cost = fields.Float(group_operator='sum')

    def name_get(self):
        return [(r.id, r.plate) for r in self]

    @api.returns('self')
    def copy_vehicle(self):
        return self.copy()

    def get_managers(self):
        group = self.env.ref('td_lint.group_manager')
        return group.users

    def make_user(self):
        return self.env['res.users'].create({'name': 'X', 'login': 'x', 'groups_id': [(6, 0, [])]})

    def greet(self):
        return '%s %s' % (self.partner_id.title.name, self.partner_id.mobile)

    def stats(self):
        ctx = self._context
        return self.env['td.vehicle'].read_group([], ['cost:sum'], ['partner_id']), ctx

    def archive(self):
        self.toggle_active()

    def _cron(self):
        self.env['ir.cron']._notify_progress(done=1, remaining=0)

    def open_list(self):
        if self.user_has_groups('base.group_system'):
            pass
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'td.vehicle',
            'view_mode': 'tree,form',
            'context': {'tree_view_ref': 'td_lint.view_list'},
        }


class TdVehicleMixin(models.Model):
    _inherit = ['td.vehicle']

    extra = fields.Char()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pack_qty = fields.Float(compute='_compute_pack_qty')

    @api.depends('product_uom', 'product_uom_qty')
    def _compute_pack_qty(self):
        for line in self:
            line.pack_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)


class ResPartner(models.Model):
    _inherit = ['res.partner']

    td_code = fields.Char()


class TdTrip(models.Model):
    _name = 'td.trip'
    _description = 'Trip'

    driver_id = fields.Many2one('res.partner')
    driver_mobile = fields.Char(related='driver_id.mobile')
