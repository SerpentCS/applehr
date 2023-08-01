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
        return super().action_confirm()
