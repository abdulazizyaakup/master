# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re

class SearchLeadsByKeywords(models.TransientModel):

    _name = 'search.bykeywords'
    _description = 'Search leads by keywords'

    def _default_lead(self):
        return self.env['crm.lead'].search([])

    keywords = fields.Char("Enter Keyword")

    def search_leads(self):
        view_mode = 'tree'
        tree_view_id = self.env.ref('crm.crm_case_tree_view_leads').id
        # tree_pivot_id = self.env.ref('your_module.your_pivot_view').id
        leads = self._default_lead()
        
        p_title = []
        new_key = []
        
        if self.keywords:
            key = self.keywords.split()
            for ky in key:
                if len(ky) > 3:
                    new_key.append(ky)
        
        # print(new_key)
        existing1 = []
        existing2 = []

        for l in leads:
            if any(re.findall(''.join(new_key), l.name, re.IGNORECASE)):
                # print("Found a match at ID ", l.id)
                existing1.append(l.id)
            if(l.crm_title):
                if any(re.findall(''.join(new_key), l.crm_title, re.IGNORECASE)):
                    # print("Found a match at ID ", l.id)
                    existing2.append(l.id)


        domain = ['|',('id','in',existing1),('id','in',existing2)]


        # return {
        #     'name':_('Existing'),
        #     'view_type': 'tree',
        #     'view_mode':'tree',
        #     'views':self.env.ref('crm.crm_case_tree_view_oppor').id,
        #     'res_model':'crm.lead',
        #     'action':'ir.actions.act_window',
        #     'target':'new',
        #     # 'domain':domain,

        # }
        return {
            'type': 'ir.actions.act_window',
            'name': _(' Result of ' + '"' + self.keywords + '"' + ' Filtered'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'crm.lead',
            'view_id': False,
            'views': [(self.env.ref('starken-crm.crm_case_tree_view_leads_after_wizard').id, 'tree')],
            # 'context': context,
            'domain': domain,
            'target': 'new',
        }

        # return {
        #     'name': _('test'),
        #     'view_type': 'tree',
        #     'view_mode': 'tree',
        #     'view_id': self.env.ref('crm.crm_case_tree_view_oppor').id,
        #     'res_model': 'crm.lead',
        #     'context': "",
        #     'type': 'ir.actions.act_window',
        #     'target': 'new',
        # }




            

