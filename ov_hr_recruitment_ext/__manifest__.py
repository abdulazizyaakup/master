# -*- coding: utf-8 -*-
{
    'name': "OV HR Recruitment Ext",

    'summary': """
        Extension for HR Recruitment to includes all required fields for ATS System""",

    'description': """
        This module inherit hr_recruitment meodule to add all required fields for ATS, including Project Management and Deployment Module on HRMS System
    """,

    'author': "Optivolve Group Sdn Bhd",
    'website': "http://optivolve.co",
    'category': 'Employees',
    'version': '1.0',
    'depends': ['base','hr_recruitment','hr','hr_contract','website'],

    'data': [
        'security/ir.model.access.csv',
        'data/map_website_data.xml',
        'data/delete_existing_data.xml',
        'data/stage_data.xml',
        'data/contact_stage_data.xml',
        'data/ov_salary_package_data.xml',
        'data/days_avail_data.xml',
        'data/races_data.xml',
        'data/shift_preference_data.xml',
        'data/source_data.xml',
        'data/interview_form_data.xml',
        'demo/ov_preferred_location.xml',
        'demo/ov_preferred_site.xml',
        'demo/ov_job_position.xml',
        'views/applicant_templates.xml',
        'views/ov_races_view.xml',
        'views/ov_salary_package_view.xml',
        'views/ov_project_site_view.xml',
        'views/ov_hr_recruitment_ext_view.xml',
        'views/ov_hr_employee_ext_view.xml',
        'views/ov_res_partner_view.xml',
        'views/map_website_view.xml',
        'views/res_users_view.xml',
        'views/ov_prev_company_view.xml',
        'wizard/contact_status_views.xml',
        'report/contract_daily.xml',
        'report/contract_monthly.xml',
        'report/contract_daily_applicant.xml',
        'report/contract_monthly_applicant.xml',
        
        #'views/templates.xml',
    ],
    
    'demo': [],
    'installabe':True,
}