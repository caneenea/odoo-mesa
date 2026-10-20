from odoo import fields, models, api
from odoo.exceptions import UserError


class OrderMesa(models.Model):
    _name = 'mesa.order'
    _description = 'Order Mesa'
    _rec_name = 'code'
    _order = 'time desc'


    code = fields.Char(string="Order Number", readonly=True)
    time =fields.Datetime(string='Time', required=True, default=lambda self: fields.Datetime.now())
    status = fields.Selection([
        ('normal', 'Normal'),
        ('rush', 'Rush'),
    ], string='Status', required=True, default='normal', help="Kitchen priority for this order.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Kitchen'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('billed', 'Billed'),
        ('cancelled', 'Cancelled'),
    ], string='State', required=True, default='draft', compute='_compute_state', store=True, readonly=False,
       help="Workflow stage of this order. Sent/Preparing/Ready follow the kitchen tickets automatically; "
            "the other stages are set by the buttons.")
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    order_item_ids = fields.One2many("mesa.order_item", "order_id", string="Order Items")
    ticket_ids = fields.One2many("mesa.kitchen.ticket", "order_id", string="Kitchen Tickets")
    visit_id = fields.Many2one("mesa.visit", string="Visit", required=True, ondelete='cascade')
    has_unsent_items = fields.Boolean(string='Unsent Items', compute='_compute_has_unsent_items', store=True,
                                      help="True when at least one line hasn't been sent to the kitchen yet.")


    @api.model
    def create(self, values):
        if values.get('visit_id'):
            visit = self.env['mesa.visit'].browse(values['visit_id'])
            if visit.state == 'closed':
                raise UserError("You can't add an order to a closed visit. Reopen the visit first.")
        values['code'] = self.env['ir.sequence'].next_by_code('mesa.order')
        return super().create(values)

    @api.depends('order_item_ids.total')
    def _compute_total(self):
        for order in self:
            order.total = sum(order.order_item_ids.mapped('total'))

    @api.depends('order_item_ids.is_ticketed')
    def _compute_has_unsent_items(self):
        for order in self:
            order.has_unsent_items = any(not item.is_ticketed for item in order.order_item_ids)

    @api.depends('ticket_ids.state')
    def _compute_state(self):
        for order in self:
            if order.state not in ('sent', 'preparing', 'ready'):
                continue
            tickets = order.ticket_ids.filtered(lambda t: t.state != 'cancelled')
            if not tickets:
                continue
            if all(t.state == 'ready' for t in tickets):
                order.state = 'ready'
            elif all(t.state == 'new' for t in tickets):
                order.state = 'sent'
            else:
                order.state = 'preparing'

    def _send_items(self, items):
        """Create one kitchen ticket per station, as a new round, for the given lines of this order,
        and deduct their stock. Raises before creating anything if a check fails."""
        self.ensure_one()
        required_qty = {}
        for item in items:
            if not item.menu_item_id.station_ids:
                raise UserError(
                    '"%s" has no station assigned. Set one before sending this order to the kitchen.'
                    % item.menu_item_id.name
                )
            required_qty[item.menu_item_id] = required_qty.get(item.menu_item_id, 0) + item.quantity

        for menu_item, qty in required_qty.items():
            if menu_item.stock_qty < qty:
                raise UserError(
                    'Not enough stock for "%s": %s in stock, %s needed.'
                    % (menu_item.name, menu_item.stock_qty, qty)
                )

        next_round = 1
        if self.ticket_ids:
            next_round = max(self.ticket_ids.mapped('round')) + 1
        tickets_by_station = {}
        for item in items:
            for station in item.menu_item_id.station_ids:
                ticket = tickets_by_station.get(station)
                if ticket is None:
                    ticket = self.env['mesa.kitchen.ticket'].sudo().create({
                        'order_id': self.id,
                        'station_id': station.id,
                        'round': next_round,
                    })
                    tickets_by_station[station] = ticket
                self.env['mesa.kitchen.ticket.line'].sudo().create({
                    'ticket_id': ticket.id,
                    'order_item_id': item.id,
                    'quantity': item.quantity,
                })
            item.menu_item_id.sudo().stock_qty -= item.quantity

    def action_send(self):
        to_send = self.filtered(lambda order: order.state == 'draft')
        for order in to_send:
            order._send_items(order.order_item_ids)
        to_send.write({'state': 'sent'})

    def action_send_new_items(self):
        # only lines that aren't on a ticket yet are sent, so pressing the button twice
        # sends nothing the second time
        to_send = self.filtered(lambda order: order.state in ('sent', 'preparing', 'ready'))
        for order in to_send:
            new_items = order.order_item_ids.filtered(lambda i: not i.is_ticketed)
            if new_items:
                # the new round's tickets start as 'new', so _compute_state moves the order
                # back to sent/preparing, and to ready once every ticket is ready
                order._send_items(new_items)

    def action_serve(self):
        if self.filtered(lambda order: order.state != 'ready'):
            raise UserError('Only orders that are Ready can be marked as served.')
        for order in self:
            unsent = order.order_item_ids.filtered(lambda i: not i.is_ticketed)
            if unsent:
                raise UserError(
                    "Some items haven't been sent to the kitchen yet: %s. Use 'Send New Items' first."
                    % ', '.join(unsent.mapped('menu_item_id.name'))
                )
        self.state = 'served'

    def action_bill(self):
        self.state = 'billed'

    def action_cancel(self):
        to_cancel = self.filtered(lambda order: order.state not in ('billed', 'cancelled'))
        for order in to_cancel:
            for item in order.order_item_ids.filtered(lambda i: i.is_ticketed):
                item.menu_item_id.sudo().stock_qty += item.quantity
            order.ticket_ids.filtered(lambda t: t.state != 'cancelled').write({'state': 'cancelled'})
        to_cancel.write({'state': 'cancelled'})

    def unlink(self):
        if self.filtered(lambda order: order.state != 'draft'):
            raise UserError('Only draft orders can be deleted.')
        return super().unlink()
