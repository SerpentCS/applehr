# -*- coding: utf-8 -*-

{
    'name': 'Website Extend',
    'description': '''Website Extend''',
    'category': 'Website',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'depends': [
        'crm',
        'calendar',
        'website_sale',
        'appointment', 
        'hr',
        'portal',
        'website_slides'
    ],
    'data': [
        'views/crm_lead_view.xml',
        'views/website_templates.xml',
        'views/website_view.xml',
        'views/sale_order_view.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'website_extend/static/src/scss/website_extend.scss',
            'website_extend/static/src/xml/website_slides_fullscreen.xml',
            'website_extend/static/src/js/slides_course_fullscreen_player.js',
            'website_extend/static/src/js/website_extend.js',
            'website_extend/static/src/js/balance_portal.js',
        ],
    },
    'application': True,
    'installable': True,
}
