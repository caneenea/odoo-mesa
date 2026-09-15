from odoo import fields, models, api


class MenuCategoryMesa(models.Model):
    _name = 'mesa.menu_category'
    _description = 'Menu Category'

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description', required=False)

    _order = 'name'
