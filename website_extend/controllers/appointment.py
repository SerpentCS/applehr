
import json
from babel.dates import format_datetime, format_date, format_time
from datetime import datetime
from werkzeug.exceptions import NotFound
from odoo import exceptions, http, fields, _
from odoo.http import request, route
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo.tools.misc import get_lang
from odoo.addons.appointment.controllers.appointment import AppointmentController


class AppointmentControllerExtend(AppointmentController):


    @http.route(['/appointment/<int:appointment_type_id>/info'],
                type='http', auth="public", website=True, sitemap=False)
    def appointment_type_id_form(self, appointment_type_id, staff_user_id, date_time, duration, **kwargs):
        """
        Render the form to get information about the user for the appointment

        :param appointment_type_id: the appointment type id related
        :param staff_user_id: the user selected for the appointment
        :param date_time: the slot datetime selected for the appointment
        :param duration: the duration of the slot
        :param filter_appointment_type_ids: see ``Appointment.appointments()`` route
        """
        appointment_type = self._fetch_and_check_private_appointment_types(
            kwargs.get('filter_appointment_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('invite_token'),
            current_appointment_type_id=int(appointment_type_id),
        )
        if not appointment_type:
            raise NotFound()
        partner = self._get_customer_partner()
        partner_data = partner.read(fields=['name', 'mobile', 'email'])[0] if partner else {}
        date_time_object = datetime.strptime(date_time, dtf)
        day_name = format_datetime(date_time_object, 'EEE', locale=get_lang(request.env).code)
        date_formated = format_date(date_time_object.date(), locale=get_lang(request.env).code)
        time_locale = format_time(date_time_object.time(), locale=get_lang(request.env).code, format='short')
        if kwargs and kwargs.get('data', False):
            data = json.loads(kwargs.get('data'))
            if data:
                if data.get('name', False):
                    name = data.get('name', False)
                    partner_data.update({ 'name': name })
                if data.get('phone', False):
                    phone = data.get('phone', False)
                    partner_data.update({ 'mobile': phone })
                    partner_data.update({ 'phone': phone })
                if data.get('email_from', False):
                    email = data.get('email_from', False)
                    partner_data.update({ 'email': email })
        return request.render("appointment.appointment_form", {
            'partner_data': partner_data,
            'appointment_type': appointment_type,
            'available_appointments': self._fetch_available_appointments(
                kwargs.get('filter_appointment_type_ids'),
                kwargs.get('filter_staff_user_ids'),
                kwargs.get('invite_token'),
            ),
            'main_object': appointment_type,
            'datetime': date_time,
            'date_locale': day_name + ' ' + date_formated,
            'time_locale': time_locale,
            'datetime_str': date_time,
            'duration_str': duration,
            'duration': float(duration),
            'staff_user': request.env['res.users'].browse(int(staff_user_id)),
            'timezone': request.session.get('timezone') or appointment_type.appointment_tz,  # bw compatibility
            'users_possible': self._get_possible_staff_users(appointment_type, json.loads(kwargs.get('filter_staff_user_ids') or '[]')),
        })

