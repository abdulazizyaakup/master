# -*- coding: utf-8 -*-
{
    'name': "Starken CRM Module",

    'summary': """Starken CRM Module """,

    'description': """""",

    'author': "Starken AAC Sdn. Bhd",
    'website': "http://www.starken.com.my",

    'category': 'Uncategorized',
    'version': '0.115',

    'depends': ['base', 'product', 'crm', 'sale', 'sale_crm', 'stock'],

    # always loaded
    'data': [
        'views/pricing_policy.xml',
        'data/res_groups.xml',
        'report/sale_order_report.xml',
        'wizard/create_quotation.xml',
        'wizard/keyword_filter.xml',
        'wizard/survey.xml',
        'views/partner.xml',
        'views/partner_type.xml',
        'views/crm_lead.xml',
        'views/mssql_tracker.xml',
        'views/crm_lead_category.xml',
        # 'views/starken_report.xml',
        'views/sale_order_report.xml',
        # 'views/starken_sale_order_report.xml',
        'views/product_template.xml',
        'views/template_main.xml',
        'views/sale_order.xml',
        'data/res_country_state.xml',
        'data/res_lang.xml',
        'data/partner_type.xml',
        'data/delivery_zone.xml',
        'data/crm_stage.xml',
        'data/crm_lead.xml',
        'data/mssql_query.xml',
        'data/ir_sequence.xml',
        'data/ir_default.xml',
        # 'data/res_users.xml',
        'data/ir_cron.xml',
        'data/ir_rule.xml',
        'security/ir.model.access.csv',
        'security/crm_security.xml',
        'data/ir_config_parameter.xml',
        'views/delivery_order_report.xml',
        'views/stock_picking.xml',
        'data/pricing_policy.xml',
        'views/sale_order_toapprove_list.xml',
        'views/res_config_settings.xml',
        'views/res_company_views.xml',
        'views/crm_stage_inherit_view.xml'
    ],
}
