from odoo import fields, models, api


class PaymentMesa(models.Model):
    _name = 'mesa.payment'
    _description = 'Payment Mesa'

    amount = fields.Float(string='Amount', required=True)
    tip = fields.Float(string='Tip')
    visit_id = fields.Many2one('mesa.visit',string='Visit', required=True, ondelete='cascade')
    method = fields.Selection(string = "Method",selection=[('cash','Cash'),
                                             ('card','Card')])




