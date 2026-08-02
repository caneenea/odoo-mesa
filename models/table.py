from odoo import fields, models, api


class TableMesa(models.Model):
    _name = 'mesa.table'
    _description = 'Table Mesa'

    table_num = fields.Char(string='Table Number', required=True)
    table_location = fields.Selection(string='Table Location', required=True,selection = [('inside', 'Inside'),
                                                                              ('porch', 'Porch'),
                                                                              ('fountain', 'Fountain')])
    table_status = fields.Selection(string='Table Status', required=True,  selection=[('free', 'Free' ),
                                                                                     ('busy', 'Busy'),
                                                                                     ('needs_cleaning', 'Needs Cleaning'),],
     )


