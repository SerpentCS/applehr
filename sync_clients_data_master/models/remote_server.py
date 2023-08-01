import calendar
import logging
from datetime import datetime
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

_logger = logging.getLogger(__name__)


class RemoteServer(models.Model):
    _name = "remote.server"
    _description = "Remote Server"
    _rec_name = "name"

    name = fields.Char(required=1)
    url = fields.Char("Server Url", required=1)
    user = fields.Char(required=1)
    password = fields.Char(required=1)
    dbname = fields.Char("Database", required=1)
    partner_id = fields.Many2one(
        "res.partner", "Customer", ondelete="cascade", copy=False
    )
    date_sync = fields.Datetime(string="Last Sync Date", default=datetime.now())
    rate = fields.Float()
    start_date = fields.Date(string="Start Date")

    def _fetch_client_log_data(self, server):
        log_datas = []
        if server:
            addr = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
        try:
            uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr)).authenticate(
                dbname, userid, password, {}
            )
        except:
            _logger.warning("Could not authenticate user on the remote server")
        try:
            log_datas = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname,
                uid,
                password,
                "partner.work.history",
                "search_read",
                ([
                    ('employee_id', '!=', False),
                    ('join_date', '<=', self.start_date),
                    '|',
                    ('end_date', '>=', fields.Date.today()),
                    ('end_date', '=', False)
                ]),
                ["partner_company_id", "employee_id", "emp_code"],
            )
        except:
            _logger.warning("Could not retrieve data from client server")
        employee_data = []
        for logdata in log_datas:
            vals = {
                "partner_id": self.partner_id.id,
                "emp_name": logdata.get("employee_id")[1],
                "res_model": "hr.employee",
                "emp_code": logdata.get("emp_code"),
                "partner_company": logdata.get("partner_company_id")[1]
                if logdata.get("partner_company_id")
                else "",
                "date": fields.Date.today(),
                "remote_server_id": self.id,
            }
            client_data_rec = self.env["client.data"].search(
                [
                    ("date", "=", fields.Date.today()),
                    ("emp_code", "=", logdata.get("emp_code")),
                    ("remote_server_id", "=", self.id),
                ],
                limit=1,
            )
            if not client_data_rec:
                employee_data.append(vals)
        self.env["client.data"].create(employee_data)
        server["date_sync"] = datetime.now()
        return True

    def _fetch_client_past_date_deta(self, server):
        log_datas = []
        employee_data_dic = []
        if server:
            addr = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
        try:
            uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr)).authenticate(
                dbname, userid, password, {}
            )
        except:
            _logger.warning("Could not authenticate user on the remote server")
        try:
            log_datas = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname,
                uid,
                password,
                "partner.work.history",
                "search_read",
                ([
                    ('employee_id', '!=', False),
                    ('join_date', '<=', self.start_date),
                    ('write_date', '<=', fields.Date.today()),
                    ('write_date', '>=', fields.Date.today()),
                    '|',
                    ('end_date', '>=', fields.Date.today()),
                    ('end_date', '=', False)
                ]),
                ["partner_company_id", "employee_id", "emp_code"],
            )
            if self.start_date <= fields.Date.today():
                for log_data in log_datas:
                    number_of_days = 1
                    differece_days = fields.Date.today() - self.start_date
                    for day in range(differece_days.days + 1):
                        date = self.start_date + relativedelta(day=number_of_days)
                        employee_data_dic.append({
                            'partner_company': log_data.get("partner_company_id")[1]
                            if log_data.get("partner_company_id")
                            else "",
                            "emp_code": log_data.get("emp_code"),
                            "emp_name": log_data.get("employee_id")[1],
                            "date": date
                        })
                        number_of_days += 1
        except:
            _logger.warning("Could not retrieve data from client server")
        employee_data = []
        for emp_data in employee_data_dic:
            vals = {
                "partner_id": self.partner_id.id,
                "emp_name": emp_data.get("emp_name"),
                "res_model": "hr.employee",
                "emp_code": emp_data.get("emp_code"),
                "partner_company": emp_data.get("partner_company"),
                "date": emp_data.get("date"),
                "remote_server_id": self.id,
            }
            client_data_rec = self.env["client.data"].search(
                [
                    ("date", "=", emp_data.get("date")),
                    ("emp_code", "=", emp_data.get("emp_code")),
                    ("remote_server_id", "=", self.id),
                ],
                limit=1,
            )
            if not client_data_rec:
                employee_data.append(vals)
        self.env["client.data"].create(employee_data)
        server["date_sync"] = datetime.now()
        return True

    def button_sync_partner_data(self):
        for server in self:
            url = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
            try:
                uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (url)).authenticate(
                    dbname, userid, password, {}
                )
                if not uid:
                    raise UserError(_("Connection Failed!"))
            except:
                raise UserError(_("Connection Failed!"))
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Synced successfully!"),
                    "message": _("Everything seems properly synced!"),
                    "sticky": False,
                },
            }

    @api.model
    def _client_log_data_fetch(self):
        server_datas = self.env["remote.server"].search([])
        for server in server_datas:
            server._fetch_client_log_data(server)
            self._cr.commit()
        self._generate_employee_creation_charges()

    @api.model
    def _client_log_data_fetch_past_date(self):
        server_datas = self.env["remote.server"].search([])
        for server in server_datas:
            server._fetch_client_past_date_deta(server)
            self._cr.commit()
        self._generate_employee_creation_charges()

    def _fetch_client_one_time_charges_data(self, server):
        log_datas = []
        employee_data_dic = []
        if server:
            addr = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
        try:
            uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr)).authenticate(
                dbname, userid, password, {}
            )
        except:
            _logger.warning("Could not authenticate user on the remote server")
        try:
            log_datas = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname,
                uid,
                password,
                "partner.work.history",
                "search_read",
                ([
                    ('employee_id', '!=', False),
                    ('join_date', '<=', server.start_date),
                ]),
                ["partner_company_id", "employee_id", "emp_code"],
            )
        except:
            _logger.warning("Could not retrieve data from client server")
        employee_data = []
        for logdata in log_datas:
            vals = {
                "partner_id": self.partner_id.id,
                "emp_name": logdata.get("employee_id")[1],
                "res_model": "hr.employee",
                "emp_code": logdata.get("emp_code"),
                "partner_company": logdata.get("partner_company_id")[1]
                if logdata.get("partner_company_id")
                else "",
                "date": fields.Date.today(),
                "remote_server_id": self.id,
                "is_one_time_charges": True,
            }
            client_data_rec = self.env["client.data"].search([
                ("emp_code", "=", logdata.get("emp_code")),
                ("remote_server_id", "=", self.id),
                ("is_one_time_charges", "=", True),
            ], limit=1)
            if not client_data_rec:
                employee_data.append(vals)
        self.env["client.data"].create(employee_data)
        server["date_sync"] = datetime.now()
        return True

    @api.model
    def _client_one_time_charges_data(self):
        server_datas = self.env["remote.server"].search([])
        for server in server_datas:
            server._fetch_client_one_time_charges_data(server)

    def _generate_employee_creation_charges(self):
        balance_history_obj = self.env['balance.history']
        client_datas = self.env["client.data"].with_context(active_test=False).search([
            ("is_paid", "=", False),
            ("date", "<=", fields.Date.today())
        ])
        remote_server_rec = client_datas.mapped('remote_server_id')
        for server in remote_server_rec:
            number_of_employee = len(client_datas.filtered(lambda line: line.remote_server_id.id == server.id))
            amount = number_of_employee * server.rate
            new_balance_rec = balance_history_obj.create({
                'description': 'Daily employee charges :- %s' %(fields.Date.today().strftime('%d-%m-%Y')),
                'partner_id': server.partner_id.id,
                'credit': 0.0,
                'debit': amount,
                'date': fields.Date.today(),
            })
            client_data_rec = client_datas.filtered(
                lambda line: line.remote_server_id.id == server.id)
            server.partner_id.balance -= amount
            client_data_rec.write({
                'balance_history_id': new_balance_rec.id,
                'is_paid': True
            })

    @api.model
    def _generate_customer_bill(self):
        previous_month_first_date = fields.Date.today() + relativedelta(
            months=-1, day=1
        )
        previous_month_last_date = previous_month_first_date + relativedelta(
            day=calendar.monthrange(
                previous_month_first_date.year, previous_month_first_date.month
            )[1]
        )
        client_datas = (
            self.env["client.data"]
            .with_context(active_test=False)
            .search(
                [
                    "|",
                    ("date", "=", False),
                    "&",
                    ("date", ">=", previous_month_first_date),
                    ("date", "<=", previous_month_last_date),
                ]
            )
        )
        product_id = self.env.ref(
            "sync_clients_data_master.employee_creation_invoice_product"
        )
        for partner, lines in groupby(client_datas, lambda l: l.partner_id):
            for remote_server, lines in groupby(
                client_datas.filtered(lambda l: l.partner_id.id == partner.id),
                lambda l: l.remote_server_id,
            ):
                invoice_vals = {
                    "partner_id": partner.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product_id.id,
                                "quantity": len(list(lines)),
                                "price_unit": remote_server.rate or 0.0,
                                "remote_server_id": remote_server.id,
                            },
                        )
                    ],
                }
                self.env["account.move"].create(invoice_vals).action_post()
