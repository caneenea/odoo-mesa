from odoo import fields, models, api


class ReservationMesa(models.Model):
    _name = 'mesa.reservation'
    _description = 'Reservation Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    guest_id = fields.Many2one('mesa.guest', string='Guest', required=False, help="Linked guest record, if this reservation belongs to a known guest.")
    guest_name = fields.Char(string='Reservation Name', required=False, help="Name to book under when there is no linked guest record, e.g. a phone booking.")
    reservation_time = fields.Datetime(string='Reservation Time', required=True)
    party_size = fields.Integer(string='Party Size', required=True, help="Number of guests expected.")

    visit_ids = fields.One2many('mesa.visit', 'reservation_id', string='Visits')

    _order = 'reservation_time'

    @api.depends('guest_id.name', 'guest_id.surname', 'guest_name', 'reservation_time')
    def _compute_name(self):
        for reservation in self:
            time_str = reservation.reservation_time.strftime('%m/%d %H:%M') if reservation.reservation_time else 'No Time'
            guest_label = reservation.guest_id.display_name if reservation.guest_id else reservation.guest_name
            if guest_label:
                reservation.name = "%s - %s" % (guest_label, time_str)
            else:
                reservation.name = "Reservation - %s" % time_str

