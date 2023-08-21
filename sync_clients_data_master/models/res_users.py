import io
import base64
import tempfile
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from io import StringIO
from datetime import datetime, date

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _fetch_customers_minimum_balance(self):
        minimum_balance_list = []
        customer_rec = self.env["res.partner"].search([])
        for customer in customer_rec:
            if customer.balance < customer.minimum_balance:
                minimum_balance_list.append(customer.id)
        customer_minimum_balance_rec = self.env['res.partner'].browse(minimum_balance_list)
        attch_obj = self.env["ir.attachment"]
        # Create Work Book
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        # Add Sheet
        sheet = workbook.add_worksheet('Customers Balance List')
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
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 35)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 20)
        sheet.write('A1', 'Sr.No', column_fmt)
        sheet.write('B1', 'Customer Name', column_fmt)
        sheet.write('C1', 'Current Balance', column_fmt)
        sheet.write('D1', 'Minimum Balance', column_fmt)
        row = 1
        sr_count = 1
        for customer in customer_minimum_balance_rec:
            sheet.write(row, 0, sr_count, row_center_fmt)
            sheet.write(row, 1, customer.display_name or '', row_center_fmt)
            sheet.write(row, 2, customer.balance, row_center_fmt)
            sheet.write(row, 3, customer.minimum_balance, row_center_fmt)
            row += 1
            sr_count += 1
        # Workbook save and end
        workbook.close()
        data = base64.b64encode(fp.getvalue())
        fp.close()
        # Deleting existing attachment files
        attach_ids = attch_obj.search([
            ('res_model', '=', 'mail.template')
        ])
        if attach_ids:
            try:
                attach_ids.unlink()
            except:
                pass
        # Creating Attachment
        today_date = date.today()
        today_date_str = today_date.strftime('%d/%m/%Y')
        report_name = 'customers_minimum_balance_list_%s.xlsx' % (today_date_str)
        doc_id = attch_obj.sudo().create({
            'name': report_name,
            'datas': data,
            'res_model': 'mail.template',
            'name': report_name,
            'public': True,
        })
        user_admin = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'sync_clients_data_master.email_template_customers_minimum_balance_list')
        mail_template.write({
            'attachment_ids': [(6, 0, [doc_id.id])],
            'subject': 'Customers Minimum Balance List : %s' % (today_date_str)
        })
        if customer_minimum_balance_rec:
            mail_template.send_mail(user_admin.id, force_send=True)
        return True
