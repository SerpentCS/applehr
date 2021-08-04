import uuid
import psycopg2
import io
import ast

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib


class SyncClientDataLog(models.Model):
    _name = "sync.client.data.log"

    name = fields.Char("Resource Name")
    log_date = fields.Datetime('Log Date',
                               default=lambda self: fields.Datetime.now())
    res_id = fields.Integer("Resource ID")
    model_name = fields.Char("Model Name")
    method = fields.Char('Method')
    uuid = fields.Char("UUID")
    args = fields.Char("Args")
    remote = fields.Char("Remote")
    state = fields.Selection(
        [
            ("logged", "Logged"),
            ("Synced", "Synced"),
            ("Processed", "Processed"),
            ("Failed", "Failed"),
            ("Cancelled", "Cancelled"),
        ],
        string="State",
        default="logged",
    )
    remote_server_id = fields.Many2one('remote.server',
                                       'Remote Server',
                                       ondelete='cascade')
    _sql_constraints = [
        (
            "uuid_uniq",
            "unique(uuid)",
            (
                "This UUID already exists\n"
                "Record will be skipped to avoid duplication"
            ),
        )
    ]

    def _cron_log_auto_vacuum(self):
        current_date = fields.Datetime.from_string(fields.Datetime.now())
        one_month_before_date = current_date + relativedelta(months=-1)
        all_log_datas = self.env['sync.client.data.log'].search([
                ('log_date', '<', one_month_before_date),
                ('state', 'in', ['Synced', 'Processed'])
        ])
        all_log_datas.unlink()
