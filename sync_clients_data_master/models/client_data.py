
from odoo import _, api, fields, models, modules
import uuid, copy

from datetime import datetime


class ClientData(models.Model):
    _name = "client.data"
    _descripation = "Manage Client Billing Data"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "emp_name"

    partner_id = fields.Many2one('res.partner', 'Customer',
                                 ondelete="cascade",
                                 copy=False,
                                 index=True)
    emp_name = fields.Char('Employee Name')
    res_id = fields.Char('Res ID')
    res_model = fields.Char('Res Model')
    date_start = fields.Date('Start Date', tracking=True)
    date_end = fields.Date('Ending Date', tracking=True)
    active = fields.Boolean('Status', tracking=True)
