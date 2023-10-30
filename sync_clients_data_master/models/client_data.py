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
    description = fields.Char("Description")
    partner_company = fields.Char("Partner Company")
    user_company = fields.Char("User Company")
    amount_charged = fields.Float("Charged Amount")
    res_model = fields.Char()
    date = fields.Date(tracking=True)
    remote_server_id = fields.Many2one("remote.server", "Remote Server")
    is_paid = fields.Boolean("Paid")
    balance_history_id = fields.Many2one("balance.history", string="Charges Reference")
    product_id = fields.Many2one("product.product", string="Product")
