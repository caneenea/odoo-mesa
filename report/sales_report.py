from odoo import models, api


def _sales_domain_and_title(env, data):
    """Order lines sold in the wizard's date range, optionally limited to some menu items.
    'Sold' means the order went to the kitchen: draft and cancelled orders are left out."""
    domain = [
        ('order_id.time', '>=', data['start_date']),
        # the end date is included: everything up to the last second of that day
        ('order_id.time', '<=', '%s 23:59:59' % data['end_date']),
        ('order_id.state', 'not in', ('draft', 'cancelled')),
    ]
    if not data['menu_item_ids']:
        title = 'All menu items'
    else:
        domain.append(('menu_item_id', 'in', data['menu_item_ids']))
        names = env['mesa.menu_item'].browse(data['menu_item_ids']).mapped('name')
        title = 'Menu items: %s' % ', '.join(names)
    title += ' | %s to %s' % (data['start_date'], data['end_date'])
    return domain, title


# Report models must be named 'report.' + the report action's report_name, and model names must be
# lowercase. The module folder is 'Mesa', so report_name uses a lowercase 'mesa.' prefix and each
# template sets key="mesa.<id>" so Odoo can still find it (it looks templates up by key first).
class SalesLinesReport(models.AbstractModel):
    _name = 'report.mesa.report_sales_lines'
    _description = 'Sales Lines Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain, title = _sales_domain_and_title(self.env, data)
        order_items = self.env['mesa.order_item'].search(domain)

        lines = []
        for item in order_items:
            lines.append({
                'date': item.order_id.time,
                'visit': item.order_id.visit_id.name,
                'menu_item': item.menu_item_id.name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.total,
            })
        return {
            'docs': lines,
            'report_name': title,
        }


class SalesByItemReport(models.AbstractModel):
    _name = 'report.mesa.report_sales_by_item'
    _description = 'Sales Totals per Menu Item Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain, title = _sales_domain_and_title(self.env, data)
        order_items = self.env['mesa.order_item'].search(domain)

        # one entry per menu item, adding up every line that sold it
        totals = {}
        for item in order_items:
            if item.menu_item_id.id in totals:
                totals[item.menu_item_id.id]['quantity'] += item.quantity
                totals[item.menu_item_id.id]['revenue'] += item.total
            else:
                totals[item.menu_item_id.id] = {
                    'menu_item': item.menu_item_id.name,
                    'quantity': item.quantity,
                    'revenue': item.total,
                }
        return {
            'docs': totals,
            'report_name': title,
        }
