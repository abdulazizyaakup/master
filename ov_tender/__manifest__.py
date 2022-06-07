# -*- coding: utf-8 -*-
{
    'name': "ov_tender",

    'summary': """
        This module is for tender monitoring system which will send email to subscriber on related tender based on
        keywords""",

    'description': """
        This module is for tender monitoring system which will send email to subscriber on related tender based on
        keywords
    """,

    'author': "Optivolve Group Sdn Bhd",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale','website','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/report_invoice.xml',
        'views/tender_views.xml',
        'views/keywords_views.xml',
        'views/partner_views.xml',
        #'wizard/add_customer_view.xml',
        'views/template_edited.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}