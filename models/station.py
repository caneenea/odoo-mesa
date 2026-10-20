from odoo import fields, models, api


class StationMesa(models.Model):
    _name = 'mesa.station'
    _description = 'Station Mesa'
    _rec_name = 'type'
    _order = 'type'


    type = fields.Selection(string='Station Type', required=True, help="Kitchen station this record represents.", selection=[
        ('pantry', 'Pantry'),
        ('saute', 'Saute'),
        ('broil', 'Broil'),
        ('dessert', 'Dessert'),
        ('expeditor', 'Expeditor'),
    ])

    menu_item_ids = fields.Many2many(
        'mesa.menu_item',
        'mesa_menu_item_station_rel',
        'station_id',
        'menu_item_id',
        string='Menu Items',
    )
    employee_ids = fields.Many2many(
        'mesa.employee',
        'mesa_employee_station_rel',
        'station_id',
        'employee_id',
        string='Employees',
        help="Employees who can work this station."
    )

    _sql_constraints = [
        ('type_uniq', 'UNIQUE(type)', 'A station of this type already exists.'),
    ]

