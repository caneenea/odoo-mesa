from odoo import fields, models, api


class MenuItemMesa(models.Model):
    _name = 'mesa.menu_item'
    _description = 'Menu Item Mesa'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price', required=True)

