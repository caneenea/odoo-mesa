from odoo import fields, models, api


class MesaEmployee(models.Model):
    _name = 'mesa.employee'
    _description = 'Mesa Employee'
    _rec_name = 'full_name'

    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)
    name = fields.Char(string="Name", required=True)
    surname = fields.Char(string="Surname", required=True)
    birth_date = fields.Date(string="Birth Date", required=True)
    salary = fields.Float(string="Salary", required=True, help="Employee's base salary.")
    phone = fields.Char(string="Phone", required=True)
    hire_date = fields.Date(string="Hire Date", required=True)
    last_date = fields.Date(string="Last Date", required=False, help="Date employment ended. Leave empty while the employee is still active.")
    email = fields.Char(string="Email", required=False)
    address = fields.Char(string="Address", required=False)

    position_id = fields.Many2one(
        'mesa.position',
        string='Position',
        required=True,
        ondelete='restrict',
        help="Job position held by this employee."
    )

    visit_ids = fields.One2many('mesa.visit', 'server_id', string='Visits')
    shift_ids = fields.One2many('mesa.shift', 'employee_id', string='Shifts')

    _order = 'surname, name'

    @api.depends('name', 'surname')
    def _compute_full_name(self):
        for employee in self:
            employee.full_name = ("%s %s" % (employee.name or '', employee.surname or '')).strip()

