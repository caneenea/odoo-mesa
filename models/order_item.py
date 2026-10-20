from odoo import fields, models, api
from odoo.exceptions import UserError


class OrderItemMesa(models.Model):
    _name = 'mesa.order_item'
    _description = 'Order Item Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    price = fields.Float(string='Price', help="Unit price at the time this item was ordered.")
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    notes = fields.Text(string='Notes', required=False, help="Special preparation instructions for this line, e.g. \"no onions\".")

    menu_item_id = fields.Many2one(
        'mesa.menu_item',
        string="Menu Item",
        required=True,
        ondelete='cascade'
    )
    order_id = fields.Many2one(
        "mesa.order",
        string="Order",
        required=True,
        ondelete='restrict'
    )
    ticket_line_ids = fields.One2many(
        'mesa.kitchen.ticket.line',
        'order_item_id',
        string='Kitchen Ticket Lines',
        help="One entry per station this line was sent to."
    )
    is_ticketed = fields.Boolean(string='Sent to Kitchen', compute='_compute_is_ticketed', store=True)

    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity > 0)', 'Quantity must be positive.'),
        ('price_non_negative', 'CHECK(price >= 0)', 'Price can not be negative.'),
    ]

    @api.model
    def create(self, values):
        if values.get('order_id'):
            order = self.env['mesa.order'].browse(values['order_id'])
            if order.state in ('served', 'billed', 'cancelled'):
                raise UserError(
                    "You can't add items to an order that is served, billed or cancelled. Start a new order instead."
                )
        if not values.get('price') and values.get('menu_item_id'):
            values['price'] = self.env['mesa.menu_item'].browse(values['menu_item_id']).price
        return super().create(values)

    @api.onchange('menu_item_id')
    def _onchange_menu_item_id(self):
        if self.menu_item_id:
            self.price = self.menu_item_id.price

    @api.depends('quantity', 'price')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.price

    @api.depends('quantity', 'menu_item_id.name')
    def _compute_name(self):
        for line in self:
            if line.menu_item_id:
                line.name = "%sx %s" % (line.quantity, line.menu_item_id.name)
            else:
                line.name = "Order Item"

    @api.depends('ticket_line_ids')
    def _compute_is_ticketed(self):
        for line in self:
            line.is_ticketed = bool(line.ticket_line_ids)

    def unlink(self):
        if self.filtered(lambda line: line.ticket_line_ids):
            raise UserError('This line has already been sent to the kitchen and can not be deleted.')
        return super().unlink()
