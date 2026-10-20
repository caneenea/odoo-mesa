from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SalesReportWizard(models.TransientModel):
    _name = 'mesa.sales.report.wizard'
    _description = 'Sales Report Wizard'

    menu_item_ids = fields.Many2many('mesa.menu_item', string='Menu Items',
                                     help="Leave empty to include every menu item.")
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True,
                           help="Included: orders placed on this day are part of the report.")

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for wizard in self:
            if wizard.end_date < wizard.start_date:
                raise ValidationError('The end date can not be before the start date.')

    def print_sales_lines(self):
        self.ensure_one()
        data = {
            "menu_item_ids": self.menu_item_ids.ids,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        return self.env.ref('Mesa.action_report_sales_lines').report_action(None, data=data)

    def print_sales_by_item(self):
        self.ensure_one()
        data = {
            "menu_item_ids": self.menu_item_ids.ids,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        return self.env.ref('Mesa.action_report_sales_by_item').report_action(None, data=data)
