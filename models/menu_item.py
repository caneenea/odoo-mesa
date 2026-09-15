from odoo import fields, models, api


class MenuItemMesa(models.Model):
    _name = 'mesa.menu_item'
    _description = 'Menu Item Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price', required=True, help="Selling price of this menu item.")
    order_item_ids = fields.One2many(
        "mesa.order_item",
        "menu_item_id",
        string="Order Items",
    )

    category_ids = fields.Many2many('mesa.menu_category', string='Categories')
    station_id = fields.Many2one('mesa.station', string='Station', required=False, help="Kitchen station that prepares this item.")
    stock_qty = fields.Float(string='Stock Quantity', default=0, help="Quantity currently in stock.")

    _order = 'name'


