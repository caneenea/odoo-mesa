from odoo import fields, models, api


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

    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity > 0)', 'Quantity must be positive.'),
    ]

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
