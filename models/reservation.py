from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class ReservationMesa(models.Model):
    _name = 'mesa.reservation'
    _description = 'Reservation Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    guest_id = fields.Many2one('mesa.guest', string='Guest', required=False, help="Linked guest record, if this reservation belongs to a known guest.")
    guest_name = fields.Char(string='Reservation Name', required=False, help="Name to book under when there is no linked guest record, e.g. a phone booking.")
    reservation_time = fields.Datetime(string='Reservation Time', required=True)
    party_size = fields.Integer(string='Party Size', required=True, help="Number of guests expected.")
    state = fields.Selection([
        ('booked', 'Booked'),
        ('seated', 'Seated'),
        ('cancelled', 'Cancelled'),
    ], string='State', required=True, default='booked')
    table_id = fields.Many2one('mesa.table', string='Table', required=False,
                               help="Table the party will be seated at. Needed before pressing Seat.")

    visit_ids = fields.One2many('mesa.visit', 'reservation_id', string='Visits')

    _order = 'reservation_time'

    _sql_constraints = [
        ('party_size_positive', 'CHECK(party_size >= 1)', 'Party size must be at least 1.'),
    ]

    @api.constrains('reservation_time')
    def _check_reservation_time(self):
        # only runs when the time is set or changed, so past reservations already in the system stay valid
        now = fields.Datetime.now()
        for reservation in self:
            if reservation.reservation_time < now:
                raise ValidationError('A reservation can not be made in the past.')

    @api.constrains('guest_id', 'guest_name')
    def _check_guest(self):
        for reservation in self:
            if not reservation.guest_id and not reservation.guest_name:
                raise ValidationError('Pick a guest or fill in the reservation name.')

    def action_seat(self):
        to_seat = self.filtered(lambda reservation: reservation.state == 'booked')
        for reservation in to_seat:
            if not reservation.table_id:
                raise UserError('Pick a table before seating this reservation.')
            # visit.create checks the table is free and marks it busy
            self.env['mesa.visit'].create({
                'table_id': reservation.table_id.id,
                'reservation_id': reservation.id,
            })
        to_seat.write({'state': 'seated'})

    def action_cancel(self):
        to_cancel = self.filtered(lambda reservation: reservation.state == 'booked')
        to_cancel.write({'state': 'cancelled'})

    @api.depends('guest_id.name', 'guest_id.surname', 'guest_name', 'reservation_time')
    def _compute_name(self):
        for reservation in self:
            time_str = reservation.reservation_time.strftime('%m/%d %H:%M') if reservation.reservation_time else 'No Time'
            guest_label = reservation.guest_id.display_name if reservation.guest_id else reservation.guest_name
            if guest_label:
                reservation.name = "%s - %s" % (guest_label, time_str)
            else:
                reservation.name = "Reservation - %s" % time_str

