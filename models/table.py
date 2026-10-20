from odoo import fields, models, api


class TableMesa(models.Model):
    _name = 'mesa.table'
    _description = 'Table Mesa'
    _rec_name = 'table_num'

    table_num = fields.Char(string='Table Number', required=True)
    table_location = fields.Selection(string='Table Location', required=True, selection=[
        ('inside', 'Inside'),
        ('porch', 'Porch'),
        ('fountain', 'Fountain'),
    ])
    table_status = fields.Selection(string='Table Status', required=True, default='free', selection=[
        ('free', 'Free'),
        ('busy', 'Busy'),
        ('needs_cleaning', 'Needs Cleaning'),
    ])

    visit_ids = fields.One2many('mesa.visit', 'table_id', string='Visits')

    _order = 'table_num'

    _sql_constraints = [
        ('table_num_uniq', 'UNIQUE(table_num)', 'A table with this number already exists.'),
    ]

    def action_mark_clean(self):
        to_clean = self.filtered(lambda table: table.table_status == 'needs_cleaning')
        to_clean.write({'table_status': 'free'})


