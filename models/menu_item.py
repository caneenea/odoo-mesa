from odoo import fields, models, api


class MenuItemMesa(models.Model):
    _name = 'mesa.menu_item'
    _description = 'Menu Item Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price', required=True)
    order_item_ids = fields.One2many(
        "mesa.order_item",
         "menu_item_id",
              string="Order Items",
    )


