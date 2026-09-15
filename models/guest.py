from odoo import fields, models, api


class GuestMesa(models.Model):
    _name = 'mesa.guest'
    _description = 'Mesa Guest'
    _rec_name = 'full_name'

    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)
    name = fields.Char(string='Name', required=True)
    surname = fields.Char(string='Surname', required=True)
    birth_date = fields.Date(string='Birth Date', required=True)
    regular = fields.Boolean(string='Regular Guest', default=False, help="Marks a guest who visits often.")
    preferred_location = fields.Selection(string='Preferred Location', required=True,
                                           selection=[('inside', 'Inside'), ('porch', 'Porch'), ('fountain', 'Fountain')],
                                           help="Seating area this guest prefers when a table is available.")
    notes = fields.Text(string='Notes', required=False, help="Allergies, preferences, or other useful notes about this guest.")
    reservation_ids = fields.One2many("mesa.reservation", "guest_id", string="Reservations")
    points = fields.Float(string='Loyalty Points', default=0, help="Accumulated loyalty points for this guest.")

    _order = 'surname, name'

    @api.depends('name', 'surname')
    def _compute_full_name(self):
        for guest in self:
            guest.full_name = ("%s %s" % (guest.name or '', guest.surname or '')).strip()
