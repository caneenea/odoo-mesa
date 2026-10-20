from odoo import fields, models


class KitchenTicketLineMesa(models.Model):
    _name = 'mesa.kitchen.ticket.line'
    _description = 'Kitchen Ticket Line'

    ticket_id = fields.Many2one('mesa.kitchen.ticket', string='Ticket', required=True, ondelete='cascade')
    order_item_id = fields.Many2one('mesa.order_item', string='Order Line', required=True, ondelete='cascade')
    quantity = fields.Integer(string='Quantity', required=True,
                               help="Snapshot of the order line's quantity when this ticket was created.")
    done = fields.Boolean(string='Done', default=False)

    _sql_constraints = [
        ('ticket_order_item_uniq', 'UNIQUE(ticket_id, order_item_id)', 'This order line is already on this ticket.'),
    ]
