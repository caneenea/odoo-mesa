from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ShiftMesa(models.Model):
    _name = 'mesa.shift'
    _description = 'Employee Shift'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    employee_id = fields.Many2one('mesa.employee', string='Employee', required=True, ondelete='cascade')
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=False, help="Left empty while the shift is still ongoing.")

    _order = 'start_time desc'

    _sql_constraints = [
        ('end_after_start', 'CHECK(end_time IS NULL OR end_time > start_time)', 'The shift must end after it starts.'),
    ]

    @api.depends('employee_id.name', 'employee_id.surname', 'start_time')
    def _compute_name(self):
        for shift in self:
            time_str = shift.start_time.strftime('%m/%d %H:%M') if shift.start_time else 'No Time'
            employee_label = shift.employee_id.display_name if shift.employee_id else 'Unassigned'
            shift.name = "%s - %s" % (employee_label, time_str)

    @api.constrains('employee_id', 'start_time', 'end_time')
    def _check_shift(self):
        for shift in self:
            employee = shift.employee_id
            start_date = shift.start_time.date()
            if employee.hire_date and start_date < employee.hire_date:
                raise ValidationError('%s was not hired yet on %s.' % (employee.full_name, start_date))
            if employee.last_date and start_date > employee.last_date:
                raise ValidationError('%s no longer works here on %s.' % (employee.full_name, start_date))
