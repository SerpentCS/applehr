# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def set_balance_line(self):
        self._remove_balance_line()
        for order in self:
            if order.partner_id and order.partner_id.balance > 0:
                qty = 0
                price = 0
                for line in self.order_line:
                    if not line.is_balance and not line.is_delivery:
                        qty = qty + line.product_uom_qty
                        price = price + line.price_unit
                SaleOrderLine = self.env['sale.order.line']
                # Create the sales order line
                so_description = "Balance Line"
                values = {
                    'order_id': order.id,
                    'name': so_description,
                    'product_uom_qty': qty,
                    'product_uom': request.website.product_id.uom_id.id,
                    'product_id':request.website.product_id.id,
                    'price_unit': -price,
                    'is_balance': True,
                }
                if self.order_line:
                    values['sequence'] = self.order_line[-1].sequence + 1
                SaleOrderLine.sudo().create(values)
        return True

    def _check_balance_quotation(self):
        self.ensure_one()
        self.set_balance_line()
        return True

    def _cart_update(self, *args, **kwargs):
        """ Override to update carrier quotation if quantity changed """
        self._remove_balance_line()
        return super()._cart_update(*args, **kwargs)

    def _remove_balance_line(self):
        delivery_lines = self.order_line.filtered("is_balance")
        if not delivery_lines:
            return
        to_delete = delivery_lines.filtered(lambda x: x.qty_invoiced == 0)
        if not to_delete:
            raise UserError(
                _('You can not update the shipping costs on an order where it was already invoiced!\n\nThe following delivery lines (product, invoiced quantity and price) have already been processed:\n\n')
                + '\n'.join(['- %s: %s x %s' % (line.product_id.with_context(display_default_code=False).display_name, line.qty_invoiced, line.price_unit) for line in delivery_lines])
            )
        to_delete.unlink()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_balance = fields.Boolean(string="Is a Balance", default=False)
