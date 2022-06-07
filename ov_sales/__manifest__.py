# -*- coding: utf-8 -*-
{
    'name': "Optivolve Sales",

    'summary': """
        Inherit of Sales module""",

    'description': """
        This module inherit sales module required fields
    """,

    'author': "Abdul Aziz Yaakup",
    'website': "http://optivolve.com",
    'category': 'Sales',
    'version': '1.0',
    'depends': ['base','sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'data/ov_res_partner_sequence.xml',
        'data/ov_sale_sequence.xml',
        'data/ov_purchase_sequence.xml',
        'data/ov_product_sequence.xml',
        'data/ov_delivery_order_sequence.xml',
        'data/ov_customer_group_data.xml',
        'views/ov_sales_inherit_views.xml',
        'views/ov_purchase_inherit_views.xml',
        'views/ov_partner_inherit_views.xml',
        'views/ov_stock_picking_inherit_views.xml',
        'views/ov_product_inherit_views.xml',
        'views/ov_account_invoice_inherit_views.xml',
        'views/ov_account_payment_inherit_views.xml',
        'views/ov_sales_proposal_templates.xml',
        'views/ov_sale_quotation_templates.xml',
        'views/ov_sale_invoice_templates.xml',
        'views/custom_layout_templates.xml',
    ],
    
    'demo': [],
    'qweb': [],
    'installabe':True,
}