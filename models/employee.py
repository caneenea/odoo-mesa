from odoo import fields, models, api
from odoo.exceptions import ValidationError


class MesaEmployee(models.Model):
    _name = 'mesa.employee'
    _description = 'Mesa Employee'
    _rec_name = 'full_name'
    _order = 'surname, name'


    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)
    name = fields.Char(string="Name", required=True)
    surname = fields.Char(string="Surname", required=True)
    birth_date = fields.Date(string="Birth Date", required=True)
    # not required: users outside the managers' group never see this field, so they could never fill it in
    salary = fields.Float(string="Salary", default=0.0, help="Employee's base salary. Only visible to Mesa Managers.",
                           groups='Mesa.group_mesa_manager')
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
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=False,
        help="Login account linked to this employee, used to restrict what a server can see."
    )

    visit_ids = fields.One2many('mesa.visit', 'server_id', string='Visits')
    shift_ids = fields.One2many('mesa.shift', 'employee_id', string='Shifts')
    station_ids = fields.Many2many(
        'mesa.station',
        'mesa_employee_station_rel',
        'employee_id',
        'station_id',
        string='Stations',
        help="Kitchen stations this employee can work, used to filter which kitchen tickets they see."
    )


    _sql_constraints = [
        ('salary_non_negative', 'CHECK(salary >= 0)', 'Salary can not be negative.'),
        ('user_uniq', 'UNIQUE(user_id)', 'This user is already linked to another employee.'),
    ]

    @api.depends('name', 'surname')
    def _compute_full_name(self):
        for employee in self:
            employee.full_name = ("%s %s" % (employee.name or '', employee.surname or '')).strip()

    @api.constrains('birth_date', 'hire_date', 'last_date')
    def _check_dates(self):
        today = fields.Date.today()
        for employee in self:
            if employee.birth_date and employee.hire_date:
                birth = employee.birth_date
                hire = employee.hire_date
                age_at_hire = hire.year - birth.year
                # birthday not reached yet in the hire year
                if hire.month < birth.month or (hire.month == birth.month and hire.day < birth.day):
                    age_at_hire -= 1
                if age_at_hire < 18:
                    raise ValidationError(
                        '%s would be %s on the hire date. Employees must be at least 18.'
                        % (employee.full_name, age_at_hire)
                    )
            if employee.hire_date and employee.hire_date > today:
                raise ValidationError('The hire date can not be in the future.')
            if employee.last_date and employee.hire_date and employee.last_date < employee.hire_date:
                raise ValidationError('The last date can not be before the hire date.')

