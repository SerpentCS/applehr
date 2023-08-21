from datetime import datetime
from odoo import http
import webbrowser
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from werkzeug.urls import url_join
from urllib.parse import urlparse, parse_qs, urlencode
import io
import base64
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
from io import StringIO

class BalanceHistory(http.Controller):

    @http.route(['/my/quotes/history/'], type='http', auth="public", csrf=False, website=True)
    def portal_my_invoice_detail(self, **kw):
        if kw :
            attch_obj = request.env["ir.attachment"]
            user = request.env.user
            client_data_rec = request.env['client.data'].sudo().search([
                ('partner_id', '=', user.partner_id.id),
                ('date', '>=', kw.get('start_date')),
                ('date', '<=', kw.get('end_date'))
            ])
            # Create Work Book
            fp = io.BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            # Add Sheet
            sheet = workbook.add_worksheet('Customers Balance History Report')
            # Set Table Header format
            column_fmt = workbook.add_format({
                'border': 1,
                'font_name': 'Calibri',
                'align': 'center',
                'font_size': 10,
                'bold': True,
                'text_wrap': True,
            })
            row_center_fmt = workbook.add_format({
                'border': 1,
                'font_name': 'Calibri',
                'align': 'center',
                'font_size': 10,
            })
            row_right_fmt = workbook.add_format({
                'border': 1,
                'font_name': 'Calibri',
                'align': 'right',
                'font_size': 10,
            })
            sheet.merge_range('A1:G2', 'Employee Charges Report', column_fmt)
            sheet.merge_range('A3:G3', '')
            sheet.merge_range('A4:G4', user.partner_id.name, column_fmt)
            sheet.merge_range('A5:G5', '')
            sheet.merge_range('A6:D6', "Start Date :- " + kw.get('start_date'), column_fmt)
            sheet.merge_range('E6:G6', "End Date :- " + kw.get('end_date'), column_fmt)
            sheet.merge_range('A7:G7', '')
            sheet.set_column('A:A', 10)
            sheet.set_column('B:B', 10)
            sheet.set_column('C:C', 10)
            sheet.set_column('D:D', 35)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 35)
            sheet.set_column('G:G', 10)
            sheet.write('A8', 'Sr. No', column_fmt)
            sheet.write('B8', 'Date', column_fmt)
            sheet.write('C8', 'Spequa ID', column_fmt)
            sheet.write('D8', 'Partner Company', column_fmt)
            sheet.write('E8', 'Server Name', column_fmt)
            sheet.write('F8', 'Description', column_fmt)
            sheet.write('G8', 'Charged Amount', column_fmt)
            row = 8
            sr_count = 1
            total_amount = 0.0
            for client_data in client_data_rec:
                sheet.write(row, 0, sr_count, row_center_fmt)
                sheet.write(row, 1, client_data.date.strftime('%d-%m-%Y'), row_center_fmt)
                sheet.write(row, 2, client_data.emp_code, row_center_fmt)
                sheet.write(row, 3, client_data.partner_company, row_center_fmt)
                sheet.write(row, 4, client_data.remote_server_id.name, row_center_fmt)
                sheet.write(row, 5, client_data.balance_history_id.description, row_center_fmt)
                sheet.write(row, 6, client_data.amount_charged, row_right_fmt)
                row += 1
                sr_count += 1
                total_amount += client_data.amount_charged
            sheet.merge_range(row, 0, row, 5, 'Total', row_center_fmt)
            sheet.write(row, 6, total_amount, row_right_fmt)
            workbook.close()
            data = base64.b64encode(fp.getvalue())
            fp.close()
            # Deleting existing attachment files
            attach_ids = attch_obj.sudo().search([
                ('res_model', '=', 'client.data')
            ])
            if attach_ids:
                try:
                    attach_ids.unlink()
                except:
                    pass
            # Creating Attachment
            report_name = '%s_balance_history_report_%s_%s.xlsx' % (
                user.partner_id.name, kw.get('start_date'), kw.get('end_date'))
            doc_id = attch_obj.sudo().create({
                'name': report_name,
                'datas': data,
                'res_model': 'client.data',
                'name': report_name,
                'public': True,
            })
            # Downloading the file
            # return {
            #     'type': 'ir.actions.act_url',
            #     'url': '/web/content/%s?download=true' % (doc_id.id),
            #     'target': 'self',
            #     'download': True,
            # }
        else:
            print("start date not specified")
            return request.render("website_extend.balance_history_template",{})

        

    @http.route('/my/quotes/history/pdf', csrf=False, type='http', auth="user", website=True)
    def print_picking_reports(self,**kw):

        print("keeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",kw)

        picking_ids = kw.get('ids')

        print(picking_ids)


        redirect_url = f'/report/pdf/stock.action_report_picking?docids={picking_ids}'

        return request.redirect(redirect_url)
    
        
