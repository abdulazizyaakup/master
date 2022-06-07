# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_get_sales_order_approval(self):
        return self.env['ir.config_parameter'].sudo().get_param('sales.order.approval_level')

    def _default_get_so_sales_per_limit(self):
        return self.env['ir.config_parameter'].sudo().get_param('sales.person.pricedifflimit')

    def _default_get_so_agm_per_limit(self):
        return self.env['ir.config_parameter'].sudo().get_param('sales.agm.pricedifflimit')

    def _default_get_so_ceo_per_limit(self):
        return self.env['ir.config_parameter'].sudo().get_param('sales.ceo.pricedifflimit')

    sales_order_approval = fields.Selection([
        ('sales_ceo', 'Sales and CEO'),
        ('sales_agm_ceo', 'Sales, AGM and CEO')
    ], config_parameter='sales.order.approval_level', default=_default_get_sales_order_approval)

    so_sales_per_limit = fields.Float(config_paramter='sales.person.pricedifflimit', default=_default_get_so_sales_per_limit)
    so_agm_per_limit = fields.Float(config_parameter='sales.agm.pricedifflimit', default=_default_get_so_agm_per_limit)
    so_ceo_per_limit = fields.Float(config_parameter='sales.ceo.pricedifflimit', default=_default_get_so_ceo_per_limit)