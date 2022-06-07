# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher
from itertools import chain
from odoo.exceptions import RedirectWarning

class MasterPivotView(models.TransientModel):
	_name = 'master.pivot.view'

    def _default_project(self):
        return self.env['master.project'].browse(self._context.get('active_ids'))

    def _default_bu_ids(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.crmlead_ids

    def _default_opportunity_value(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.bci_related_project


    def open_pivot_view(self):

    	return {
            'type': 'ir.actions.act_window',
            'name': 'Group CRM',
            'res_model': 'master.project',
            'domain': [],
            'view_mode': 'pivot',
            'context': {'default_lead_id':lead_id,
                        'default_lead_name':lead_name,
                        'default_lead_project_id':lead_p_id,
                        },
        }
