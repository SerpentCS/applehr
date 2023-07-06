# -*- coding: utf-8 -*-

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.exceptions import UserError


class WebsiteSaleDelivery(WebsiteSale):

    @http.route()
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        if order:
            order._check_balance_quotation()
        return super(WebsiteSaleDelivery, self).shop_payment(**post)

    @http.route(['/shop/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        if order:
            if any(tx.state not in ("cancel", "error", "draft") for tx in order.transaction_ids):
                raise UserError(_('It seems that there is already a transaction for your order, you can not change the delivery method anymore'))
            order._check_balance_quotation()
        return super(WebsiteSaleDelivery, self).update_eshop_carrier(**post)

    @http.route()
    def cart(self, **post):
        order = request.website.sale_get_order()
        if order:
            order._remove_balance_line()
        return super().cart(**post)

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                # Retrieve the last known order from the session if the session key `sale_order_id`
                # was prematurely cleared. This is done to prevent the user from updating their cart
                # after payment in case they don't return from payment through this route.
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        tx = order.get_portal_last_transaction() if order else order.env['payment.transaction']

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            total_amount = 0
            for line in order.order_line:
                if line.is_balance:
                    total_amount = total_amount + abs(line.price_total)
            balance_values = {
                'description': 'Balance Debited',
                'partner_id': order.partner_id.id,
                'credit': 0.0,
                'debit': total_amount,
                'date': fields.Date.today(),
            }
            request.env['balance.history'].sudo().create(balance_values)
            order.partner_id.balance = order.partner_id.balance - total_amount
            request.website.sale_reset()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentPostProcessing.remove_transactions(tx)
        return request.redirect('/shop/confirmation')

