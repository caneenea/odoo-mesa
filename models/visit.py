from odoo import fields, models, api
from odoo.exceptions import UserError


class VisitMesa(models.Model):
    _name = 'mesa.visit'
    _description = 'Visit Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    time_opened = fields.Datetime(string='Time Opened', required=True)
    time_closed = fields.Datetime(string='Time Closed', required=False, help="Left empty while the visit is still ongoing.")
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', required=True, default='open')

    total = fields.Float(string='Total', compute='_compute_totals', store=True, help="Sum of non-cancelled order totals.")
    amount_paid = fields.Float(string='Amount Paid', compute='_compute_totals', store=True)
    balance_due = fields.Float(string='Balance Due', compute='_compute_totals', store=True)

    payment_ids = fields.One2many("mesa.payment", "visit_id", string="Payments")
    order_ids = fields.One2many("mesa.order", "visit_id", string="Orders")

    table_id = fields.Many2one('mesa.table', string='Table', required=False, help="Table occupied during this visit.")
    server_id = fields.Many2one('mesa.employee', string='Server', required=False, help="Employee responsible for this visit.")
    reservation_id = fields.Many2one('mesa.reservation', string='Reservation', required=False, help="Reservation this visit originated from, if any.")

    _order = 'time_opened desc'

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

    def action_close_visit(self):
        self.write({'state': 'closed', 'time_closed': fields.Datetime.now()})

    def action_reopen_visit(self):
        self.write({'state': 'open', 'time_closed': False})

    def unlink(self):
        if self.filtered(lambda visit: visit.state == 'closed'):
            raise UserError('Closed visits can not be deleted.')
        return super().unlink()
