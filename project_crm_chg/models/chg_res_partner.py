# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from itertools import groupby


class ChgSaleTeam(models.Model):
    _name = 'sale.team'
    _inherit = ['mail.thread.cc','mail.thread.cc']
    _description = "Saleperson team"

    name = fields.Char(string="Team")

class ChgPartnerType(models.Model):
    _name = 'chg.partner.type'
    _inherit = ['mail.thread.cc','mail.thread.cc']
    _description = "Partner type based on Chin Hin development"

    name = fields.Char(string="Type")

class ChgResPartner(models.Model):
    _inherit = 'res.partner'
    _description = "Inherit res partner to group partner based on their role"

    # partner_type = fields.Selection([('developer','Developer'),('maincontractor','Main Contractor'),('subcontractor','Sub Contractor')], string="Partner Type")
    # partner_types = fields.Many2one('chg.partner.type', string="Partner Type")
    # partner_types_name = fields.Char(string="Partner Type Name")
    project_count = fields.Integer("Project", compute='_compute_project_count')
    project_count_ids = fields.Many2many('master.project', compute="_compute_project_count", string='Projects Count', help='Technical field used for stat button')
    ssm_reg_number = fields.Char("Business Reg. Number")
    comp_address = fields.Char("Address")

    # contact_name = fields.Char("Contact Name")
    # contact_role = fields.Char("Contact Role")
    town = fields.Char("Town")
    state = fields.Char("Province")
    postcode = fields.Char("Postcode")
    country = fields.Char("Country")
    firm_id = fields.Char("Firm ID")
    # contact_fax = fields.Char("Fax")
    registration_id = fields.Char("Registration ID")
    # division = fields.Selection([('fd','FD'),('td','TD')])
    bu = fields.Many2one('res.company',string='Business Unit')
    # partner_id = fields.many2one('crm.lead','partner_id', string="Partner")
    bu_lines_master_id = fields.Many2one('crm.lead', string='Master Project', ondelete='cascade', index=True, copy=False)
    


    # def _get_data_same_value(self):
    #     partner = self.env['res.partner'].read_group([('partner_id', 'in', self.ids)], ['name'])
    #     # groups = self.read_group(cr, uid, [], ['name'], ['name'])
    #     # duplicate_names = [g['name'] for g in groups if g['name_count'] > 1]
    #     keyfunc = lambda r: r.name
    #     # for part in partner:
    #     partner_banks = sorted(partner_banks, key=keyfunc)
    #     for k, g in groupby(partner_banks, keyfunc):


    # @api.onchange('partner_types')
    # def _get_partner_type_name(self):
    #     self.partner_types_name = self.partner_types.name or ''

    def _compute_project_count(self):
        for p in self:
            # p.project_count_ids = self.env['master.project'].search(['|','|',('project_developer1', '=', p.id),('project_developer2', '=', p.id),('project_architect1', '=', p.id),('project_architect2', '=', p.id)])
            # if(p.partner_type.name == ''):
            p.project_count_ids = self.env['master.project'].search(['|','|','|',('project_developer1', '=', p.id),('project_architect1', '=', p.id),('project_quantity_surveyor1', '=', p.id),('project_main_contractor1', '=', p.id)])
            p.project_count = len(p.project_count_ids)

    def action_view_project(self):
        '''
        This function returns an action that displays the leads from project.
        '''
        action = self.env.ref('project_crm_chg.master_project_action').read()[0]
        action['domain'] = [('id', 'in', self.project_count_ids.ids)]
        return action

    # def _get_contact_name(self, partner, name):
    #     return "%s, %s" % (partner.commercial_company_name or partner.sudo().parent_id.name, name)

    # def _get_name(self):
    #     """ Utility method to allow name_get to be overrided without re-browse the partner """
    #     partner = self
    #     name = partner.name or ''
    #     # function = partner.function or ''

    #     if partner.company_name or partner.parent_id:
    #         if not name and partner.type in ['invoice', 'delivery', 'other']:
    #             name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
    #         if not partner.is_company:
    #             name = self._get_contact_name(partner, name)
    #     if self._context.get('show_address_only'):
    #         name = partner._display_address(without_company=True)
    #     if self._context.get('show_address'):
    #         name = name + "\n" + partner._display_address(without_company=True)
    #     name = name.replace('\n\n', '\n')
    #     name = name.replace('\n\n', '\n')
    #     if self._context.get('address_inline'):
    #         name = name.replace('\n', ', ')
    #     if self._context.get('show_email') and partner.email:
    #         name = "%s <%s>" % (name, partner.email)
    #     if self._context.get('html_format'):
    #         name = name.replace('\n', '<br/>')
    #     if self._context.get('show_vat') and partner.vat:
    #         name = "%s ‒ %s" % (name, partner.vat)
    #     return name
