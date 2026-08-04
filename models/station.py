from odoo import fields, models, api


class StationMesa(models.Model):
    _name = 'mesa.station'
    _description = 'Station Mesa'

    type = fields.Selection(string='Type', required=True, selection=[('pantry','Pantry'),
                                                                     ('saute','Saute'),
                                                                     ('broil','Broil'),
                                                                     ('dessert','Dessert'),
                                                                     ('expeditor','Expeditor')])
