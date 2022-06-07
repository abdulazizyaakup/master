# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher
from itertools import chain
from odoo.exceptions import RedirectWarning


class MidahReport(models.TransientModel):

    _name = 'crm.midah.report'
    _description = 'CRM Midah Group report'

    def _get_allowed_company(self):
        val = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        value = []
        for v in val:
            value.append(v.id)
        
        domain = [('id', 'in', value)]
        return domain

    def _get_default_company(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.company_id.id

    company_id = fields.Many2one('res.company',string="Company",domain=_get_allowed_company)

    def midah_report(self):
        view_mode = 'tree'
        tree_view_id = self.env.ref('project_crm_chg.crm_tree_view_midah_group').id

        return {
            'type': 'ir.actions.act_window',
            'name': _(' Result of Midah custom report'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'view_id': False,
            'views': [(self.env.ref('project_crm_chg.crm_tree_view_midah_group').id, 'tree'),(self.env.ref('crm.crm_lead_view_form').id, 'form')],
            'context': {},
            'domain': [('company_id','in',[3,4,12,13])],
            'target': 'current',
        }





            

