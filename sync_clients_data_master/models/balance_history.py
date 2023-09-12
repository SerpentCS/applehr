from odoo import api, fields, models
import calendar
import logging
from datetime import datetime
from itertools import groupby
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

_logger = logging.getLogger(__name__)


class BalanceHistory(models.Model):
    _name = "balance.history"
    _description = "Balance History"
    _rec_name = "partner_id"
    _order = "date desc"

    @api.depends("debit", "credit")
    def _compute_balance(self):
        for line in self:
            line.balance = line.credit - line.debit
            line.customer_balance()

    partner_id = fields.Many2one("res.partner", string="Customer")
    product_id = fields.Many2one("product.product", string="Product")
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
    closing_balance = fields.Float(string='Closing Balance')
    invoice_id = fields.Many2one('account.move', string="Invoice Reference")

    def customer_balance(self):
        partner = self.partner_id
        for server in partner.remote_servers_ids:
            user_balance_partner = self.partner_id.balance

            if server:
                addr = server.url
                userid = server.user
                password = server.password
                dbname = server.dbname
                try:
                    common_2 = xmlrpclib.ServerProxy(
                        '{}/xmlrpc/2/common'.format(addr))
                    model_2 = xmlrpclib.ServerProxy(
                        '{}/xmlrpc/2/object'.format(addr))
                    odoo_10 = common_2.authenticate(
                        dbname, userid, password, {})
                except Exception as e:
                    _logger.warning(
                        "Could not authenticate user on the remote server: %s", e)
                    continue
                try:
                    logs_data = model_2.execute_kw(dbname, odoo_10, password, 'customer.balance', 'search_read',
                                                   [[('name', '=', 'customer_balance')]], {'fields': ["balance"]})

                    for line in logs_data:
                        new_data = model_2.execute_kw(dbname, odoo_10, password, 'customer.balance', 'write',
                                                      [line['id'], {'balance': user_balance_partner}])
                except Exception as e:
                    _logger.warning(
                        "Could not retrieve or update data from the client server: %s", e)
                    continue
        return True
