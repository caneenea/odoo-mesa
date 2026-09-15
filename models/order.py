from odoo import fields, models, api
from odoo.exceptions import UserError


class OrderMesa(models.Model):
    _name = 'mesa.order'
    _description = 'Order Mesa'
    _rec_name = 'time'

    time = fields.Datetime(string='Time', required=True)
    status = fields.Selection([
        ('normal', 'Normal'),
        ('rush', 'Rush'),
    ], string='Status', required=True, default='normal', help="Kitchen priority for this order.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Kitchen'),
        ('served', 'Served'),
        ('billed', 'Billed'),
        ('cancelled', 'Cancelled'),
    ], string='State', required=True, default='draft', help="Workflow stage of this order.")
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    order_item_ids = fields.One2many("mesa.order_item", "order_id", string="Order Items")
    visit_id = fields.Many2one("mesa.visit", string="Visit", required=True, ondelete='cascade')

    _order = 'time desc'

    @api.depends('order_item_ids.total')
    def _compute_total(self):
        for order in self:
            order.total = sum(order.order_item_ids.mapped('total'))

    def action_send(self):
        self.state = 'sent'

    def action_serve(self):
        self.state = 'served'

    def action_bill(self):
        self.state = 'billed'

    def action_cancel(self):
        self.state = 'cancelled'

    def unlink(self):
        if self.filtered(lambda order: order.state != 'draft'):
            raise UserError('Only draft orders can be deleted.')
        return super().unlink()
