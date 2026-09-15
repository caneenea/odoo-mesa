from odoo import fields, models, api


class PaymentMesa(models.Model):
    _name = 'mesa.payment'
    _description = 'Payment Mesa'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    amount = fields.Float(string='Amount', required=True, help="Amount paid, tip excluded.",
                           default=lambda self: self._default_amount())
    tip = fields.Float(string='Tip', help="Gratuity left on top of the amount, if any.")
    visit_id = fields.Many2one('mesa.visit', string='Visit', required=True, ondelete='cascade')
    guest_id = fields.Many2one('mesa.guest', string='Paid By', required=False, help="Guest who made this payment, for split billing across a visit.")
    method = fields.Selection(string="Method", required=True, selection=[
        ('cash', 'Cash'),
        ('card', 'Card'),
    ])

    _order = 'visit_id'

    _sql_constraints = [
        ('amount_positive', 'CHECK(amount >= 0)', 'Amount must be positive.'),
        ('tip_positive', 'CHECK(tip >= 0)', 'Tip must be positive.'),
    ]

    def _default_amount(self):
        visit_id = self.env.context.get('default_visit_id')
        if visit_id:
            return self.env['mesa.visit'].browse(visit_id).balance_due
        return 0.0

    @api.onchange('visit_id')
    def _onchange_visit_id(self):
        if self.visit_id:
            self.amount = self.visit_id.balance_due

    @api.depends('amount', 'method')
    def _compute_name(self):
        method_labels = dict(self._fields['method'].selection)
        for payment in self:
            method_label = method_labels.get(payment.method)
            if method_label:
                payment.name = "%.2f (%s)" % (payment.amount, method_label)
            else:
                payment.name = "%.2f" % payment.amount




