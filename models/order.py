from odoo import fields, models, api


class OrderMesa(models.Model):
    _name = 'mesa.order'
    _description = 'Order Mesa'
    _rec_name = 'time'

    time = fields.Datetime(string='Time', required=True)
    status = fields.Selection([
        ('normal', 'Normal'),
        ('rush','Rush')
    ])

    order_item_ids = fields.One2many("mesa.order_item","order_id", string="Order Items")
    visit_id = fields.Many2one("mesa.visit", string="Visit Items", required=True, ondelete='cascade')
