# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher
from itertools import chain
from odoo.exceptions import RedirectWarning


class SearchMasterByKeywords(models.TransientModel):

    _name = 'searchmaster.bykeywords'
    _description = 'Search master project by keywords'

    def _default_master(self):
        return self.env['project.crm'].search([])

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
        dev = self.env['crm.lead'].browse(self._context.get('active_ids')).crm_prj_dev1
        # return str(val.name).upper()
        # vals = bci.mapped('')


        
        p_title = []
        new_key1 = []
        new_key2 = []
        keyword1 = self.keywords1
        keyword2 = self.keywords2
        
        bad_chars = ['!','@','#','$','%','^','&','*','(',')','<','>','?','{','}',':',';','[',']','|','|']
        key_val1 = r''.join((filter(lambda i: i not in bad_chars, keyword1)))

        # print("KEY VAL ", key_val1)

        if key_val1:
            key = key_val1.split()
            for ky in key:
                if len(ky) >= 3:
                    new_key1.append(ky)

        lead_name_to_bci_name = []
        lead_name_to_bci_keyword = []
        lead_title_to_bci_name = []
        lead_title_to_bci_keyword = []
        existing1 = []
        existing2 = []
        existing3 = []
        existing4 = []

        
        for l in bci:
            key_keyword = []
            key_name = []
            bci_keyword = r''.join((filter(lambda f: f not in bad_chars, l.project_keywords)))
            bci_name = r''.join((filter(lambda g: g not in bad_chars, l.name)))
            
            if bci_keyword:
                ke = bci_keyword.split()
                for k in ke:
                    if len(k) >= 3:
                        key_keyword.append(k)

            if bci_name:
                bn = bci_name.split()
                for b in bn:
                    if len(b) >= 3:
                        key_name.append(b)

            # print("AA ",key_keyword )
            # print("BB ",key_name )

            for n in new_key1:
                for o in key_keyword:
                    # print("XXX1 ", o)
                    if len(re.findall(''.join(o), n, re.IGNORECASE)) >= 1:
                        wording1 = self.similar(o,n)
                        if(wording1>=1.0):
                            existing1.append(l.id)
                        # existing1.append(l.id)
                        # print("XXX ", l.name)
                        

                for kn in key_name:
                    # print("YYY2 ", kn)
                    if len(re.findall(''.join(kn), n, re.IGNORECASE)) >= 1:
                        wording2 = self.similar(kn,n)
                        if(wording2>=1.0):
                            existing4.append(l.id)
                        # print("YYY ", l.name)
                        
                        # wording1 = self.similar(n,o)
                #         total = total + 1.0
                #         # print(n, " SIMILAR ",o , " ratio  " ,wording1)
                        
                #         # if (wording1 >= 0.9):
                #         #     total = total + 1.0
                #             # ratio1 = type(wording1)
                            
                #             # print(n, " SIMILAR1 ",o , " ratio1  " ,ratio1)
                #             # total = total + wording1
                #             # existing1.append(l.id)
                #     # print("XXXXXXXXXXXX ", total)
                # if(total >= 1.0):
                #     print(total ,"XXXX ", l.name)

                    if(dev.id == False):
                        if any(re.findall(''.join(n), o, re.IGNORECASE)):
                            wording2 = self.similar(n,o)
                            # print(n, " SIMILAR ",o , " ratio  " ,wording2)
                            if (wording2 == 1.0):
                                value2 = type(wording2)

                                # print(n, " SIMILAR2 ",o , " ratio2  " ,value2)
                                # total = total + wording2
                                # existing1.append(l.id)
                # print("MASTER TOTAL ", total)
                # if total == 1.0:
                #     print("NAME ",l.name)


        for rec in bci:
            for a in dev:    
                if (a.display_name == rec.project_developer1.name):
                    val1 = self.similar(rec.name,key_val1)
                    if(val1 > 0.1):
                        # print("www ", rec.name, val1)
                        lead_name_to_bci_name.append(rec.id)
                    val2 = self.similar(rec.project_keywords,key_val1)
                    if(val2 > 0.1):
                        # print("XXX ", rec.name, val2)
                        lead_name_to_bci_keyword.append(rec.id)


        for rec3 in bci:
            # print("REC 3 NAME  ", rec3.name)
            # for c in dev:    
            val7 = self.similar(rec3.name,key_val1)
            if(val7 > 0.7):
                existing2.append(rec3.id)
            val8 = self.similar(rec3.project_keywords,key_val1)
            if(val8 > 0.7):
                existing3.append(rec3.id)

        if keyword2:
            key_val2 = r''.join((filter(lambda j: j not in bad_chars, keyword2)))
            
            for rec2 in bci:
                # print("FFFF ", rec2.project_developer1.id)
                for b in dev:    
                    if (b.display_name == rec2.project_developer1.name):
                    # print("XXXXXXXXXXXXXX ", b.id)
                        val3 = self.similar(rec2.name,key_val2)
                        if(val3 > 0.1):
                            # print("YYY ", rec2.name, val3)
                            lead_title_to_bci_name.append(rec2.id)
                        val4 = self.similar(rec2.project_keywords,key_val2)
                        if(val4 > 0.1):
                            # print("ZZZ ", rec2.name, val4)
                            lead_title_to_bci_keyword.append(rec2.id)


        in_a = lead_name_to_bci_name
        in_b = lead_name_to_bci_keyword
        in_c = lead_title_to_bci_name
        in_d = lead_title_to_bci_keyword

        in_all = [*lead_name_to_bci_name, *lead_name_to_bci_keyword, *lead_title_to_bci_name, *lead_title_to_bci_keyword]

        lead_id = self.env['crm.lead'].browse(self._context.get('active_ids')).id
        lead_name = self.env['crm.lead'].browse(self._context.get('active_ids')).name
        lead_p_id = self.env['crm.lead'].browse(self._context.get('active_ids')).crm_project_id
        msg = _('Cannot find similar project from BCI project list.')
        action1 = self.env.ref('project_crm_chg.crm_project_action')
        action2 = self.env.ref('project_crm_chg.master_project_action')
        # domain = ['|'('id','in',combine1),('id','in',combine2)]
        # domain = ['&',('id','in',lead_name_to_bci_name),('id','in',existing1)]
        # domain = ['|','|','|','&',('id','in',lead_name_to_bci_name),('id','in',lead_name_to_bci_keyword),('id','in',lead_title_to_bci_name),('id','in',lead_title_to_bci_keyword),('id','in',existing1)]
        if(dev.id == False):
            domain = ['&','|','|',('id','in',existing1),('id','in',existing2),('id','in',existing3),('id','in',existing4)]
        if(dev.id != False):
            domain = ['|','|','|','|',('id','in',lead_name_to_bci_name),('id','in',existing1),('id','in',existing2),('id','in',existing3),('id','in',existing4)]
        if(not lead_name_to_bci_name):
            domain = ['|','|',('id','in',existing2),('id','in',existing2),('id','in',existing4)]  
        if(not lead_name_to_bci_keyword):
            domain = ['|','|',('id','in',existing2),('id','in',existing2),('id','in',existing4)]  
        if(not lead_title_to_bci_name):
            domain = ['|','|',('id','in',existing2),('id','in',existing2),('id','in',existing4)]
        if(not lead_title_to_bci_keyword):
            domain = ['|','|',('id','in',existing2),('id','in',existing2),('id','in',existing4)]   
        if(not existing2):
            domain = ['|','|','|',('id','in',existing1),('id','in',existing2),('id','in',existing3),('id','in',existing4)]
        if(not existing3):
            domain = ['|','|','|',('id','in',existing1),('id','in',existing2),('id','in',existing3),('id','in',existing4)]
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
            'res_model': 'project.crm',
            'view_id': False,
            'views': [(self.env.ref('project_crm_chg.project_crm_case_tree_view_leads_after_wizard').id, 'tree'),(self.env.ref('project_crm_chg.crm_project_form').id, 'form')],
            'context': {'default_lead_id':lead_id,
                        'default_lead_name':lead_name,
                        'default_lead_project_id':lead_p_id,
                        },
            'domain': domain,
            'target': 'new2',
        }
        # else:
        #     raise RedirectWarning(msg, action2.id, _('Create New in Master List'))





            

