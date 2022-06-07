# -*- coding: utf-8 -*-
{
    'name': "OV Scanner",

    'summary': """
        Integrate with TWAIN scanner""",

    'description': """
        Integrate with TWAIN Scanner
    """,

    'author': "Optivolve Group Sdn Bhd",
    'website': "http://optivolve.co",
    'category': '',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ov_scanner_views.xml',
    ],
    'qweb': ['static/src/xml/ov_scanner.xml'],
    'demo': [
        #'demo/demo.xml',
    ],
    'installabe':True,
}