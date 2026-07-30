from odoo import fields, models, api


class MesaEmployee(models.Model):
    _name = 'mesa.employee'
    _description = 'Mesa Employee'

    name = fields.Char(string="Name", required=True)
    surname = fields.Char(string="Surname", required=True)
    birth_date = fields.Date(string="Birth Date", required=True)
    salary = fields.Float(string="Salary", required=True)
    phone = fields.Char(string="Phone", required=True)
    hire_date = fields.Date(string="Hire Date", required=True)
    last_date = fields.Date(string="Last Date", required=False)
    email = fields.Char(string="Email", required=False)
    address = fields.Char(string="Address", required=False)

    position_id = fields.Many2one(
        'mesa.position',
        string='Position',
        required=True,
        ondelete='restrict'
    )

