from odoo import api, fields, models


class BalanceHistory(models.Model):
    _name = "balance.history"
    _description = "Balance History"
    _rec_name = "partner_id"

    @api.depends("debit", "credit")
    def _compute_balance(self):
        for line in self:
            line.balance = line.credit - line.debit

    partner_id = fields.Many2one("res.partner", string="Customer")
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    debit = fields.Float(string="Debit")
    credit = fields.Float(string="Credit")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one(
        related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True)
    balance = fields.Monetary(
        compute="_compute_balance", currency_field="company_currency_id",
        store=True, string='Balance')

