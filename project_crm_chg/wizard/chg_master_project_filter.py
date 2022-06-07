# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher


class SearchLeadsByKeywords(models.TransientModel):

    _name = 'searchlead.bykeywords'
    _description = 'Search leads by keywords'

    def _default_lead(self):
        return self.env['crm.lead'].search([])

    # def _default_opportunity_name(self):
    #     val = self.env['master.project'].browse(self._context.get('active_ids'))
    #     return val.name

    def _default_opportunity_keywords(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.project_keywords

    keywords = fields.Char("Keywords",default=_default_opportunity_keywords)

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def search_leads(self):
        view_mode = 'tree'
        tree_view_id = self.env.ref('crm.crm_case_tree_view_leads').id
        leads = self._default_lead()
        # ids = self.env['master.project'].browse(self._context.get('active_ids'))
        
        p_title = []
        new_key = []
        vals = self.keywords
        
        bad_chars = ['!','@','#','$','%','^','&','*','(',')','<','>','?','{','}',':',';','[',']','|','|']
        key_val = r''.join((filter(lambda i: i not in bad_chars, vals)))

        if key_val:
            key = key_val.split()
            for ky in key:
                if len(ky) >= 3:
                    new_key.append(ky)

        existing1 = []
        existing2 = []
        existing3 = []
        existing4 = []

        # for rec in leads:
        #     val1 = self.similar(rec.name,key_val)
        #     if(val1 > 0.3):
        #     # val2 = self.similar(rec.crm_title,vals)
        #         print("RATIO 1::::::: ",rec.name)
        #     if(val1 > 0.4):
        #     # val2 = self.similar(rec.crm_title,vals)
        #         print("RATIO 2::::::: ",rec.name)
        #     if(val1 > 0.5):
        #     # val2 = self.similar(rec.crm_title,vals)
        #         print("RATIO 3::::::: ",rec.name)
        #     # print("RATIO 2::::::: ",val2)


        for l in leads:
            for n in new_key:
                if any(re.findall(''.join(n), l.name, re.IGNORECASE)):
                    existing1.append(l.id)
                if(l.crm_title):
                    if any(re.findall(''.join(n), l.crm_title, re.IGNORECASE)):
                        existing2.append(l.id)
                # if(l.crm_title):
                    if any(re.findall(''.join(vals), l.crm_title, re.IGNORECASE)):
                        existing4.append(l.id)
            if any(re.findall(''.join(vals), l.name, re.IGNORECASE)):
                existing3.append(l.id)

        new_val = []
        for ex1 in existing1:
            for ex2 in existing2:
                if(ex1 == ex2):
                    new_val.append(ex1)

        domain = ['|','|','&',('id','in',existing1),('id','in',existing2),('id','in',existing3),('id','in',existing4)]
        # domain = [('id','in',new_val)]

        return {
            'type': 'ir.actions.act_window',
            'name': _(' Result of ' + '"' + self.keywords + '"' + ' Filtered'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'crm.lead',
            'view_id': False,
            'views': [(self.env.ref('project_crm_chg.crm_case_tree_view_leads_after_wizard').id, 'tree')],
            # 'context': context,
            'domain': domain,
            'target': 'new',
        }





            

