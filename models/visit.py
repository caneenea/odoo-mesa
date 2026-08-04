from odoo import fields, models, api


class VisitMesa(models.Model):
    _name = 'mesa.visit'
    _description = 'Visit Mesa'

    time_opened = fields.Datetime(string='Time Opened', required=True)
    time_closed = fields.Datetime(string='Time Closed', required=True)

    payment_ids = fields.One2many("mesa.payment","visit_id",string="Payment IDs")
    order_ids = fields.One2many("mesa.order","visit_id",string="Order IDs")
