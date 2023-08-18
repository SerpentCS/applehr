from datetime import datetime
from odoo import http
import webbrowser
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from werkzeug.urls import url_join
from urllib.parse import urlparse, parse_qs, urlencode

class BalanceHistory(http.Controller):

    @http.route(['/my/quotes/history/'], type='http', auth="public", csrf=False, website=True)
    def portal_my_invoice_detail(self, **kw):

        print("KWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",kw)

        if kw :

            user = request.env.user

            print(user)

            partner_id = user.partner_id

            print(partner_id)

            start_date_obj = kw.get('start_date')
            print(start_date_obj)

            print(type(start_date_obj))


            end_date_obj = kw.get('end_date')
            print(end_date_obj)

            print(type(end_date_obj))


            start_date = datetime.strptime(start_date_obj, '%m-%d-%Y').date()

            print(start_date)

            print('42436543623142363462524635',type(start_date))

            
            end_date = datetime.strptime(end_date_obj, '%m-%d-%Y').date()
            print(end_date)

            print("jvjdsvjsjhfjhdahjvfhajsvf",type(end_date))


            domain = []
            domain += [('date', '>=', start_date), ('date', '<=', end_date), ('partner_id','=',partner_id.id)]

            balance_records = request.env['balance.history'].search(domain)

            picking_ids_list = balance_records.mapped('id')


            picking_obj = [str(rec) for rec in picking_ids_list] 


            print('bbbbbbbbbbbbbbbbbb',picking_obj)

            picking_ids = ','.join(picking_obj)

            print('PICKKKKKKKKKKKKKKK',balance_records)


            return request.render("website_extend.balance_history_template",{
                'records': balance_records,
                'picking_ids':picking_ids
            })
            
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
    
        
