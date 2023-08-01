from odoo import fields, models


class ClientData(models.Model):
    _name = "client.data"
    _description = "Manage Client Billing Data"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "emp_name"

    partner_id = fields.Many2one(
        "res.partner", "Customer", ondelete="cascade", copy=False, index=True
    )
    emp_name = fields.Char("Employee")
    emp_code = fields.Char("Spequa ID")
    partner_company = fields.Char()
    res_model = fields.Char()
    date = fields.Date(tracking=True)
    remote_server_id = fields.Many2one("remote.server", "Remote Server")
    is_paid = fields.Boolean("Paid")
    is_one_time_charges = fields.Boolean("One Time Charges")
    balance_history_id = fields.Many2one("balance.history", string="Charges Reference")
