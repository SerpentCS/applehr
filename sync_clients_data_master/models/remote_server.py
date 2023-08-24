import calendar
import logging
from datetime import datetime, date
import pytz
from datetime import timedelta
from itertools import groupby
from odoo.exceptions import ValidationError
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
        "res.partner", "Customer", ondelete="cascade", copy=False)
    date_sync = fields.Datetime(string="Last Sync Date", default=datetime.now())
    rate = fields.Float()
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    is_stop_server = fields.Boolean(string="Stop/Run Server")

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

    def button_stop_server(self):
        for server in self:
            if not server.end_date:
                raise ValidationError(_(
                    "End Date are required in sync client data line %s!") % (server.name))
            server.write({
               "is_stop_server": True,
            })

    def button_start_server(self):
        for server in self:
            server.write({
               "is_stop_server": False,
               "end_date": False,
            })

    def _fetch_daily_data(self, server):
        user = self.env['res.users'].sudo().browse([2])
        tz = pytz.timezone(user.tz) or pytz.utc
        today_user_tz_date = pytz.utc.localize(datetime.now()).astimezone(tz).date()
        # Get employee active deta base on today date
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
                    '|',
                    ('end_date', '>=', today_user_tz_date),
                    ('end_date', '=', False)
                ]),
                ["partner_company_id", "employee_id", "emp_code"],
            )
        except:
            _logger.warning("Could not retrieve data from client server")
        employee_data = []
        client_data_rec = self.env["client.data"].search([
            ("date", "=", today_user_tz_date),
            ("remote_server_id", "=", server.id),
            ("is_one_time_charges", "=", False),
        ])
        for logdata in log_datas:
            vals = {
                "partner_id": server.partner_id.id,
                "emp_name": logdata.get("employee_id")[1],
                "res_model": "hr.employee",
                "emp_code": logdata.get("emp_code"),
                "partner_company": logdata.get("partner_company_id")[1]
                if logdata.get("partner_company_id")
                else "",
                "date": today_user_tz_date,
                "remote_server_id": server.id,
                "amount_charged": server.rate,
                'description': 'Daily employee charges :- %s' %(today_user_tz_date.strftime('%d-%m-%Y')),
            }
            client_data_ids = client_data_rec.filtered(
                lambda line: line.emp_code == logdata.get("emp_code"))
            if not client_data_ids:
                employee_data.append(vals)
        self.env["client.data"].create(employee_data)
        server["date_sync"] = datetime.now()
        return True

    def _fetch_past_date_deta(self, server):
        # Get employee past deta data.
        log_datas = []
        user = self.env['res.users'].sudo().browse([2])
        tz = pytz.timezone(user.tz) or pytz.utc
        today_user_tz_date = pytz.utc.localize(datetime.now()).astimezone(tz).date()
        previous_day_date = today_user_tz_date - relativedelta(days=1)
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
                    ('join_date', '>=', server.start_date),
                    ('write_date', '<=', today_user_tz_date),
                    ('write_date', '>=', previous_day_date),
                ]),
                ["partner_company_id", "employee_id", "emp_code", "join_date", "end_date"],
            )
        except:
            _logger.warning("Could not retrieve data from client server")
        employee_data = []
        client_data_rec = self.env["client.data"].search([
            ("remote_server_id", "=", server.id),
            ("is_one_time_charges", "=", False),
        ])
        for logdata in log_datas:
            emp_join_date_str = logdata.get("join_date")
            emp_end_date_str = logdata.get("end_date")
            emp_end_date = False
            if emp_end_date_str:
                emp_end_date = datetime.strptime(emp_end_date_str, "%Y-%m-%d").date()
            if not emp_end_date:
                emp_end_date = previous_day_date
            emp_join_date = datetime.strptime(emp_join_date_str, "%Y-%m-%d").date()
            differece_days = emp_end_date - emp_join_date
            number_of_days = 0
            for day in range(differece_days.days + 1):
                date = emp_join_date + timedelta(days=number_of_days)
                vals = {
                    "partner_id": server.partner_id.id,
                    "emp_name": logdata.get("employee_id")[1],
                    "res_model": "hr.employee",
                    "emp_code": logdata.get("emp_code"),
                    "partner_company": logdata.get("partner_company_id")[1]
                    if logdata.get("partner_company_id")
                    else "",
                    "date": date,
                    "remote_server_id": server.id,
                    "amount_charged": server.rate,
                    'description': 'Daily employee charges :- %s' %(date.strftime('%d-%m-%Y')),
                }
                number_of_days += 1
                client_data_ids = client_data_rec.filtered(
                    lambda line: line.emp_code == logdata.get("emp_code") and line.date == date)
                if not client_data_ids:
                    employee_data.append(vals)
        self.env["client.data"].create(employee_data)
        server["date_sync"] = datetime.now()
        return True

    def _fetch_one_time_charges_data(self, server):
        # Get employee one time charges data base on differece days in conf.
        user = self.env['res.users'].sudo().browse([2])
        tz = pytz.timezone(user.tz) or pytz.utc
        today_user_tz_date = pytz.utc.localize(datetime.now()).astimezone(tz).date()
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
                    ('join_date', '<=', server.start_date),
                ]),
                ["partner_company_id", "employee_id", "emp_code", "join_date", "end_date"],
            )
        except:
            _logger.warning("Could not retrieve data from client server")
        dict_res = {}
        employee_data = []
        client_data_rec = self.env["client.data"].search([
            ("remote_server_id", "=", server.id)
        ])
        for logdata in log_datas:
            emp_join_date_str = logdata.get("join_date")
            emp_end_date_str = logdata.get("end_date")
            emp_end_date = False
            if emp_end_date_str:
                emp_end_date = datetime.strptime(emp_end_date_str, "%Y-%m-%d").date()
            if not emp_end_date:
                emp_end_date = today_user_tz_date
            emp_join_date = datetime.strptime(emp_join_date_str, "%Y-%m-%d").date()
            differece_days = server.start_date - emp_join_date
            if differece_days.days >= server.partner_id.days_one_time_charge:
                if logdata.get("emp_code") not in dict_res:
                    dict_res[logdata.get("emp_code")] = {
                        "emp_code": logdata.get("emp_code")
                    }
                    vals = {
                        "partner_id": server.partner_id.id,
                        "emp_name": logdata.get("employee_id")[1],
                        "res_model": "hr.employee",
                        "emp_code": logdata.get("emp_code"),
                        "partner_company": logdata.get("partner_company_id")[1]
                        if logdata.get("partner_company_id")
                        else "",
                        "date": today_user_tz_date,
                        "remote_server_id": server.id,
                        "is_one_time_charges": True,
                        "amount_charged": server.partner_id.one_time_charge,
                        'description': 'One time employee charges :- %s' %(today_user_tz_date.strftime('%d-%m-%Y')),
                    }
                    client_data_ids = client_data_rec.filtered(
                        lambda line: line.emp_code == logdata.get("emp_code") and line.is_one_time_charges)
                    if not client_data_ids:
                        employee_data.append(vals)
            elif differece_days.days < server.partner_id.days_one_time_charge:
                total_days = today_user_tz_date - emp_join_date
                number_of_days = 0
                for day in range(total_days.days + 1):
                    date = emp_join_date + timedelta(days=number_of_days)
                    if emp_end_date >= date:
                        vals = {
                            "partner_id": server.partner_id.id,
                            "emp_name": logdata.get("employee_id")[1],
                            "res_model": "hr.employee",
                            "emp_code": logdata.get("emp_code"),
                            "partner_company": logdata.get("partner_company_id")[1]
                            if logdata.get("partner_company_id")
                            else "",
                            "date": date,
                            "remote_server_id": server.id,
                            "amount_charged": server.rate,
                            'description': 'Daily employee charges :- %s' %(date.strftime('%d-%m-%Y')),
                        }
                        number_of_days += 1
                        client_data_ids = client_data_rec.filtered(
                            lambda line: line.emp_code == logdata.get("emp_code") and line.date == date)
                        if not client_data_ids:
                            employee_data.append(vals)
        self.env["client.data"].create(employee_data)
        server["date_sync"] = datetime.now()
        return True

    @api.model
    def _fetch_employee_data(self):
        server_datas = self.env["remote.server"].search([
            ('is_stop_server', '=', False)
        ])
        for server in server_datas:
            server._fetch_daily_data(server)
            server._fetch_past_date_deta(server)
            server._fetch_one_time_charges_data(server)
            self._cr.commit()
        self._generate_employee_creation_charges()

    # @api.model
    # def _fetch_employee_past_date_data(self):
    #     server_datas = self.env["remote.server"].search([
    #         ('is_stop_server', '=', False)
    #     ])
    #     for server in server_datas:
    #         server._fetch_past_date_deta(server)
    #         self._cr.commit()
    #     self._generate_employee_creation_charges()

    # @api.model
    # def _fetch_one_time_charges_employee_data(self):
    #     server_datas = self.env["remote.server"].search([
    #         ('is_stop_server', '=', False)
    #     ])
    #     for server in server_datas:
    #         server._fetch_one_time_charges_data(server)
    #     self._generate_employee_creation_charges()

    def _generate_employee_creation_charges(self):
        user = self.env['res.users'].sudo().browse([2])
        tz = pytz.timezone(user.tz) or pytz.utc
        today_user_tz_date = pytz.utc.localize(datetime.now()).astimezone(tz).date()
        balance_history_obj = self.env['balance.history']
        client_datas = self.env["client.data"].with_context(active_test=False).search([
            ("is_paid", "=", False),
            ("is_one_time_charges", "=", False),
            ("date", "<=", today_user_tz_date)
        ])
        client_one_time_charges_datas = self.env["client.data"].with_context(active_test=False).search([
            ("is_paid", "=", False),
            ("is_one_time_charges", "=", True),
            ("date", "<=", today_user_tz_date)
        ])
        remote_server_rec = client_datas.mapped('remote_server_id')
        remote_server_one_time_charges_rec = client_one_time_charges_datas.mapped('remote_server_id')
        for server in remote_server_rec:
            number_of_employee = len(client_datas.filtered(lambda line: line.remote_server_id.id == server.id))
            amount = number_of_employee * server.rate
            new_balance_rec = balance_history_obj.create({
                'description': 'Daily employee charges :- %s' %(today_user_tz_date.strftime('%d-%m-%Y')),
                'partner_id': server.partner_id.id,
                'credit': 0.0,
                'debit': amount,
                'date': today_user_tz_date,
            })
            client_data_rec = client_datas.filtered(
                lambda line: line.remote_server_id.id == server.id)
            server.partner_id.balance -= amount
            new_balance_rec.write({
                'closing_balance': server.partner_id.balance
            })
            client_data_rec.write({
                'balance_history_id': new_balance_rec.id,
                'is_paid': True
            })
        for server in remote_server_one_time_charges_rec:
            number_of_employee = len(client_one_time_charges_datas.filtered(lambda line: line.remote_server_id.id == server.id))
            amount = number_of_employee * server.partner_id.one_time_charge
            new_balance_rec = balance_history_obj.create({
                'description': 'One time employee charges :- %s' %(today_user_tz_date.strftime('%d-%m-%Y')),
                'partner_id': server.partner_id.id,
                'credit': 0.0,
                'debit': amount,
                'date': today_user_tz_date,
            })
            client_data_rec = client_one_time_charges_datas.filtered(
                lambda line: line.remote_server_id.id == server.id)
            server.partner_id.balance -= amount
            new_balance_rec.write({
                'closing_balance': server.partner_id.balance
            })
            client_data_rec.write({
                'balance_history_id': new_balance_rec.id,
                'is_paid': True
            })
