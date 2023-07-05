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
        'hr'
    ],
    'data': [
        'views/crm_lead_view.xml',
        'views/website_templates.xml',
        'views/website_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_extend/static/src/js/website_extend.js',
        ],
    },
    'application': True,
    'installable': True,
}
