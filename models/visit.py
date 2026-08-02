from odoo import fields, models, api


class VisitMesa(models.Model):
    _name = 'mesa.visit'
    _description = 'Visit Mesa'

    time_opened = fields.Datetime(string='Time Opened', required=True)
    time_closed = fields.Datetime(string='Time Closed', required=True)
