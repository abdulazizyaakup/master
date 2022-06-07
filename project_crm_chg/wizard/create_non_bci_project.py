# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import string
from difflib import SequenceMatcher
from itertools import chain
from odoo.exceptions import RedirectWarning,UserError, ValidationError

class CreateNonBciProject(models.TransientModel):

    _name = 'create.nonbci.project'
    _description = 'Create non bci project'


    def _get_user_id(self):
        return self.env.uid

    def _get_user_company_id(self):
        return self.env.company.id

    province1 = fields.Selection([
                                ('Johor','Johor'),
                                ('Kedah','Kedah'),
                                ('Kelantan','Kelantan'),
                                ('Terengganu','Terengganu'),
                                ('Perak','Perak'),
                                ('Selangor','Selangor'),
                                ('Kuala Lumpur','Kuala Lumpur'),
                                ('Johor','Johor'),
                                ('Melaka','Melaka'),
                                ('Negeri Sembilan','Negeri Sembilan'),
                                ('Pahang','Pahang'),
                                ('Sabah','Sabah'),
                                ('Sarawak','Sarawak'),
                                ('Putrajaya','Putrajaya'),
                                ('Penang','Penang')
                                  ],string="Province")
    name = fields.Char("Project Name", required=True)
    requestor = fields.Many2one('res.users', string="Request By")
    requestor_company = fields.Many2one('res.company', string="Requestor's Company")
    is_bci_project = fields.Boolean("BCI Project?", default=False)
    project_type = fields.Char("Project Type")
    project_location = fields.Char("Project Location")
    project_developer1 = fields.Many2one('res.partner', string="Developer 1")
    project_developer1_contact1 = fields.Many2one('res.partner', string="Developer 1 Contact 1")
    project_developer1_contact2 = fields.Many2one('res.partner', string="Developer 1 Contact 2")
    project_developer2 = fields.Many2one('res.partner', string="Developer 2")
    project_developer2_contact1 = fields.Many2one('res.partner', string="Developer 2 Contact 1")
    project_developer2_contact2 = fields.Many2one('res.partner', string="Developer 2 Contact 2")
    project_architect1 = fields.Many2one('res.partner', string="Architect 1")
    project_architect1_contact1 = fields.Many2one('res.partner', string="Architect 1 Contact 1")
    project_architect1_contact2 = fields.Many2one('res.partner', string="Architect 1 Contact 2")
    project_architect2 = fields.Many2one('res.partner', string="Architect 2")
    project_architect2_contact1 = fields.Many2one('res.partner', string="Architect 2 Contact 1")
    project_architect2_contact2 = fields.Many2one('res.partner', string="Architect 2 Contact 2")
    consulting_engineer1 = fields.Many2one('res.partner', string="Consulting Engineer 1")
    consulting_engineer1_contact1 = fields.Many2one('res.partner', string="Consulting Engineer 1 Contact 1")
    consulting_engineer1_contact2 = fields.Many2one('res.partner', string="Consulting Engineer 1 Contact 2")
    consulting_engineer2 = fields.Many2one('res.partner', string="Consulting Engineer 2")
    consulting_engineer2_contact1 = fields.Many2one('res.partner', string="Consulting Engineer 2 Contact 1")
    consulting_engineer2_contact2 = fields.Many2one('res.partner', string="Consulting Engineer 2 Contact 2")
    consultant1 = fields.Many2one('res.partner', string="Consultant 1")
    consultant1_contact1 = fields.Many2one('res.partner', string="Consultant 1 Contact 1")
    consultant1_contact2 = fields.Many2one('res.partner', string="Consultant 1 Contact 2")
    green_building_consultant1 = fields.Many2one('res.partner', string="Green Building Consultant 1")
    green_building_consultant1_contact1 = fields.Many2one('res.partner', string="Green Building Consultant 1 Contact 1")
    green_building_consultant1_contact2 = fields.Many2one('res.partner', string="Green Building Consultant 1 Contact 2")
    project_quantity_surveyor1 = fields.Many2one('res.partner', string="Quantity Surveyor 1")
    project_quantity_surveyor1_contact1 = fields.Many2one('res.partner', string="Quantity Surveyor 1 Contact 1")
    project_quantity_surveyor1_contact2 = fields.Many2one('res.partner', string="Quantity Surveyor 1 Contact 2")
    project_main_contractor1 = fields.Many2one('res.partner', string="Main Contractor 1")
    project_main_contractor1_contact1 = fields.Many2one('res.partner', string="Main Contractor 1 Contact 1")
    project_main_contractor1_contact2 = fields.Many2one('res.partner', string="Main Contractor 1 Contact 2")
    project_main_contractor2 = fields.Many2one('res.partner', string="Main Contractor 2")
    project_main_contractor2_contact1 = fields.Many2one('res.partner', string="Main Contractor 2 Contact 1")
    project_main_contractor2_contact2 = fields.Many2one('res.partner', string="Main Contractor 2 Contact 2")
    contractor1 = fields.Many2one('res.partner', string="Contractor 1")
    contractor1_contact1 = fields.Many2one('res.partner', string="Contractor 1 Contact 1")
    contractor1_contact2 = fields.Many2one('res.partner', string="Contractor 1 Contact 2")
    project_sub_contractor1 = fields.Many2one('res.partner', string="Subcontractor 1")
    project_sub_contractor1_contact1 = fields.Many2one('res.partner', string="Subcontractor 1 Contact 1")
    project_sub_contractor1_contact2 = fields.Many2one('res.partner', string="Subcontractor 1 Contact 2")
    turnkey_contractor1 = fields.Many2one('res.partner', string="Turnkey Contractor 1")
    turnkey_contractor1_contact1 = fields.Many2one('res.partner', string="Turnkey Contractor 1 Contact 1")
    turnkey_contractor1_contact2 = fields.Many2one('res.partner', string="Turnkey Contractor 1 Contact 2")
    project_owner1 = fields.Many2one('res.partner', string="Owner 1")
    project_owner1_contact1 = fields.Many2one('res.partner', string="Owner 1 Contact 1")
    project_owner1_contact2 = fields.Many2one('res.partner', string="Owner 1 Contact 2")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    project_value = fields.Char('Project Value(Million)')
    other_info = fields.Text('Other Info')
    element_info = fields.Text('Building Elements Included')
    customer = fields.Many2one('res.partner',string='Customer Name')
    ref = fields.Char(string='Reference', index=True)
    status_id = fields.Many2one('project.crm.status', string="Project Status2")
    stage_id = fields.Selection([('new','New'),('validated','Validated'),('duplicate','Duplicate'),('cancelled','Cancelled')], default='new')
    opportunity_count = fields.Integer("Opportunity", compute='_compute_opportunity_count')
    opportunity_count_ids = fields.Many2many('crm.lead', compute="_compute_opportunity_count", string='Opportunities Count', help='Technical field used for stat button')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    project_stage_id = fields.Many2one('project.crm.stage', string='Project Stage', ondelete='restrict', tracking=True, index=True, copy=False,
        group_expand='_read_group_stage_ids')
    town = fields.Char("Town")
    project_owner_type = fields.Many2one('project.owner.type', string="Owner Type", required=True)
    project_development_type = fields.Many2one('project.dev.type', string="Project Development Type")
    project_site_area = fields.Char("Site Area")
    project_floor_area = fields.Char("Floor Area")
    project_building_storeys = fields.Char("Storeys")
    project_timestamp = fields.Char("Timestamp")
    project_refid = fields.Char("Project Refid")
    project_version = fields.Char("Version")
    project_remarks = fields.Text('Remarks')
    project_keywords = fields.Char("Keywords")
    bci_region = fields.Char("BCI Region")
    timetable_remarks = fields.Char("Timetable Remarks")
    us_value = fields.Char("US Value")
    foreign_participation = fields.Boolean("Foreign Participation")
    major = fields.Boolean("Major")
    project_notes = fields.Text("Project Notes")
    project_green_building_rating = fields.Char("Green Building Rating")
    project_status_description = fields.Char("Project Status Description")
    project_units_residential = fields.Char("Project Units Residential")
    project_units_industrial = fields.Char("Project Units Industrial")
    project_category1 = fields.Many2one('project.crm.category',string="Category 1", required=True)
    project_subcategory1 = fields.Many2one('project.crm.category',string="Sub-Category 1")
    address = fields.Text("Address")

    #@api.constrains('project_developer1','project_architect1','project_quantity_surveyor1','project_main_contractor1')
    #def check_validation(self):
    #    dev = self.project_developer1
    #    arc = self.project_architect1
    #    qs = self.project_quantity_surveyor1
    #    mc = self.project_main_contractor1

    #    if(not dev):
    #        if(not qs):
    #            if(not mc):
    #                if(not arc):
    #                    raise ValidationError('Project Developer, Architect,Quantity Surveyor and Main Contractor are empty. Please fill in at least one of it.')



    def create_non_bci(self):
        requestor_id = self._get_user_id()
        comp = self._get_user_company_id()
        for b in self:
            self.env['master.project'].sudo().create({
                        'name':b.name,
                        'requestor': requestor_id,
                        'requestor_company': comp,
                        'is_bci_project':False,
                        'project_keywords':b.project_keywords,
                        'project_code':'/',
                        'stage_id':'new',
                        'address':b.address,
                        'province1': b.province1,
                        'project_owner_type':b.project_owner_type.id,
                        'project_development_type':b.project_development_type.id,
                        'project_site_area':b.project_site_area,
                        'project_floor_area':b.project_floor_area,
                        'project_building_storeys':b.project_building_storeys,
                        'start_date':b.start_date,
                        'end_date':b.end_date,
                        'project_value':b.project_value,
                        'company_id':1,
                        'project_green_building_rating':b.project_green_building_rating,
                        'project_status_description':b.project_status_description,
                        'project_units_residential':b.project_units_residential,
                        'project_units_industrial':b.project_units_industrial,
                        'project_category1':b.project_category1.id,
                        'project_subcategory1':b.project_subcategory1.id,
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

        return self.env['master.project'].change_stage_to_waiting()
