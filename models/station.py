from odoo import fields, models, api


class StationMesa(models.Model):
    _name = 'mesa.station'
    _description = 'Station Mesa'
    _rec_name = 'type'

    type = fields.Selection(string='Station Type', required=True, help="Kitchen station this record represents.", selection=[
        ('pantry', 'Pantry'),
        ('saute', 'Saute'),
        ('broil', 'Broil'),
        ('dessert', 'Dessert'),
        ('expeditor', 'Expeditor'),
    ])

    menu_item_ids = fields.One2many('mesa.menu_item', 'station_id', string='Menu Items')

    _order = 'type'
