from odoo import fields, models, api


class OrderMesa(models.Model):
    _name = 'mesa.order'
    _description = 'Order Mesa'

    time = fields.Datetime(string='Time', required=True)
    status = fields.Selection([
        ('normal', 'Normal'),
        ('rush','Rush')
    ])
