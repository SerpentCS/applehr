from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    move_type = fields.Selection(selection_add=[("in_invoice", "Bill")])
    payment_mode = fields.Selection([
        ("cash", "Cash"),
        ("chequa", "Chequa"),
        ("online", "Online"),
    ], default="cash", string="Payment Mode")
    bank_name = fields.Char(string="Bank Name")
    chequa_no = fields.Char(string="Chequa No#")
    issue_date = fields.Date(string="Issue Date")
    online_id = fields.Char(string="Online Id")
    transection_id = fields.Char(string="Transection Id")

    def action_post(self):
        # add balance for selected customer.
        res = super(AccountMove, self).action_post()
        if self.move_type == 'out_invoice':
            balance_values = {
                'description': 'Balance added',
                'partner_id': self.partner_id.id,
                'credit': self.amount_untaxed,
                'debit': 0.0,
                'date': fields.Date.today(),
            }
            self.env['balance.history'].create(balance_values)
            self.partner_id.balance += self.amount_untaxed
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    remote_server_id = fields.Many2one("remote.server", string="Service")
