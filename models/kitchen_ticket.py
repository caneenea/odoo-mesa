from odoo import fields, models, api


class KitchenTicketMesa(models.Model):
    _name = 'mesa.kitchen.ticket'
    _description = 'Kitchen Ticket'
    _rec_name = 'name'
    _order = 'time_sent desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    order_id = fields.Many2one('mesa.order', string='Order', required=True, ondelete='cascade')
    station_id = fields.Many2one('mesa.station', string='Station', required=True, ondelete='restrict')
    round = fields.Integer(string='Round', required=True, default=1,
                           help="Which send this ticket came from: 1 for the first Send to Kitchen, "
                                "2 and up for each Send New Items afterwards.")
    state = fields.Selection([
        ('new', 'New'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('cancelled', 'Cancelled'),
    ], string='State', required=True, default='new', compute='_compute_state', store=True, readonly=False,
       help="Follows the ticket's lines automatically: ready once every line is marked done. "
            "Cancelled is set by cancelling the order.")
    time_sent = fields.Datetime(string='Time Sent', required=True, default=lambda self: fields.Datetime.now())
    time_started = fields.Datetime(string='Time Started', required=False, help="Left empty until a line on this ticket is marked done.")
    time_ready = fields.Datetime(string='Time Ready', required=False, help="Left empty until every line on this ticket is marked done.")

    ticket_line_ids = fields.One2many('mesa.kitchen.ticket.line', 'ticket_id', string='Lines')
    order_status = fields.Selection(related='order_id.status', string='Priority', store=True,
                                     help="Mirrors the order's rush/normal status, kept here so the kitchen view doesn't need direct access to the order model.")
    items_summary = fields.Text(string='Items', compute='_compute_items_summary', store=True)

    _sql_constraints = [
        # same key as before on purpose: Odoo sees the definition changed and replaces the old constraint
        ('order_station_uniq', 'UNIQUE(order_id, station_id, round)', 'Only one kitchen ticket per station per order round.'),
    ]

    @api.depends('order_id.visit_id.table_id.table_num', 'station_id.type', 'round')
    def _compute_name(self):
        # same label lookup as the payment name in payment.py: 'pantry' -> 'Pantry'
        station_labels = dict(self.env['mesa.station']._fields['type'].selection)
        for ticket in self:
            visit = ticket.order_id.visit_id.sudo()
            table_label = visit.table_id.table_num if visit.table_id else 'No Table'
            station_label = station_labels.get(ticket.station_id.type, 'Station')
            ticket.name = "%s - %s" % (table_label, station_label)
            if ticket.round > 1:
                ticket.name += " (Round %s)" % ticket.round

    @api.depends('ticket_line_ids.order_item_id.name', 'ticket_line_ids.order_item_id.notes')
    def _compute_items_summary(self):
        for ticket in self:
            lines = []
            for ticket_line in ticket.ticket_line_ids:
                item = ticket_line.order_item_id
                line = item.name
                if item.notes:
                    line += ' (%s)' % item.notes
                lines.append(line)
            ticket.items_summary = '\n'.join(lines) or 'No items'

    @api.depends('ticket_line_ids.done')
    def _compute_state(self):
        for ticket in self:
            if ticket.state == 'cancelled':
                continue
            lines = ticket.ticket_line_ids
            done_lines = lines.filtered('done')
            if not done_lines:
                ticket.state = 'new'
            elif len(done_lines) == len(lines):
                if not ticket.time_ready:
                    ticket.time_ready = fields.Datetime.now()
                ticket.state = 'ready'
            else:
                if not ticket.time_started:
                    ticket.time_started = fields.Datetime.now()
                ticket.state = 'preparing'

    def action_start(self):
        to_start = self.filtered(lambda t: t.state == 'new')
        for ticket in to_start:
            if not ticket.time_started:
                ticket.time_started = fields.Datetime.now()
        to_start.state = 'preparing'

    def action_ready(self):
        to_ready = self.filtered(lambda t: t.state in ('new', 'preparing'))
        to_ready.ticket_line_ids.write({'done': True})
        for ticket in to_ready:
            if not ticket.time_ready:
                ticket.time_ready = fields.Datetime.now()
        to_ready.state = 'ready'
