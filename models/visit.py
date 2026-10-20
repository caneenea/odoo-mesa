from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class VisitMesa(models.Model):
    _name = 'mesa.visit'
    _description = 'Visit Mesa'
    _rec_name = 'name'
    _order = 'time_opened desc'


    name = fields.Char(string='Name', compute='_compute_name', store=True)
    time_opened = fields.Datetime(string='Time Opened', required=True, default=lambda self: fields.Datetime.now())
    time_closed = fields.Datetime(string='Time Closed', required=False, help="Left empty while the visit is still ongoing.")
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', required=True, default='open')

    # digits=(16, 2) stores the money values rounded to 2 decimals, so a zero balance is exactly 0.00
    total = fields.Float(string='Total', digits=(16, 2), compute='_compute_totals', store=True,
                         help="Sum of non-cancelled order totals.")
    amount_paid = fields.Float(string='Amount Paid', digits=(16, 2), compute='_compute_totals', store=True)
    balance_due = fields.Float(string='Balance Due', digits=(16, 2), compute='_compute_totals', store=True)

    payment_ids = fields.One2many("mesa.payment", "visit_id", string="Payments")
    order_ids = fields.One2many("mesa.order", "visit_id", string="Orders")

    table_id = fields.Many2one('mesa.table', string='Table', required=False, help="Table occupied during this visit.")
    server_id = fields.Many2one('mesa.employee', string='Server', required=False, help="Employee responsible for this visit.")
    reservation_id = fields.Many2one('mesa.reservation', string='Reservation', required=False, help="Reservation this visit originated from, if any.")


    @api.depends('order_ids.total', 'order_ids.state', 'payment_ids.amount')
    def _compute_totals(self):
        for visit in self:
            visit.total = sum(visit.order_ids.filtered(lambda o: o.state != 'cancelled').mapped('total'))
            visit.amount_paid = sum(visit.payment_ids.mapped('amount'))
            visit.balance_due = visit.total - visit.amount_paid

    @api.depends('table_id.table_num', 'time_opened')
    def _compute_name(self):
        for visit in self:
            time_str = visit.time_opened.strftime('%m/%d %H:%M') if visit.time_opened else 'No Time'
            if visit.table_id:
                visit.name = "Table %s - %s" % (visit.table_id.table_num, time_str)
            else:
                visit.name = "Visit - %s" % time_str

    @api.constrains('server_id')
    def _check_server_position(self):
        for visit in self:
            if visit.server_id and visit.server_id.position_id.title != 'server':
                raise ValidationError('%s is not a server.' % visit.server_id.full_name)

    @api.model
    def create(self, values):
        if values.get('table_id'):
            table = self.env['mesa.table'].browse(values['table_id'])
            if table.table_status != 'free':
                raise UserError('Table %s is not free and can not be used.' % table.table_num)
        visit = super().create(values)
        if visit.table_id:
            visit.table_id.sudo().table_status = 'busy'
        return visit

    def action_close_visit(self):
        if self.filtered(lambda visit: visit.balance_due != 0):
            raise UserError('Visit has an outstanding balance and cannot be closed.')
        for visit in self:
            active_orders = visit.order_ids.filtered(lambda o: o.state not in ('served', 'billed', 'cancelled'))
            if active_orders:
                raise UserError(
                    'This visit still has orders that are not served, billed or cancelled. '
                    'Finish or cancel them before closing the visit.'
                )
        to_close = self.filtered(lambda visit: visit.state == 'open')
        to_close.write({'state': 'closed', 'time_closed': fields.Datetime.now()})
        for visit in to_close:
            if visit.table_id:
                visit.table_id.sudo().table_status = 'needs_cleaning'
            for payment in visit.payment_ids.filtered('guest_id'):
                payment.guest_id.sudo().points += payment.amount / 10.0

    def action_reopen_visit(self):
        to_reopen = self.filtered(lambda visit: visit.state == 'closed')
        for visit in to_reopen.filtered('table_id'):
            other_open = self.search([
                ('table_id', '=', visit.table_id.id),
                ('state', '=', 'open'),
                ('id', '!=', visit.id),
            ])
            if other_open:
                raise UserError(
                    'Table %s is already in use by another open visit, so this visit can not be reopened.'
                    % visit.table_id.table_num
                )
        to_reopen.write({'state': 'open', 'time_closed': False})
        for visit in to_reopen:
            if visit.table_id:
                visit.table_id.sudo().table_status = 'busy'

    def unlink(self):
        if self.filtered(lambda visit: visit.state == 'closed'):
            raise UserError('Closed visits can not be deleted.')
        return super().unlink()
