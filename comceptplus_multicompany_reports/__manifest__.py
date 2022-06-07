#! -*- encoding: utf-8 -*-
{
    'name': 'Multicompany report setup',
    'version': '1.0',
    'license': 'LGPL-3',
    'author': 'comceptPLUS',
    'summary': 'Base setup to allow multiple layouts for reports',
    'website': 'https://comceptplus.com',
    'category': 'Tools',
    'description': """
- Adds a tab in company where we can set the templates to use in reports.
- Allows to chose the paper format to apply to a company's reports.
- Adds a method to enable update of specific fields in the company's record.
- Allows to select the external layout for the company
""",
    'depends': ['base'],
    'data': ['views/res_company_view.xml'],
    'images': ['static/images/main_screenshot.png'],
    'installable': True,
}
