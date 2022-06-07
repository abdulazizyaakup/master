# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class Company(models.Model):
    _inherit = 'res.company'

    paperformat_id = fields.Many2one('report.paperformat', 'Paper format')

    def update_field(self, aux_company=False, aux_field=False, aux_value=False):
        try:
            company_id = self.search([('name', 'ilike', aux_company)], limit=1)
            if company_id:
                vals = {}
                vals[aux_field] = self.env.ref(aux_value).id
                company_id.sudo().write(vals)
        except Exception as e:
            _logger.info("ERROR: %s" % e)
