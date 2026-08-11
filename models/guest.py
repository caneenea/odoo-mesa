from odoo import fields, models, api


class GuestMesa(models.Model):
    _name = 'mesa.guest'
    _description = 'Mesa Guest'

    name = fields.Char(string='Name', required=True)
    surname = fields.Char(string='Surname', required=True)
    birth_date = fields.Date(string='Birth Date', required=True)
    regular = fields.Boolean(string='Regular', required=True, default=False)
    preferred_location = fields.Selection(string= 'Preferred Location',required = True,selection = [('inside', 'Inside'),('porch', 'Porch'),('fountain', 'Fountain')])
    notes = fields.Text(string='Notes', required=False)
    reservation_ids = fields.One2many("mesa.reservation","guest_id",string="Reservations")
