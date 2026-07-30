from odoo import fields, models, api


class PositionMesa(models.Model):
    _name = 'mesa.position'
    _description = 'Employee Position'
    _rec_name = 'title'

    title = fields.Selection(string='Title', required = True, selection = [('busser', 'Busser'),
                                                                           ('server', 'Server'),
                                                                           ('cook', 'Cook'),
                                                                           ('host', 'Host'),]
                             )
    base_pay = fields.Float(string = "Base Pay", required=True)
    department = fields.Char(string = "Department", required=True)

    employee_ids = fields.One2many(
        'mesa.employee',
        'position_id',
        string="Employees"
    )
