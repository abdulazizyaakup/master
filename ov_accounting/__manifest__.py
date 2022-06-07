# -*- coding: utf-8 -*-
{
    'name': "Optivolve Accounting",

    'summary': """
        Inherit of Accounting module""",

    'description': """
        This module inherit accounting module required fields
    """,

    'author': "Abdul Aziz Yaakup",
    'website': "http://optivolve.com",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['account','account_accountant','account_analytic_default','account_reports','account_invoice_extract'],

    'data': [
        # 'views/ov_accounting_views.xml',
        'views/ov_report_payment_receipt_templates.xml',
    ],
    
    'demo': [],
    'qweb': [],
    'installabe':True,
}