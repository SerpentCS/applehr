# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
{
    'name': 'Contact us Book Appointment',
    'description': '''This module will allow user to make Appointment Booking from the contactus page. ''',
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Serpent Consultancy Pvt Ltd',
    'depends': ['website','calendar'],


    'data': [
            'views/appointment_template.xml',
            'views/thankyou_form_submitted.xml',
            'data/website_data.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            '/appointment_booking_contact_us/static/src/js/pop.js',
        ],
    },
    'application': True,
    'installable': True,

}
