from datetime import datetime
import ast
from datetime import datetime, date, timedelta, timezone
from pytz import timezone, utc, UTC
from odoo import http 
import pytz
import json
from odoo.http import request
from odoo import api
import time
import re
from odoo.exceptions import ValidationError
import werkzeug
import base64
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.addons.website.controllers.main import Website


class Appointmentform(http.Controller):

    @http.route(['/appointments'], type='http', auth='public', website=True)
    def appointment_form(self, **kw):
        if request.httprequest.method == 'GET':
            contact_us_dict = {}
            if kw.get('data'):
                contact_us_dict = ast.literal_eval(kw.get('data'))
            else:
                contact_us_dict = kw
            kw = contact_us_dict

            vals= {
                    'partner_name': kw.get('name') ,
                    'phone': kw.get('phone'),
                    'email': kw.get('email_from'),
                    'company': kw.get('company'),
                    'description': kw.get('description'),
                    'subject': kw.get('subject'),
                }
            return request.render('appointment_booking_contact_us.appointments_template', vals)
        elif request.httprequest.method == 'POST':
            partner_id = request.env['res.partner'].search([('email','=',kw.get('email'))],limit=1)
            if not partner_id:
                rec = {}
                rec.update({
                    'name' : kw.get('partner_name'),
                    'email': kw.get('email'),
                    'phone': kw.get('phone'),
                })                
                partner_id = request.env['res.partner'].sudo().create(rec)
            attendees_ids_obj_if_exits = [
                 (0,0, {  'phone': kw.get('phone'),'email': kw.get('email'),'partner_id': partner_id.id,'event_id': 1,})
                ]
            start_date = datetime.strptime(kw.get('start'), '%Y-%m-%d %H:%M:%S')
            user_tz_main =  pytz.timezone("Asia/Calcutta")
            if request.session.uid :
                print("THISSSS IS IF STARTEMENT")
                user_tz = request.env.user.tz 
                user_tz_main = pytz.timezone(user_tz)
            localized_datetime = user_tz_main.localize(start_date)
            utc_datetime = localized_datetime.astimezone(pytz.UTC)
            updated_start_date = utc_datetime.replace(tzinfo=None)
            stop_time = updated_start_date + timedelta(hours=1)
            create_vals = {
                'name': kw.get('subject'),
                'start': updated_start_date,
                'stop': stop_time,
                'partner_ids': (4, partner_id.id),
                'description': kw.get('description'),
                'attendee_ids': attendees_ids_obj_if_exits,
                'user_id': request.env.user.id,
            }
            create_vals_crm = {
                'name': kw.get('subject'),
                'phone':kw.get('phone'),
                'email_from':kw.get('email'),
                'partner_id': partner_id.id,
                'user_id': request.env.user.id,
            }
            request.env['calendar.event'].sudo().create(create_vals)
            request.env['crm.lead'].sudo().create(create_vals_crm)
            return request.render('appointment_booking_contact_us.thankyou_appointment_form')

    @http.route(['/thankyouAppointmentsubmitted'], type='http', auth='public', website=True)
    def thankyou_submission(self, **kw):

        return request.render("appointment_booking_contact_us.thankyou_appointment_form")
    



   

