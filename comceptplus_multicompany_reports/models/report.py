# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    # Load the right paper format
    def render_qweb_pdf(self, res_ids=None, data=None):
        try:
            company = self.env[self.model].browse(res_ids).company_id
            self.paperformat_id = company.paperformat_id.id
        except:
            pass
        return super(IrActionsReport, self).render_qweb_pdf(res_ids=res_ids, data=data)

    # Load the right paperformat
    @api.model
    def render_qweb_html(self, docids, data=None):
        try:
            company = self.env[self.model].browse(res_ids).company_id
            self.paperformat_id = company.paperformat_id.id
        except:
            pass
        return super(IrActionsReport, self).render_qweb_html(docids=docids, data=data)
