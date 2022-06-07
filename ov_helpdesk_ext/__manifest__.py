# -*- coding: utf-8 -*-
{
    'name': "OV Helpdesk Ext",

    'summary': """
        Extension for Helpdesk module to link with ATS System""",

    'description': """
        This module inherit Helpdesk module to link with ATS System
    """,

    'author': "Optivolve Group Sdn Bhd",
    'website': "http://optivolve.co",
    'category': 'Employees',
    'version': '1.0',
    'depends': ['base', 'hr','hr_recruitment','helpdesk','ov_hr_recruitment_ext'],

    'data': [
        'views/ov_helpdesk_ext_views.xml'
        
        #'views/templates.xml',
    ],
    
    'demo': [],
    'installabe':True,
}