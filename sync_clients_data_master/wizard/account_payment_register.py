from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        # add rechargeable balance for selected customer.
        if self._context.get('active_model') == 'account.move':
            move_rec = self.env['account.move'].browse(self._context.get('active_ids', []))
            for move in move_rec.filtered(lambda line: line.move_type == 'out_invoice'):
                if all(line.product_id.is_rechargeable for line in move.invoice_line_ids):
                    balance_values = {
                        'description': 'Balance added',
                        'partner_id': move.partner_id.id,
                        'credit': move.amount_untaxed,
                        'debit': 0.0,
                        'date': fields.Date.today(),
                    }
                    new_balance_rec = self.env['balance.history'].create(balance_values)
                    move.partner_id.balance += move.amount_untaxed
                    new_balance_rec.write({
                        'closing_balance': move.partner_id.balance
                    })
        return super().action_create_payments()
