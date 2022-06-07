# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher
from itertools import chain
from odoo.exceptions import RedirectWarning


class SearchFromBCIMaster(models.TransientModel):

    _name = 'searchbcimaster.bycode'
    _description = 'Search bci master project by bci number'

    def _default_bci_master(self):
        return self.env['project.crm'].search([])

    def _default_gcrm_master(self):
        return self.env['master.project'].search([])

    bci_number = fields.Char("BCI Number")


    def search_bci(self):
        bci = self._default_bci_master()
        master = self._default_gcrm_master()
        bci_project_id = self.env['project.crm'].browse(self._context.get('active_ids')).id
        master_project_id = self.env['master.project'].browse(self._context.get('active_ids')).id


        bci_list = []
        master_list = []
        for bc in bci:
            bci_list.append(bc.bci_project_code)

        for m in master:
            master_list.append(m.bci_project_code)

        for b in bci:
            if(self.bci_number in bci_list):

                domain = [('bci_project_code','=',self.bci_number)]
                return {
                    'type': 'ir.actions.act_window',
                    'name': _(' Result'),
                    'view_type': 'form',
                    'view_mode': 'tree, form',
                    'res_model': 'project.crm',
                    'view_id': False,
                    'views': [(self.env.ref('project_crm_chg.project_crm_case_tree_view_leads_after_wizard').id, 'tree'),(self.env.ref('project_crm_chg.crm_project_form').id, 'form')],
                    'context': {'default_project_id':bci_project_id},
                    'domain': domain,
                    'target': 'new',
                }
            if(self.bci_number in master_list):

                domain = [('bci_project_code','=',self.bci_number)]
                return {
                    'type': 'ir.actions.act_window',
                    'name': _(' Result'),
                    'view_type': 'form',
                    'view_mode': 'tree, form',
                    'res_model': 'project.crm',
                    'view_id': False,
                    'views': [(self.env.ref('project_crm_chg.project_master_tree_view_leads_after_wizard').id, 'tree'),(self.env.ref('project_crm_chg.crm_project_form').id, 'form')],
                    'context': {'default_project_id':master_project_id},
                    'domain': domain,
                    'target': 'new',
                }
            if(self.bci_number not in bci_list):
                action = self.env.ref('project_crm_chg.master_project_action_create')
                # action = clean_action(action)
                # domain = [('project_code', '=', b.bci_project_code)]
                # action['domain'] = domain
                msg = _('The following BCI number not exist in the BCI Master List.')
                raise RedirectWarning(msg, action.id, _('Create Project'))

    def search_master(self):
        bci = self._default_gcrm_master()

        bci_list = []
        for bc in bci:
            bci_list.append(bc.bci_project_code)

        for b in bci:
            if(self.bci_number in bci_list):
                domain = [('bci_project_code','=',self.bci_number)]
                return {
                    'type': 'ir.actions.act_window',
                    'name': _(' Result'),
                    'view_type': 'form',
                    'view_mode': 'tree, form',
                    'res_model': 'master.project',
                    'view_id': False,
                    'views': [(self.env.ref('project_crm_chg.project_master_tree_view_leads_after_wizard').id, 'tree'),(self.env.ref('project_crm_chg.crm_project_form').id, 'form')],
                    'context': {},
                    'domain': domain,
                    'target': 'new',
                }
            if(self.bci_number not in bci_list):
                action = self.env.ref('project_crm_chg.master_project_action_create')
                # action = clean_action(action)
                # domain = [('project_code', '=', b.bci_project_code)]
                # action['domain'] = domain
                msg = _('The following BCI number not exist in the Group CRM Master list.')
                raise RedirectWarning(msg, action.id, _('Create Project'))

    def copy_message(self):
        title = _("Record copied from BCI to Group CRM Master!")
        message = _("Copy succeeded!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
            'title': title,
            'message': message,
            'sticky': False,
        }}

