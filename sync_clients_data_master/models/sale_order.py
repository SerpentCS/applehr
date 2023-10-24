from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # Set validation if multi product with rechargeable in SO lines.
        for rec in self:
            if len(rec.order_line) > 1:
                if any(line.product_id.is_rechargeable for line in rec.order_line) and any(not line.product_id.is_rechargeable for line in rec.order_line):
                    raise ValidationError((
                        "You can not add both rechargeable and non rechargeable product in order lines!"))
        # Deduction amount in customer balance history.
        for coupon, change in self.filtered(lambda s: s.state != 'sale')._get_point_changes().items():
            balance_values = {
                'description': 'Pay using eWallet',
                'partner_id': coupon.partner_id.id,
                'credit': 0.0,
                'debit': abs(change),
                'date': fields.Date.today(),
            }
            new_balance_rec = self.env['balance.history'].create(balance_values)
            coupon.partner_id.balance += change
            new_balance_rec.write({
                'closing_balance': coupon.partner_id.balance
            })
        return super().action_confirm()


    def _action_cancel(self):
        # Add refund in customer balance history.
        previously_confirmed = self.filtered(lambda s: s.state in ('sale', 'done'))
        for coupon, changes in previously_confirmed._get_point_changes().items():
            balance_values = {
                'description': 'Order cancelled refund',
                'partner_id': coupon.partner_id.id,
                'credit': abs(changes),
                'debit': 0.0,
                'date': fields.Date.today(),
            }
            new_balance_rec = self.env['balance.history'].create(balance_values)
            coupon.partner_id.balance += abs(changes)
            new_balance_rec.write({
                'closing_balance': coupon.partner_id.balance
            })
        return super()._action_cancel()
