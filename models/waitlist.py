from odoo import fields, models, api
from odoo.exceptions import ValidationError


class WaitlistMesa(models.Model):
    _name = 'mesa.waitlist'
    _description = 'Waitlist'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    guest_id = fields.Many2one('mesa.guest', string='Guest', required=False)
    guest_name = fields.Char(string='Waitlist Name', required=False, help="Name to call when there is no linked guest record.")
    party_size = fields.Integer(string='Party Size', required=True)
    time_added = fields.Datetime(string='Time Added', required=True, default=lambda self: fields.Datetime.now())
    status = fields.Selection(string='Status', required=True, default='waiting', selection=[
        ('waiting', 'Waiting'),
        ('seated', 'Seated'),
        ('cancelled', 'Cancelled'),
    ])
    table_id = fields.Many2one('mesa.table', string='Table', required=False, help="Table assigned once this party is seated.")

    _order = 'time_added'

    _sql_constraints = [
        ('party_size_positive', 'CHECK(party_size >= 1)', 'Party size must be at least 1.'),
    ]

    @api.constrains('guest_id', 'guest_name')
    def _check_guest(self):
        for waitlist in self:
            if not waitlist.guest_id and not waitlist.guest_name:
                raise ValidationError('Pick a guest or fill in the waitlist name.')

    @api.depends('guest_id.name', 'guest_id.surname', 'guest_name', 'party_size')
    def _compute_name(self):
        for waitlist in self:
            guest_label = waitlist.guest_id.display_name if waitlist.guest_id else (waitlist.guest_name or 'Waitlist')
            waitlist.name = "%s (%s)" % (guest_label, waitlist.party_size)
