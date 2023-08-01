from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        # Set validation for both rechargeable and non rechargeable product in invoice line.
        for rec in self:
            if len(rec.invoice_line_ids) > 1:
                if any(line.product_id.is_rechargeable for line in rec.invoice_line_ids) and any(
                        not line.product_id.is_rechargeable for line in rec.invoice_line_ids):
                    raise ValidationError((
                        "You can not add both rechargeable and non rechargeable product in invoice lines!"))
        return super().action_post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    remote_server_id = fields.Many2one("remote.server", string="Service")
