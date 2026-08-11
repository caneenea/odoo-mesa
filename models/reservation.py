from odoo import fields, models, api


class ReservationMesa(models.Model):
    _name = 'mesa.reservation'
    _description = 'Reservation Mesa'

    guest_id = fields.Many2one('mesa.guest',string='Guest', required=False)
    guest_name = fields.Char(string='Reservation Name', required=False)
    reservation_time = fields.Datetime(string='Reservation Time', required=True)
    party_size = fields.Char(string='Party Size', required=True)

