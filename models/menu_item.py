from odoo import fields, models, api


class MenuItemMesa(models.Model):
    _name = 'mesa.menu_item'
    _description = 'Menu Item Mesa'
    _rec_name = 'name'
    _order = 'name'


    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price', required=True, help="Selling price of this menu item.")
    order_item_ids = fields.One2many(
        "mesa.order_item",
        "menu_item_id",
        string="Order Items",
    )

    category_ids = fields.Many2many('mesa.menu_category', string='Categories')
    station_ids = fields.Many2many(
        'mesa.station',
        'mesa_menu_item_station_rel',
        'menu_item_id',
        'station_id',
        string='Stations',
        help="Kitchen stations that need to prepare part of this item."
    )
    stock_qty = fields.Float(string='Stock Quantity', default=0, help="Quantity currently in stock.")


    _sql_constraints = [
        ('stock_qty_non_negative', 'CHECK(stock_qty >= 0)', 'Stock quantity can not be negative.'),
        ('price_positive', 'CHECK(price > 0)', 'Price must be greater than 0.'),
    ]


