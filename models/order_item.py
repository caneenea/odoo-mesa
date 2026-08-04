from odoo import fields, models, api


class OrderItemMesa(models.Model):
    _name = 'mesa.order_item'
    _description = 'Order Item Mesa'

    quantity = fields.Integer(string='Quantity', required=True)
    notes = fields.Text(string='Notes', required=False)

    menu_item_id = fields.Many2one(
        'mesa.menu_item',
        string="Order Item",
        required=True,
        ondelete='cascade'

    )
    order_id = fields.Many2one(
        "mesa.order",
        string="Order",
        required=True,
        ondelete='restrict'
    )
