{
    'name': "G-Cast CRM",
    'summary': """
        Custom Module for G-Cast CRM""",
    'description': """
        This module for training purposes
    """,
    'author': "Fikri",
    'website': "http://www.abc.com",
    'category': 'Extra Tools',
    'version': '13.0.1',
    'depends': ['base','sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/sale_order_inherit_form.xml',
        'views/optional_items_view.xml',
        'reports/report.xml',
        'reports/quotation_sale_order.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}