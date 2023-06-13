from odoo import fields, models


class SpequaCharges(models.Model):
    _name = "spequa.charges"
    _description = "Spequa Charges"
    _rec_name = "name"

    name = fields.Char(string="Description")
    partner_id = fields.Many2one("res.partner", string="Customer")
    amount = fields.Float(string="Amount")
    date = fields.Date(string="Date")
    state = fields.Selection([
        ("draft", "Draft"),
        ("waiting_for_approval", "Waiting for Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="State", default="draft")

    def action_send_for_approval(self):
        return self.write({
            'state': 'waiting_for_approval'
        })

    def action_approved(self):
        balance_values = {
            'description': self.name,
            'partner_id': self.partner_id.id,
            'credit': 0.0,
            'debit': self.amount,
            'date': self.date,
        }
        self.env['balance.history'].create(balance_values)
        self.partner_id.balance -= self.amount
        return self.write({
            'state': 'approved'
        })

    def action_reject(self):
        return self.write({
            'state': 'rejected'
        })

    def action_reset_to_draft(self):
        return self.write({
            'state': 'draft'
        })
