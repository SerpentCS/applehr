import psycopg2
import xmlrpc
import xmlrpc.client
import functools
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from itertools import groupby
import logging

import ast
from odoo import api, fields, models, _

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

_logger = logging.getLogger(__name__)


class RemoteServer(models.Model):
    _name = "remote.server"
    _description = "Remote Server"

    name = fields.Char("Name", required=1)
    url = fields.Char("Server Url", required=1)
    user = fields.Char("User", required=1)
    password = fields.Char("Password", required=1)
    dbname = fields.Char("Database", required=1)
    partner_id = fields.Many2one('res.partner', "Customer",
                                 ondelete="cascade", copy=False)
    date_sync = fields.Datetime(string="Last Sync Date", default=datetime.now())

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
                'sync.client.data.log',
                'search_read',
                [('state', '=', 'logged')],
                ['name', 'log_date', 'res_id', 'model_name', 'method', 'uuid', 'args',
                 'state']
            )
        except:
            _logger.warning("Could not retrieve data from client server")
        fetch_ids = []
        for logdata in log_datas:
            fetch_ids.append(logdata.get('id'))
            logdata.pop('id')
        client_logs = self.env['sync.client.data.log'].create(log_datas)
        if client_logs:
            try:
                xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                    dbname,
                    uid,
                    password,
                    'sync.client.data.log',
                    'write',
                    fetch_ids,
                     {'state': "Synced"}
                )
                client_logs.write({'state': "Synced",
                                   'remote_server_id': server.id
                                   })
                self._cr.commit()
            except:
                _logger.warning("Error on acknowledgement")
        server['date_sync'] = datetime.now()
        return True

    def _process_data(self):
        client_data_logs = self.env['sync.client.data.log'].search([('state', '=', 'Synced')],
                                                                   order='log_date')
        client_data_obj = self.env['client.data']
        for data_log in client_data_logs:
            client_data = client_data_obj.with_context(active_test=False).search([('res_id', '=', data_log.res_id),
                                                 ('res_model', '=', data_log.model_name),
                                                 ('partner_id', '=', data_log.remote_server_id.partner_id.id)],
                                                 limit=1)
            args = ast.literal_eval(data_log.args)
            status = args.get('status')
            start_date = data_log.log_date.date()
            end_date = date(start_date.year + start_date.month // 12, start_date.month % 12 + 1, 1) - timedelta(1)
            if data_log.method == 'create' and (client_data.active == False or not client_data):
                vals = {
                        'partner_id': data_log.remote_server_id.partner_id.id,
                        'emp_name': data_log.name,
                        'res_id': data_log.res_id,
                        'res_model': data_log.model_name,
                        'date_start':start_date,
                        'active': status
                        }
                client_data_obj.create(vals)
                self._cr.commit()
            elif client_data and data_log.method in ['write', 'unlink']:
                if status:
                    client_data.write({
                                       'date_start': start_date,
                                       'date_end': False,
                                       'active': status
                                       })
                else:
                    client_data.write({
                                       'date_end': end_date,
                                       'active': status
                                       })
            data_log.write({"state": "Processed"})
            self._cr.commit()
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
            except:
                raise UserError (_('Connection Failed!'))

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Synced successfully!"),
                    'message': _("Everything seems properly synced!"),
                    'sticky': False,
                    }
            }

    @api.model
    def _client_log_data_fetch(self):
        server_datas = self.env['remote.server'].search([])
        for server in server_datas:
            server._fetch_client_log_data(server)
            self._cr.commit()

    @api.model
    def _client_process_data(self):
        server_datas = self.env['remote.server'].search([])
        for server in server_datas:
            server._process_data()
            self._cr.commit()

    @api.model
    def _generate_customer_bill(self):
        current_date = fields.Date.today()
        one_month_before_date = current_date + relativedelta(months=-1)
        
        client_datas = self.env['client.data'].with_context(active_test=False).search([
            '|', ('date_end', '=', False), '&', ('date_end', '>=', one_month_before_date), ('date_end', '<=', current_date)
        ])
        print('>>>>>>>>>>>>>>>',client_datas)

        product_id = self.env.ref('sync_clients_data_master.employee_creation_invoice_product')

        for partner, lines in groupby(client_datas, lambda l: l.partner_id):
            invoice_vals = {'partner_id': partner.id,
                            'move_type':'out_invoice',
                            'invoice_line_ids': [(0, 0, {
                                                'product_id': product_id.id,
                                                'quantity': len(list(lines)),
                                                'price_unit': product_id.lst_price,
                                            })]
                            }
            print('>>>>>>>>>>>>>>>>',invoice_vals)
            self.env['account.move'].create(invoice_vals).action_post()
