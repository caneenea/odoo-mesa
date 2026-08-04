from odoo import fields, models, api


class ReservationMesa(models.Model):
    _name = 'mesa.reservation'
    _description = 'Reservation Mesa'

    reservation_name = fields.Char(string='Reservation Name', required=True)
    reservation_time = fields.Datetime(string='Reservation Time', required=True)
    party_size = fields.Char(string='Party Size', required=True)
