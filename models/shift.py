from odoo import fields, models, api


class ShiftMesa(models.Model):
    _name = 'mesa.shift'
    _description = 'Employee Shift'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    employee_id = fields.Many2one('mesa.employee', string='Employee', required=True, ondelete='cascade')
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=False, help="Left empty while the shift is still ongoing.")

    _order = 'start_time desc'

    @api.depends('employee_id.name', 'employee_id.surname', 'start_time')
    def _compute_name(self):
        for shift in self:
            time_str = shift.start_time.strftime('%m/%d %H:%M') if shift.start_time else 'No Time'
            employee_label = shift.employee_id.display_name if shift.employee_id else 'Unassigned'
            shift.name = "%s - %s" % (employee_label, time_str)
