# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID,_
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import RedirectWarning
import re

class BuPlant(models.Model):
    _name = 'bu.plant'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'BU Plant'

    @api.model
    def _getCurrentCompanyIdUserDomain(self):
        return [('user_ids','!=',False), ('user_ids.share','=',False), ('type','=','contact'), ('company_type','!=','company')]


    name = fields.Char('Plant')
    bu_id = fields.Many2one('res.company', string='Company', index=True)
    active = fields.Boolean('Active', default=True)
    plant_id = fields.Char('Plant ID')
    branch_code = fields.Char('Branch Code')
    branch_partner_link = fields.Many2one('res.partner', string='Branch Address', ondelete="cascade", domain="[('parent_id', '=', False), ('type','=','contact'), ('company_type','=','company')]")
    brnch_managers = fields.Many2many('res.partner','branches_managers_res_partner_rel', 'br_id', 'pr_id',  string='Branch Manager', domain=_getCurrentCompanyIdUserDomain)
    # brnch_hoscs = fields.Many2many('res.partner','branches_hoscs_res_partner_rel', 'br_id', 'pr_id', string='Sales Coordinator', domain=_getCurrentCompanyIdUserDomain)
    brnch_steams = fields.Many2many('res.partner','branches_steams_res_partner_rel', 'br_id', 'pr_id', string='Branch Sales Team', domain=_getCurrentCompanyIdUserDomain)
    bran = fields.Many2many('res.partner','bu_plant_manager_rel', 'br_id', 'pr_id', string='Branch Sales Team', domain=_getCurrentCompanyIdUserDomain)

    
    # address_state = fields.Many2one('res.country.state', 'Branch State', related='branch_partner_link.state_id', readonly=True, store=True)
    # reply_to_email_addr = fields.Char('Reply-To Email Address')
    # bank_account = fields.Char('Bank Account No')
    

class CrmProjectLevel(models.Model):
    _name = 'crm.project.level'
    _order = "sequence"
    _description = 'Project Level'

    name = fields.Char('Level')
    sequence = fields.Integer('Sequence', default=1)
    parent = fields.Many2one('crm.project.level',string="Parent")
    parent_id = fields.Many2one('crm.project.level',string="Parent (GSM Level)")
    definition = fields.Text('Parent(GSM Level) Definition')
    company_id = fields.Many2one('res.company',string="Company")

class ChgCrmLeads(models.Model):
    _inherit = 'crm.lead'

    def _get_default_level(self):
        
        val = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        value = []
        for v in val:
            value.append(v.id)
        
        level = [('company_id', 'in', value)]
        return level

    def _get_default_sub_level(self):
        
        val = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        value = []
        for v in val:
            value.append(v.id)
        level = [('parent.id', '=', value)]
        return level            


    def _get_non_existing_master(self):
        existing_leads = self.env['crm.lead'].search([])
        non_exist_in_master = []

        for el in existing_leads:
            if el.crm_bci_id:
                non_exist_in_master.append(el.crm_bci_id)
        return non_exist_in_master

    @api.depends('crm_project_level')
    def _compute_crm_project_level_name(self):
        if self.crm_project_level:
            self.crm_project_level_name = self.crm_project_level.name
        else:
            self.crm_project_level_name = False


    crm_project_level_name = fields.Char('CRM Project Level Name',compute='_compute_crm_project_level_name')
    crm_prj_val = fields.Float("BU Project Value (Million)")
    bci_prj_val = fields.Float("BCI Project Value (Million)")
    gsm_lead = fields.Boolean(string="GSM Lead", default=False)
    master_bci_related = fields.Many2one('project.crm', related='master_id.bci_related_project',string="BCI Related",store=True)
    master_id = fields.Many2one('master.project', string="Master Project",store=True)
    sub_master_id = fields.Many2one('crm.lead', string="Master Lead",store=True)
    bu_id = fields.Many2one('res.company', string="Business Unit")
    checked_by_id = fields.Many2one('res.users', string="Checked By", index=True, tracking=True)
    assign_checked_by_id = fields.Many2one('res.users', string="Assigned to", index=True, tracking=True)
    checked_remark = fields.Char("Checked Remark")
    crmsublead_ids = fields.One2many('crm.lead', 'sub_master_id',string="BU Project ID",store=True)
    bci_province1 = fields.Char(related='master_bci_related.province1',string='Province')
    bci_region = fields.Char(related='master_bci_related.bci_region',string="BCI Region")
    bci_ownership_type = fields.Many2one(related='master_bci_related.project_owner_type',string="BCI Ownership Type")
    bci_project_category = fields.Many2one(related='master_bci_related.project_category1', string="BCI Project Category")
    bci_project_categories = fields.Many2many('project.crm.category', string="BCI Categories")#fields.Many2many('project.crm.category', 'bci_categories_rel', 'project_id', 'categories_id', string='BCI Categories')
    bci_project_stage = fields.Many2one(related='master_bci_related.project_stage_id', string="BCI Project Stage")
    bci_project_status = fields.Many2one(string="BCI Project Status")
    bci_project_value = fields.Char(string="BCI Project Value(Million)")
    bci_start_date = fields.Date(related='master_bci_related.start_date',string="BCI Start Date")
    bci_end_date = fields.Date(related='master_bci_related.end_date',string="BCI End Date")
    bci_project_remarks = fields.Text(related='master_bci_related.project_remarks',string="BCI Project Remarks")
    bci_element_info = fields.Text(related='master_bci_related.element_info',string="BCI Element Info")
    bci_name = fields.Char("BCI Name")
    bci_no_storeys = fields.Char(related='master_bci_related.project_building_storeys',string="No. Of Storeys")
    bci_complete_status = fields.Boolean(string="Completed Status", default=False)
    bci_complete_status_name = fields.Char("BCI Status", store=True)
    quotation_ids = fields.One2many('crm.lead.quotation','quotation_id',string="Quotations")
    bu_remarks = fields.Text(string='Remarks')
    parent_project_level = fields.Many2one('crm.project.level', string="GSM Project Level")
    crm_project_level = fields.Many2one('crm.project.level',string="Project Level",domain=_get_default_level)
    sub_crm_project_level = fields.Many2one('crm.project.level', string="Sub-Project Level")
    company_name = fields.Char("Company Name",compute='get_company_name')
    team_id2 = fields.Many2one('crm.team', string='Team')
    potential_value_filter = fields.Monetary(related='quotation_ids.potential_value',string="Potential Value", currency_field='company_currency', tracking=True, store=True)
    project_progress_filter = fields.Char(related='quotation_ids.project_progress',string="Progress (%)",store=True)
    developer_filter = fields.Char(related='crm_prj_dev1.name',string="Developer",store=True)
    architect_filter = fields.Char(related='crm_prj_arc1.name',string="Architect",store=True)
    contractor_filter = fields.Char(related='crm_cntrctrs.name',string="Contractor",store=True)
    qs_filter = fields.Char(related='crm_prj_qs1.name',string="Quantity Surveyor",store=True)
    ec_filter = fields.Char(related='crm_trdng_hses.name',string="Epicor Customer",store=True)
    ce_filter = fields.Char(related='crm_prj_cseng1.name',string="Consultant Engineer",store=True)
    distributor_filter = fields.Char(related='crm_prj_distributor.name',string="Distributor",store=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    # trigger_categories_value = fields.Float(compute="_set_category_many2many")
    
# _auto_set_bci_value

    @api.depends('master_id')
    @api.onchange('master_id')
    def _set_category_many2many(self):
        # bci = self.env['master.project'].search([])

        for b in self.master_id:
            if(b.project_category1):
                b.bci_project_categories = [(4, b.project_category1.id)]
            if(b.project_category2):
                b.bci_project_categories = [(4, b.project_category2.id)]
            if(b.project_category3):
                b.bci_project_categories = [(4, b.project_category3.id)]
            if(b.project_category4):
                b.bci_project_categories = [(4, b.project_category4.id)]
            if(b.project_category5):
                b.bci_project_categories = [(4, b.project_category5.id)]
            if(b.project_category6):
                b.bci_project_categories = [(4, b.project_category6.id)]
            if(b.project_category7):
                b.bci_project_categories = [(4, b.project_category7.id)]
            if(b.project_category8):
                b.bci_project_categories = [(4, b.project_category8.id)]
            if(b.project_subcategory1):
                b.bci_project_categories = [(4, b.project_subcategory1.id)]
            if(b.project_subcategory2):
                b.bci_project_categories = [(4, b.project_subcategory2.id)]
            if(b.project_subcategory3):
                b.bci_project_categories = [(4, b.project_subcategory3.id)]
            if(b.project_subcategory4):
                b.bci_project_categories = [(4, b.project_subcategory4.id)]
            if(b.project_subcategory5):
                b.bci_project_categories = [(4, b.project_subcategory5.id)]
            if(b.project_subcategory6):
                b.bci_project_categories = [(4, b.project_subcategory6.id)]
            if(b.project_subcategory7):
                b.bci_project_categories = [(4, b.project_subcategory7.id)]
            if(b.project_subcategory8):
                b.bci_project_categories = [(4, b.project_subcategory8.id)]

    @api.onchange('crm_project_level')
    #@api.depends('crm_project_level')
    def get_parent_level(self):
        if(self.crm_project_level):
            #self.parent_project_level = self.crm_project_level.parent_id.id
            # return {'domain': {'sub_crm_project_level': [('parent', '=', self.parent_project_level.id)]}}
        # for l in self.crm_project_level:
            val = self.crm_project_level.parent_id.id
            self.write({'parent_project_level':val})
            #return val

    @api.onchange('bci_prj_val')
    def get_bci_float_p_value(self):
        if(self.bci_prj_val):
            return self.get_project_value()

    @api.onchange('crm_prj_val')
    def get_bu_float_p_value(self):
        if(self.crm_prj_val):
            return self.get_project_value()

    @api.onchange('crm_project_level')
    def onchange_sub_crm_project_level(self):
        return {'domain': {'sub_crm_project_level': [
            ('parent.id',
             'in',
             self.mapped('crm_project_level.id')
             )]
        }
        }

    def get_project_value(self):
        lead = self.env['crm.lead'].search([])
        for l in lead:
            if(l.crm_prj_value):
                val1 = re.sub('[^\d\.]', '', l.crm_prj_value) 
                l.write({'crm_prj_val':float(val1)})
            if(not l.crm_prj_value):
                l.write({'crm_prj_val':float(0.00)})
            if(l.bci_project_value):
                val2 = re.sub('[^\d\.]', '', l.bci_project_value)
                l.write({'bci_prj_val':float(val2)})
            if(not l.bci_project_value):
                l.write({'bci_prj_val':float(0.00)})

    def click_parent_level(self):
        lead = self.env['crm.lead'].search([])
        for l in lead:
            if(l.crm_project_level):
                l.parent_project_level = l.crm_project_level.parent_id.id

    def copy_non_bci_to_master(self):
        non_bci_lead = self.env['crm.lead'].search([])
        master = self.env['master.project'].search([])

        for b in non_bci_lead:            
            if(not b.master_id):
                if(not b.crm_bci_id):
                    self.env['master.project'].create({
                            'name':b.name,
                            'is_bci_project':False,
                            'project_value':b.crm_prj_value,
                    })

    def set_master_id(self):
        master = self.env['master.project'].search([])
        non_bci_lead = self.env['crm.lead'].search([])
        
        for a in non_bci_lead:
            if(not a.crm_bci_id):
                for m in master:
                    if(m.name == a.name):
                        a.write({'master_id': m.id})

    # @api.depends('company_id')
    # def get_company_name(self):
    #     if self.company_id:
    #         self.company_name = self.company_id.name

    @api.depends('crm_bci_id')
    def get_province(self):
        master = self.env['master.project'].search([])
        lead = self.env['crm.lead'].search([])
        # if self.crm_bci_id:
        for m in master:
            for l in lead:
                if m.bci_project_code == l.crm_bci_id:
                    l.bci_province1 = m.province1

    @api.depends('crm_bci_id')
    def link_master(self):
        master = self.env['master.project'].search([])
        lead = self.env['crm.lead'].search([])
        # if self.crm_bci_id:
        for m in master:
            for l in lead:
                if l.crm_bci_id:
                    if m.bci_project_code == l.crm_bci_id:
                        l.master_id = m.id
                        # self.write({'master_id':m.id})
                    # l.master_bci_related = m.bci_related_project.id
                    # return self.write({'master_id':m.id})


    @api.depends('company_id')
    def auto_get_bu(self):
        if self.company_id:
            return self.update({'bu_id':self.company_id})

    @api.depends('crm_project_id')
    def set_gsm_id(self):
        leads = self.env['crm.lead'].search([])

        for l in leads:
            if(not l.sub_project_code):
                if(l.master_id):
                    l.write({"sub_project_code": l.master_id.project_code})
                if(not l.master_id):
                    l.write({"sub_project_code": False})

    @api.depends('sub_project_code')
    def set_project_id(self):
        leads = self.env['crm.lead'].search([])

        for l in leads:
            if l.sub_project_code:
                if not l.crm_project_id:
                    l.write({"crm_project_id": l.sub_project_code})

    @api.depends('master_bci_related')
    # @api.onchange('master_bci_related')
    def _auto_set_bci_value(self):
        # print("XXXXXXXXXX  ccccc  dddd  ", self.master_bci_related.name)
        for rec in self:
            if(rec.master_bci_related):
                rec.bci_province1 = rec.master_bci_related.province1
                rec.bci_no_storeys = rec.master_bci_related.project_building_storeys
                rec.bci_region = rec.master_bci_related.bci_region
                rec.bci_ownership_type = rec.master_bci_related.project_owner_type.id
                rec.bci_project_status = rec.master_bci_related.project_status_description
                rec.bci_project_category = rec.master_bci_related.project_category1.id
                rec.bci_project_stage = rec.master_bci_related.project_stage_id.id
                rec.bci_project_value = rec.master_bci_related.project_value
                rec.bci_start_date = rec.master_bci_related.start_date
                rec.bci_end_date = rec.master_bci_related.end_date
                rec.bci_project_remarks = rec.master_bci_related.project_remarks
                rec.bci_element_info = rec.master_bci_related.element_info
                rec.crm_prj_dev1 = [(6,0, rec.master_bci_related.project_developer1.ids)]
                rec.crm_prj_arc1 = [(6,0, rec.master_bci_related.project_architect1.ids)]
                rec.crm_prj_cseng1 = [(6,0, rec.master_bci_related.consulting_engineer1.ids)]
                rec.crm_prj_qs1 = [(6,0, rec.master_bci_related.project_quantity_surveyor1.ids)]
                rec.crm_cntrctrs = [(6,0, rec.master_bci_related.project_main_contractor1.ids),(6,0, self.master_bci_related.project_main_contractor2.ids),(6,0, self.master_bci_related.contractor1.ids),(6,0, self.master_bci_related.turnkey_contractor1.ids)]
                rec.crm_sbcns_aplctrs = [(6,0, rec.master_bci_related.project_sub_contractor1.ids)]
            # a.write({
            #             'bci_province1':b.province1,
            #             'bci_region': b.bci_region,
            #             'bci_ownership_type': b.project_owner_type.id,
            #             'bci_project_category': b.project_category1.id,
            #             'bci_project_stage': b.project_stage_id.id,
            #             # 'bci_project_status': b.project_status.id,
            #             'bci_project_value': b.project_value,
            #             'bci_start_date': b.start_date,
            #             'bci_end_date': b.end_date,
            #             'bci_project_remarks': b.project_remarks,
            #             'bci_element_info': b.element_info,
            #             'crm_prj_dev1':[(6,0, b.project_developer1.ids)],
            #             'crm_prj_arc1':[(6,0, b.project_architect1.ids)],
            #             'crm_prj_cseng1':[(6,0, b.consulting_engineer1.ids)],
            #             'crm_prj_qs1':[(6,0, b.project_quantity_surveyor1.ids)],
            #             'crm_cntrctrs':[(6,0, b.project_main_contractor1.ids),(6,0, b.project_main_contractor2.ids),(6,0, b.contractor1.ids),(6,0, b.turnkey_contractor1.ids)],
            #             'crm_sbcns_aplctrs':[(6,0, b.project_sub_contractor1.ids)],
            #             # 'master_id': b,
            #             })

    @api.depends('crm_bci_id')
    def copy_from_bci_to_leads(self):
        non_exist = self._get_non_existing_master()
        master = self.env['master.project'].search([])
        bci = self.env['project.crm'].search([])
        leads = self.env['crm.lead'].search([])
        # self.ensure_one()
        existing_master = []

        bci_list = []
        for b in bci:
            bci_list.append(b.bci_project_code)

        not_in_bci = []
        for ne in non_exist:
            if(ne in bci_list):
                not_in_bci.append(ne)
                
        for a in leads:
            for b in bci:
                if(b.bci_project_code == a.crm_bci_id):
                    a.write({
                        'bci_province1':b.province1,
                        'bci_region': b.bci_region,
                        'bci_ownership_type': b.project_owner_type.id,
                        'bci_project_category': b.project_category1.id,
                        'bci_project_stage': b.project_stage_id.id,
                        # 'bci_project_status': b.project_status.id,
                        'bci_project_value': b.project_value,
                        'bci_start_date': b.start_date,
                        'bci_end_date': b.end_date,
                        'bci_project_remarks': b.project_remarks,
                        'bci_element_info': b.element_info,
                        'crm_prj_dev1':[(6,0, b.project_developer1.ids)],
                        'crm_prj_arc1':[(6,0, b.project_architect1.ids)],
                        'crm_prj_cseng1':[(6,0, b.consulting_engineer1.ids)],
                        'crm_prj_qs1':[(6,0, b.project_quantity_surveyor1.ids)],
                        #'crm_cntrctrs':[(6,0, b.project_main_contractor1.ids),(6,0, b.project_main_contractor2.ids),(6,0, b.contractor1.ids),(6,0, b.turnkey_contractor1.ids)],
                        'crm_cntrctrs':[(6,0, b.project_main_contractor1.ids)],
                        'crm_cntrctrs':[(6,0, b.project_main_contractor2.ids)],
                        'crm_cntrctrs':[(6,0, b.contractor1.ids)],
                        'crm_cntrctrs':[(6,0, b.turnkey_contractor1.ids)],
                        'crm_sbcns_aplctrs':[(6,0, b.project_sub_contractor1.ids)],
                        # 'master_id': b,
                        })

        # for a in leads:
        #     for b in bci:
        #         if(b.bci_project_code == a.crm_bci_id):
        #             # a.crm_prj_dev1 = [(4,a.id,b.project_developer1.id)]
        #             # print("VALUE  ::: ",b.id)
        #             a.write({
        #                 'crm_prj_dev1':[(6,0,a.id,b.project_developer1.id)]
        #             })
                        # 'name':b.name,
                        # 'project_keywords':b.project_keywords,
                        # 'project_code':'',
                        # 'bci_project_code':b.bci_project_code,
                        # 'street':b.street,
                        # 'street2':b.street2,
                        # 'city':b.city,
                        # 'state_id':b.state_id.id,
                        # 'zip':b.zip,
                        # 'country_id':b.country_id.id,
                        # 'bci_name':b.name,
                        # 'bci_region':b.bci_region,
                        # 'bci_ownership_type':b.project_owner_type.id,
                        # 'project_development_type':b.project_development_type.id,
                        # 'project_site_area':b.project_site_area,
                        # 'project_floor_area':b.project_floor_area,
                        # 'project_building_storeys':b.project_building_storeys,
                        # 'project_timestamp':b.project_timestamp,
                        # 'project_refid':b.project_refid,
                        # 'project_version':b.project_version,
                        # 'bci_start_date':b.start_date,
                        # 'bci_end_date':b.end_date,
                        # 'bci_project_value':b.project_value,
                        # 'company_id':b.company_id.id,
                        # 'timetable_remarks':b.timetable_remarks,
                        # 'foreign_participation':b.foreign_participation,
                        # 'major':b.major,
                        # 'project_last':b.project_last,
                        # 'project_green_building_rating':b.project_green_building_rating,
                        # 'project_status_description':b.project_status_description,
                        # 'project_units_residential':b.project_units_residential,
                        # 'project_units_industrial':b.project_units_industrial,
                        # 'bci_project_category':b.project_category1.id,
                        # 'project_category2':b.project_category2.id,
                        # 'project_category3':b.project_category3.id,
                        # 'project_category4':b.project_category4.id,
                        # 'project_category5':b.project_category5.id,
                        # 'project_category6':b.project_category6.id,
                        # 'project_category7':b.project_category7.id,
                        # 'project_category8':b.project_category8.id,
                        # 'project_subcategory1':b.project_subcategory1.id,
                        # 'project_subcategory2':b.project_subcategory2.id,
                        # 'project_subcategory3':b.project_subcategory3.id,
                        # 'project_subcategory4':b.project_subcategory4.id,
                        # 'project_subcategory5':b.project_subcategory5.id,
                        # 'project_subcategory6':b.project_subcategory6.id,
                        # 'project_subcategory7':b.project_subcategory7.id,
                        # 'project_subcategory8':b.project_subcategory8.id,
                        # 'project_developer1':b.project_developer1.id,
                        # 'project_developer2':b.project_developer2.id,
                        # 'project_developer1_contact1':b.project_developer1_contact1.id,
                        # 'project_developer1_contact2':b.project_developer1_contact2.id,
                        # 'project_developer2_contact1':b.project_developer2_contact1.id,
                        # 'project_developer2_contact2':b.project_developer2_contact2.id,
                        # 'project_architect1':b.project_architect1.id,
                        # 'project_architect2':b.project_architect2.id,
                        # 'project_architect1_contact1':b.project_architect1_contact1.id,
                        # 'project_architect1_contact2':b.project_architect1_contact2.id,
                        # 'project_architect2_contact1':b.project_architect2_contact1.id,
                        # 'project_architect1_contact2':b.project_architect2_contact2.id,
                        # 'consulting_engineer1':b.consulting_engineer1.id,
                        # 'consulting_engineer2':b.consulting_engineer2.id,
                        # 'consulting_engineer1_contact1':b.consulting_engineer1_contact1.id,
                        # 'consulting_engineer1_contact2':b.consulting_engineer1_contact2.id,
                        # 'consulting_engineer2_contact1':b.consulting_engineer2_contact1.id,
                        # 'consulting_engineer2_contact2':b.consulting_engineer2_contact2.id,
                        # 'consultant1':b.consultant1.id,
                        # 'consultant1_contact1':b.consultant1_contact1.id,
                        # 'consultant1_contact2':b.consultant1_contact2.id,
                        # 'green_building_consultant1':b.green_building_consultant1.id,
                        # 'green_building_consultant1_contact1':b.green_building_consultant1_contact1.id,
                        # 'green_building_consultant1_contact2':b.green_building_consultant1_contact2.id,
                        # 'project_quantity_surveyor1':b.project_quantity_surveyor1.id,
                        # 'project_quantity_surveyor1_contact1':b.project_quantity_surveyor1_contact1.id,
                        # 'project_quantity_surveyor1_contact2':b.project_quantity_surveyor1_contact2.id,
                        # 'project_main_contractor1':b.project_main_contractor1.id,
                        # 'project_main_contractor1_contact1':b.project_main_contractor1_contact1.id,
                        # 'project_main_contractor1_contact2':b.project_main_contractor1_contact2.id,
                        # 'project_main_contractor2':b.project_main_contractor2.id,
                        # 'project_main_contractor2_contact1':b.project_main_contractor2_contact1.id,
                        # 'project_main_contractor2_contact2':b.project_main_contractor2_contact2.id,
                        # 'contractor1':b.contractor1.id,
                        # 'contractor1_contact1':b.contractor1_contact1.id,
                        # 'contractor1_contact2':b.contractor1_contact2.id,
                        # 'project_sub_contractor1':b.project_sub_contractor1.id,
                        # 'project_sub_contractor1_contact1':b.project_sub_contractor1_contact1.id,
                        # 'project_sub_contractor1_contact2':b.project_sub_contractor1_contact2.id,
                        # 'turnkey_contractor1':b.turnkey_contractor1.id,
                        # 'turnkey_contractor1_contact1':b.turnkey_contractor1_contact1.id,
                        # 'turnkey_contractor1_contact2':b.turnkey_contractor1_contact2.id,
                        # 'project_owner1':b.project_owner1.id,
                        # 'project_owner1_contact1':b.project_owner1_contact1.id,
                        # 'project_owner1_contact2':b.project_owner1_contact2.id,
                        # 'bci_project_remarks':b.project_remarks,
                        # 'bci_element_info':b.element_info,

                # })


    @api.depends('crm_bci_id')
    def copy_from_bci_to_master(self):
        non_exist = self._get_non_existing_master()
        master = self.env['master.project'].search([])
        bci = self.env['project.crm'].search([])
        leads = self.env['crm.lead'].search([])
        # self.ensure_one()
        existing_master = []

        for m in master:
            existing_master.append(m.bci_project_code)

        bci_list = []
        for b in bci:
            bci_list.append(b.bci_project_code)

        not_in_bci = []
        for ne in non_exist:
            if(ne not in bci_list):
                not_in_bci.append(ne)

        new_list = []
        for a in non_exist:
            if(a not in existing_master):
                new_list.append(a)

        for b in bci:
            if(b.bci_project_code in new_list):
                self.env['master.project'].sudo().create({
                        'name':b.name,
                        'is_bci_project': True,
                        'stage_id':'validated',
                        'province1':b.province1,
                        'project_keywords':b.project_keywords,
                        # 'project_code':'',
                        'bci_project_code':b.bci_project_code,
                        'street':b.street,
                        'street2':b.street2,
                        'city':b.city,
                        'state_id':b.state_id.id,
                        'zip':b.zip,
                        'country_id':b.country_id.id,
                        'bci_region':b.bci_region,
                        'project_owner_type':b.project_owner_type.id,
                        'project_development_type':b.project_development_type.id,
                        'project_site_area':b.project_site_area,
                        'project_floor_area':b.project_floor_area,
                        'project_building_storeys':b.project_building_storeys,
                        'project_timestamp':b.project_timestamp,
                        'project_refid':b.project_refid,
                        'project_version':b.project_version,
                        'start_date':b.start_date,
                        'end_date':b.end_date,
                        'project_value':b.project_value,
                        'company_id':b.company_id.id,
                        'timetable_remarks':b.timetable_remarks,
                        'foreign_participation':b.foreign_participation,
                        'major':b.major,
                        'project_last':b.project_last,
                        'project_green_building_rating':b.project_green_building_rating,
                        'project_status_description':b.project_status_description,
                        'project_units_residential':b.project_units_residential,
                        'project_units_industrial':b.project_units_industrial,
                        'project_category1':b.project_category1.id,
                        'project_category2':b.project_category2.id,
                        'project_category3':b.project_category3.id,
                        'project_category4':b.project_category4.id,
                        'project_category5':b.project_category5.id,
                        'project_category6':b.project_category6.id,
                        'project_category7':b.project_category7.id,
                        'project_category8':b.project_category8.id,
                        'project_subcategory1':b.project_subcategory1.id,
                        'project_subcategory2':b.project_subcategory2.id,
                        'project_subcategory3':b.project_subcategory3.id,
                        'project_subcategory4':b.project_subcategory4.id,
                        'project_subcategory5':b.project_subcategory5.id,
                        'project_subcategory6':b.project_subcategory6.id,
                        'project_subcategory7':b.project_subcategory7.id,
                        'project_subcategory8':b.project_subcategory8.id,
                        'project_developer1':b.project_developer1.id,
                        'project_developer2':b.project_developer2.id,
                        'project_developer1_contact1':b.project_developer1_contact1.id,
                        'project_developer1_contact2':b.project_developer1_contact2.id,
                        'project_developer2_contact1':b.project_developer2_contact1.id,
                        'project_developer2_contact2':b.project_developer2_contact2.id,
                        'project_architect1':b.project_architect1.id,
                        'project_architect2':b.project_architect2.id,
                        'project_architect1_contact1':b.project_architect1_contact1.id,
                        'project_architect1_contact2':b.project_architect1_contact2.id,
                        'project_architect2_contact1':b.project_architect2_contact1.id,
                        'project_architect1_contact2':b.project_architect2_contact2.id,
                        'consulting_engineer1':b.consulting_engineer1.id,
                        'consulting_engineer2':b.consulting_engineer2.id,
                        'consulting_engineer1_contact1':b.consulting_engineer1_contact1.id,
                        'consulting_engineer1_contact2':b.consulting_engineer1_contact2.id,
                        'consulting_engineer2_contact1':b.consulting_engineer2_contact1.id,
                        'consulting_engineer2_contact2':b.consulting_engineer2_contact2.id,
                        'consultant1':b.consultant1.id,
                        'consultant1_contact1':b.consultant1_contact1.id,
                        'consultant1_contact2':b.consultant1_contact2.id,
                        'green_building_consultant1':b.green_building_consultant1.id,
                        'green_building_consultant1_contact1':b.green_building_consultant1_contact1.id,
                        'green_building_consultant1_contact2':b.green_building_consultant1_contact2.id,
                        'project_quantity_surveyor1':b.project_quantity_surveyor1.id,
                        'project_quantity_surveyor1_contact1':b.project_quantity_surveyor1_contact1.id,
                        'project_quantity_surveyor1_contact2':b.project_quantity_surveyor1_contact2.id,
                        'project_main_contractor1':b.project_main_contractor1.id,
                        'project_main_contractor1_contact1':b.project_main_contractor1_contact1.id,
                        'project_main_contractor1_contact2':b.project_main_contractor1_contact2.id,
                        'project_main_contractor2':b.project_main_contractor2.id,
                        'project_main_contractor2_contact1':b.project_main_contractor2_contact1.id,
                        'project_main_contractor2_contact2':b.project_main_contractor2_contact2.id,
                        'contractor1':b.contractor1.id,
                        'contractor1_contact1':b.contractor1_contact1.id,
                        'contractor1_contact2':b.contractor1_contact2.id,
                        'project_sub_contractor1':b.project_sub_contractor1.id,
                        'project_sub_contractor1_contact1':b.project_sub_contractor1_contact1.id,
                        'project_sub_contractor1_contact2':b.project_sub_contractor1_contact2.id,
                        'turnkey_contractor1':b.turnkey_contractor1.id,
                        'turnkey_contractor1_contact1':b.turnkey_contractor1_contact1.id,
                        'turnkey_contractor1_contact2':b.turnkey_contractor1_contact2.id,
                        'project_owner1':b.project_owner1.id,
                        'project_owner1_contact1':b.project_owner1_contact1.id,
                        'project_owner1_contact2':b.project_owner1_contact2.id,
                        'project_remarks':b.project_remarks,
                        'element_info':b.element_info,

                })
                # print("BCI ID  ::: ",)
                        # except:    
                        #     pass
        
        # return create    
class CrmQProductGroup(models.Model):
    _name = 'product.quotation.group'

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', index=True)


class CrmLeadQuotation(models.Model):
    _name = 'crm.lead.quotation'
    _description = 'Quotation attachments'

    name = fields.Char('Name')
    quotation_id = fields.Many2one('crm.lead',string="Lead")
    quote_to = fields.Many2one('res.partner', string='Quote To')
    product_group = fields.Many2one('product.quotation.group',string="Product Group")
    potential_value = fields.Monetary(string='Potential Value', currency_field='company_currency', tracking=True, store=True)
    quotation_attachment = fields.Binary(string='Quotation Attachment',attachment=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    created_by = fields.Many2one('res.users',string="Upload By",index=True, tracking=2, default=lambda self: self.env.user)
    project_progress = fields.Char(string='Progress(%)')

class AssignCheckerWizard(models.TransientModel):
    _name = "crm.lead.assign.wizard"
    _description = "Update the phase for multi payemnt"

   # define the phase field which you will use to change the phase for the selected payments, for example if the phase field is a selection
    user = fields.Many2one("res.users", string="User")

    # method update_payments_phase which will be called from wizard once click on Update phase button
    def assign_checker(self):
        # return all selected payments using active_ids and you can filter them and use any validation you want
        # user = self.env['res.users'].search(['name','=','Hgliew']).id
        alll = self.env['crm.lead'].browse(self._context.get('active_ids'))
        # loop the payments
        for a in alll:
            a.assign_checked_by_id = self.user
            # for u in user:
            #     if(u.login == 'hgliew98@gmail.com'):
            # # set the selected phase for each payment
            #         a.sudo().write({a.assign_checked_by_id.id:u.id})

