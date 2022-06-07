{
    'name' : 'Optivolve Scanner',
    'version': '1.0',
    'summary': 'Direct Scan Document from Odoo',
    'category': 'Tools',
    'description':
        """
Optivolve Scanner
=================

Integrated with TWAIN to direct scan documents and save into Odoo itself
        """,
    'data': [
        'security/ir.model.access.csv',
        "views/op_scanner.xml",
        #"views/op_scanner_data.xml",
        #"op_scanner.message_of_the_day.csv",
    ],
    'depends' : ['base'],
    'qweb': ['static/src/xml/op_scanner.xml'],
    'application': True,
}
