from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_rechargeable = fields.Boolean(string="Rechargeable")
