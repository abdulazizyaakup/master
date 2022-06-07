# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher
from itertools import chain
from odoo.exceptions import RedirectWarning


class SearchMasterByKeywords2(models.TransientModel):

    _name = 'searchmaster.bykeywords2'
    _description = 'Search master project by keywords'

    def _default_master(self):
        return self.env['master.project'].search([])

    def _default_master_keywords1(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return str(val.name).upper()

    def _default_master_keywords2(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        if(val.crm_title):
            rec = str(val.crm_title).upper()

            return rec

    keywords1 = fields.Char("Keywords from project Name",default=_default_master_keywords1)
    keywords2 = fields.Char("Keywords from Project Title",default=_default_master_keywords2)

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def search_master(self):
        view_mode = 'tree'
        tree_view_id = self.env.ref('project_crm_chg.crm_project_tree').id
        bci = self._default_master()
        # vals = bci.mapped('')


        
        p_title = []
        new_key1 = []
        new_key2 = []
        keyword1 = self.keywords1
        keyword2 = self.keywords2
        
        bad_chars = ['!','@','#','$','%','^','&','*','(',')','<','>','?','{','}',':',';','[',']','|','|']
        key_val1 = r''.join((filter(lambda i: i not in bad_chars, keyword1)))

        lead_name_to_bci_name = []
        lead_name_to_bci_keyword = []
        lead_title_to_bci_name = []
        lead_title_to_bci_keyword = []


        # for l in leads:
            # for n in new_key1:
            #     if any(re.findall(''.join(n), l.name, re.IGNORECASE)):
            #         existing1.append(l.id)
            #     if(l.crm_title):
            #         if any(re.findall(''.join(n), l.crm_title, re.IGNORECASE)):
                        
        for rec in bci:
            val1 = self.similar(rec.name,key_val1)
            # print("YYY ", key_val1)
            if(val1 > 0.5):
                # print("www ", rec.name, val1)
                lead_name_to_bci_name.append(rec.id)
            val2 = self.similar(rec.project_keywords,key_val1)
            if(val2 > 0.5):
                # print("XXX ", rec.name, val2)
                lead_name_to_bci_keyword.append(rec.id)

        if keyword2:
            key_val2 = r''.join((filter(lambda j: j not in bad_chars, keyword2)))
            # print("XXX ", key_val2)
            for rec2 in bci:
                val3 = self.similar(rec2.name,key_val2)
                if(val3 > 0.5):
                    # print("YYY ", rec2.name, val3)
                    lead_title_to_bci_name.append(rec2.id)
                val4 = self.similar(rec2.project_keywords,key_val2)
                if(val4 > 0.5):
                    # print("ZZZ ", rec2.name, val4)
                    lead_title_to_bci_keyword.append(rec2.id)

        # list_ids = lead_name_to_bci_name+lead_name_to_bci_keyword+lead_title_to_bci_name+lead_title_to_bci_keyword
        
        # list_ids = list(chain(lead_name_to_bci_name, lead_name_to_bci_keyword, lead_title_to_bci_name,lead_title_to_bci_keyword))
        # try:
        #     if(len(list_ids)>0):
        #         domain = ['|','|','&',('id','in',lead_name_to_bci_name),('id','in',lead_name_to_bci_keyword),('id','in',lead_title_to_bci_name),('id','in',lead_title_to_bci_keyword)]
        # except:
        #     print("NOT EXIST")
        lead_id = self.env['crm.lead'].browse(self._context.get('active_ids')).id
        lead_name = self.env['crm.lead'].browse(self._context.get('active_ids')).name
        lead_p_id = self.env['crm.lead'].browse(self._context.get('active_ids')).crm_project_id
        msg = _('Cannot find similar project from Master project list.')
        action1 = self.env.ref('project_crm_chg.crm_project_action')
        action2 = self.env.ref('project_crm_chg.master_project_action')
        domain = ['|','|','&',('id','in',lead_name_to_bci_name),('id','in',lead_name_to_bci_keyword),('id','in',lead_title_to_bci_name),('id','in',lead_title_to_bci_keyword)]
        # if not self.keywords2
        k = self.keywords1 or ''
        l = self.keywords2 or ''
        # print("YYYY ",list_ids)
        # print("XXXX ",len(list_ids))
        # if(len(list_ids)>0):
        return {
            'type': 'ir.actions.act_window',
            'name': _(' Result of ' + '"' + k + '"' + '&' + '"' + l + '"' ' Filtered'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'master.project',
            'view_id': False,
            'views': [(self.env.ref('project_crm_chg.project_master_tree_view_leads_after_wizard').id, 'tree')],
            'context': {'default_lead_id':lead_id,
                        'default_lead_name':lead_name,
                        'default_lead_project_id':lead_p_id,},
            'domain': domain,
            'target': 'new2',
        }
        # else:
        #     raise RedirectWarning(msg, action2.id, _('Create New in Master List'))





            

