from odoo import api, fields, models


class TdVehicle(models.Model):
    _name = 'td.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread']

    _plate_uniq = models.Constraint('UNIQUE(plate)', 'Plate must be unique')

    name = fields.Char()
    plate = fields.Char()
    partner_id = fields.Many2one('res.partner')
    driver_phone = fields.Char(related='partner_id.phone')
    cost = fields.Float(aggregator='sum')

    @api.depends('plate')
    def _compute_display_name(self):
        for r in self:
            r.display_name = r.plate

    def get_managers(self):
        group = self.env.ref('td_lint.group_manager')
        return group.user_ids

    def make_user(self):
        return self.env['res.users'].create({'name': 'X', 'login': 'x', 'group_ids': [(6, 0, [])]})

    def greet(self):
        name = self.partner_id.name or ''
        return '%s %s' % (name.title(), self.partner_id.phone)

    def stats(self):
        ctx = self.env.context
        return self.env['td.vehicle']._read_group([], ['partner_id'], ['cost:sum']), ctx

    def archive(self):
        self.filtered('active').action_archive()

    def _cron(self):
        self.env['ir.cron']._commit_progress(processed=1, remaining=0)

    def open_list(self):
        if self.env.user.has_group('base.group_system'):
            pass
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'td.vehicle',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'context': {'list_view_ref': 'td_lint.view_list'},
        }


class TdVehicleExt(models.Model):
    _inherit = 'td.vehicle'

    extra = fields.Char()


class TdVehicle2(models.Model):
    _name = 'td.vehicle'
    _inherit = ['td.vehicle', 'mail.activity.mixin']


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pack_qty = fields.Float(compute='_compute_pack_qty')

    @api.depends('product_uom_id', 'product_uom_qty')
    def _compute_pack_qty(self):
        for line in self:
            line.pack_qty = line.product_uom_id._compute_quantity(line.product_uom_qty, line.product_id.uom_id)

    def _prepare_move_vals(self):
        # ключ vals для stock.move: у него поле product_uom осталось
        return {'product_uom': self.product_uom_id.id}


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _uom(self):
        return self.product_uom


class ResPartner(models.Model):
    _inherit = 'res.partner'

    td_code = fields.Char()


class TdTrip(models.Model):
    _name = 'td.trip'
    _description = 'Trip'

    driver_id = fields.Many2one('res.partner')
    driver_phone = fields.Char(related='driver_id.phone')
    job_title = fields.Char()
    label = fields.Char(compute='_compute_label')

    def _compute_label(self):
        for trip in self:
            trip.label = (trip.job_title or '').title()
