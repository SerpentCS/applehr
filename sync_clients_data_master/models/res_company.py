from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    administrator_email = fields.Char('Administrator Email')
