# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID,_
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import RedirectWarning
from odoo.addons.web.controllers.main import clean_action
import datetime
import requests

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')

evaluation_context = {
    'datetime': datetime,
    'context_today': datetime.datetime.now,
}

class FormatAddressMixin(models.AbstractModel):
    _name = "format.address.mixin"
    _description = 'Address Format'

    def _fields_view_get_address(self, arch):
        # consider the country of the user, not the country of the partner we want to display
        address_view_id = self.env.company.country_id.address_view_id
        if address_view_id and not self._context.get('no_address_format'):
            #render the partner address accordingly to address_view_id
            doc = etree.fromstring(arch)
            for address_node in doc.xpath("//div[hasclass('o_address_format')]"):
                Partner = self.env['res.partner'].with_context(no_address_format=True)
                sub_view = Partner.fields_view_get(
                    view_id=address_view_id.id, view_type='form', toolbar=False, submenu=False)
                sub_view_node = etree.fromstring(sub_view['arch'])
                #if the model is different than res.partner, there are chances that the view won't work
                #(e.g fields not present on the model). In that case we just return arch
                if self._name != 'res.partner':
                    try:
                        self.env['ir.ui.view'].postprocess_and_fields(self._name, sub_view_node, None)
                    except ValueError:
                        return arch
                address_node.getparent().replace(address_node, sub_view_node)
            arch = etree.tostring(doc, encoding='unicode')
        return arch

class ProjectCRM(models.Model):
    _name = 'project.crm'
    _inherit = ['mail.thread.cc','mail.thread.cc','mail.thread', 'mail.activity.mixin']

    _description = "Project/CRM"

    def _get_user_id(self):
        return self.env.uid

    def _get_user_company_id(self):
        return self.env.company.id

    def _get_user_new_lead_level(self):
        comp_id = self.env.company.id
        lev = self.env['crm.project.level'].search([])
        for i in lev:
            if(i.company_id.id == comp_id):
                if(i.name == 'New Lead'):
                    val = i.id

                    return val

    def _default_project_id(self):
        return self.env['project.crm'].browse(self._context.get('active_ids'))

    def _default_team_id(self, user_id):
        domain = [('use_leads', '=', True)] if self._context.get('default_type') != "lead" or self.type != 'lead' else [('use_opportunities', '!=', True)]
        return self.env['crm.team']._get_default_team_id(user_id=user_id, domain=domain)

    def _default_stage_id(self):
        team = self._default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id

    def getMasterProject(self):

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')



        getMaster = requests.get('http://api.bciasia.com/projects.cfc?wsdl&token='+token+'&method=getByQuery&returnFormat=json'+
'&fields=projectid,state,cat_1_name,con_start,con_end,projectrefid,floor_area,project_name,subcat_1_name,cat_2_name,subcat_2_name,town,dev_type,owner_type,'+
'last,state_name,keyword,remarks,postcode,ag_storeys,project_status,time_stamp,site_area,value,project_type,status_text,address,projectstage')

        data = getMaster.json()

        existing_list = []

        for bci in bci_projects:
                existing_list.append(bci.bci_project_code)


        new_list = list(set(existing_list)) 
        
        for a in data:
            getRegion = requests.get('http://api.bciasia.com/regions.cfc?wsdl&token='+token+'&method=getByQuerygetByPK&bciregionid='+a['BCIREGIONID']+'&returnFormat=json')
            
            region_vals = getRegion.json()
            for rn in region_vals:
                region_name = rn['BCIREGION_NAME']

            if(str(a['PROJECTID']) in new_list):
                continue
            elif(str(a['PROJECTID']) not in new_list):
                self.env['project.crm'].sudo().create({
                            'name':a['PROJECT_NAME'],
                            'is_bci_project':True,
                            'project_keywords':a['KEYWORD'],
                            'project_code':'/',
                            'bci_project_code':a['PROJECTID'],
                            'address1':a['ADDRESS'],
                            #'state_id':b.state_id.id,
                            'zip':a['POSTCODE'],
                            #'country_id':b.country_id.id,
                            'bci_region':region_name,
                            'project_owner_type':a['OWNER_TYPE'],
                            'project_development_type':a['DEV_TYPE'],
                            'project_site_area':a['SITE_AREA'],
                            'project_floor_area':a['FLOOR_AREA'],
                            'project_building_storeys':a['AG_STOREYS'],
                            'project_timestamp':a['TIME_STAMP'],
                            'project_refid':a['PROJECTREFID'],
                            'project_version':a['VERSION'],
                            'start_date':a['CON_START'],
                            'end_date':a['CON_END'],
                            'project_value':a['VALUE'],
                            #'company_id':b.company_id.id,
                            #'timetable_remarks':a[''],
                            # 'foreign_participation':a[''],
                            # 'major':a[''],
                            'project_last':a['LAST'],
                            'project_green_building_rating':a['GREEN_STAR_RATING_ID'],
                            'project_status_description':a['STATUS_TEXT'],
                            # 'project_units_residential':a[''],
                            # 'project_units_industrial':a[''],
                            'project_category1':a['CAT_1_NAME'],
                            'project_category2':a['CAT_2_NAME'],
                            'project_category3':a['CAT_3_NAME'],
                            'project_category4':a['CAT_4_NAME'],
                            'project_category5':a['CAT_5_NAME'],
                            'project_category6':a['CAT_6_NAME'],
                            'project_category7':a['CAT_7_NAME'],
                            'project_category8':a['CAT_8_NAME'],
                            'project_subcategory1':a['SUBCAT_1_NAME'],
                            'project_subcategory2':a['SUBCAT_2_NAME'],
                            'project_subcategory3':a['SUBCAT_3_NAME'],
                            'project_subcategory4':a['SUBCAT_4_NAME'],
                            'project_subcategory5':a['SUBCAT_5_NAME'],
                            'project_subcategory6':a['SUBCAT_6_NAME'],
                            'project_subcategory7':a['SUBCAT_7_NAME'],
                            'project_subcategory8':a['SUBCAT_8_NAME'],
                            'project_remarks':a['REMARKS'],
                            'element_info':a[''],

                    })                




    def getProjectParties(self):

        #self.ensure_one()

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')
        bci_partner = self.env['res.partner'].search([])

        no_architect_list = []

        for bci in bci_projects:
            if(not bci.project_architect1):
                no_architect_list.append(bci.bci_project_code)

        new_list = list(set(no_architect_list)) 

        for bp in bci_projects:
            if(bp.bci_project_code in new_list):
                getAll = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid')
#            getAll2 = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid=53447003&returnFormat=json&fields=role_name,companyid,contactid,projectid')
                link_get = 'http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid'
            
                try:
                    data = getAll.json()
                    print(data)
                except ValueError:
                    print("LINK IS :",link_get)
                    print("Response content is not valid JSON 1")
            
            #try:
                for a in data:
                    if(str(a['PROJECTID']) == bp.bci_project_code):
                        if(a['ROLE_NAME'] == 'Architect'):
                            part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Architect')])
                            for p in part:
                                bp.sudo().write({'project_architect1':p[0].id})
                    #if(a['ROLE_NAME'] == 'Developer'):
                    #    part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Developer')])
                    #    for p in part:
                    #        bp.sudo().write({'project_developer1':p[0].id})
                    #if(a['ROLE_NAME'] == 'Main Contractor'):
                    #    part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Main Contractor')])
                    #    for p in part:
                    #        print("XXXXXXXXXX ",p[0].name, " DDDD ", p[0].id)
                    #        bp.sudo().write({'project_main_contractor1':p[0].id})
                    #if(a['ROLE_NAME'] == 'Contractor'):
                    #    part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Contractor')])
                    #    for p in part:
                    #        bp.sudo().write({'contractor1':p[0].id})
                    #if('Civil' in a['ROLE_NAME']):
                    #    part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','ilike','Civil')])
                    #    for p in part:
                    #        bp.sudo().write({'project_civil_structural_eng1':p[0].id})
                    

            #except ValueError:
            #    print("Error here:  ",testVal)
            #    print("Response content is not valid JSON 2")
    def getProjectArchitect(self):

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')
        bci_partner = self.env['res.partner'].search([])

        no_arc_list = []

        for bci in bci_projects:
            if(not bci.project_architect1):
                no_arc_list.append(bci.bci_project_code)

        new_list = list(set(no_arc_list)) 

        for bp in bci_projects:
            if(bp.bci_project_code in new_list):
                getAll = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid')
                link_get = 'http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid'
            
                try:
                    data = getAll.json()
                except ValueError:
                    print("Response content is not valid JSON 1")
            
                for a in data:
                    if(str(a['PROJECTID']) == bp.bci_project_code):
                        if('Architect' in a['ROLE_NAME']):
                            part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Architect')])
                            for p in part:
                                bp.sudo().write({'project_architect1':p[0].id})


    def getProjectDeveloper(self):

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')
        bci_partner = self.env['res.partner'].search([])

        no_developer_list = []

        for bci in bci_projects:
            if(not bci.project_developer1):
                no_developer_list.append(bci.bci_project_code)

        new_list = list(set(no_developer_list)) 

        for bp in bci_projects:
            if(bp.bci_project_code in new_list):
                getAll = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid')
                link_get = 'http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid'
            
                try:
                    data = getAll.json()
                except ValueError:
                    print("Response content is not valid JSON 1")
            
                for a in data:
                    if(str(a['PROJECTID']) == bp.bci_project_code):
                        if(a['ROLE_NAME'] == 'Developer'):
                            part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Developer')])
                            for p in part:
                                bp.sudo().write({'project_developer1':p[0].id})


    def getProjectMainCon(self):

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')
        bci_partner = self.env['res.partner'].search([])

        no_maincon_list = []

        for bci in bci_projects:
            if(not bci.project_main_contractor1):
                no_maincon_list.append(bci.bci_project_code)

        new_list = list(set(no_maincon_list)) 

        for bp in bci_projects:
            if(bp.bci_project_code in new_list):
                getAll = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid')
                link_get = 'http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid'
            
                try:
                    data = getAll.json()
                except ValueError:
                    print("Response content is not valid JSON 1")
            
                for a in data:
                    if(str(a['PROJECTID']) == bp.bci_project_code):
                        if(a['ROLE_NAME'] == 'Main Contractor'):
                            part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Main Contractor')])
                            for p in part:
                                bp.sudo().write({'project_main_contractor1':p[0].id})

    def getProjectContractor(self):

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')
        bci_partner = self.env['res.partner'].search([])

        no_con_list = []

#for p in range(0, 1000, 10):
#    process10(sites[p:p+10])

        for bci in bci_projects:
            if(not bci.contractor1):
                no_con_list.append(bci.bci_project_code)

        new_list = list(set(no_con_list)) 

        for bp in bci_projects:
            if(bp.bci_project_code in new_list):
                getAll = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid')
                link_get = 'http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid'
            
                try:
                    data = getAll.json()
                except ValueError:
                    print("Response content is not valid JSON 1")
            
                for a in data:
                    if(str(a['PROJECTID']) == bp.bci_project_code):
                        if(a['ROLE_NAME'] == 'Contractor'):
                            part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Contractor')])
                            for p in part:
                                bp.sudo().write({'contractor1':p[0].id})

    def getProjectCivilEng(self):

        clientID = 'starken08_API'
        passwd = 'Chgb58200'

        r = requests.get('https://api.bciasia.com/rest/auth.json?clientID='+clientID+'&password='+passwd)
        vals = r.json()
        token = vals['TOKEN']

        bci_projects = self.env['project.crm'].search([],order='create_date desc')
        bci_partner = self.env['res.partner'].search([])

        no_civil_list = []

        for bci in bci_projects:
            if(not bci.project_civil_structural_eng1):
                no_civil_list.append(bci.bci_project_code)

        new_list = list(set(no_civil_list)) 

        for bp in bci_projects:
            if(bp.bci_project_code in new_list):
                getAll = requests.get('http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid')
                link_get = 'http://api.bciasia.com/projectroles.cfc?wsdl&token='+token+'&method=getByQuery&projectid='+bp.bci_project_code+'&returnFormat=json&fields=role_name,companyid,projectid'
            
                try:
                    data = getAll.json()
                except ValueError:
                    print("Response content is not valid JSON 1")
            
                for a in data:
                    if(str(a['PROJECTID']) == bp.bci_project_code):
                        if('Civil' in a['ROLE_NAME']):
                            part = self.env['res.partner'].search([('firm_id','=',a['COMPANYID']),('partner_type.name','=','Civil & Structural Engineer')])
                            for p in part:
                                bp.sudo().write({'project_civil_structural_eng1':p[0].id})

    name = fields.Char("Project Name")
    is_related_project = fields.Boolean("Is Related Project?", default=True)
    project_code = fields.Char("GSM Project ID", default="/")
    project_type = fields.Char("Project Type")
    bci_project_code = fields.Char("BCI Project ID")
    # project_category = fields.Many2one('project.crm.category', string='Category',tracking=10, index=True)
    project_location = fields.Char("Project Location")
    #parties involved#

    project_facade_consultant = fields.Many2one('res.partner', string="Facade Consultant")
    project_facade_consultant_contact1 = fields.Many2one('res.partner', string="Facade Consultant 1 Contact 1")
    project_facade_consultant_contact2 = fields.Many2one('res.partner', string="Facade Consultant 1 Contact 2")
    project_interior_designer = fields.Many2one('res.partner', string="Interior Designer")
    project_interior_designer_contact1 = fields.Many2one('res.partner', string="Interior Designer 1 Contact 1")
    project_interior_designer_contact2 = fields.Many2one('res.partner', string="Interior Designer 1 Contact 2")

    project_design_builder = fields.Many2one('res.partner', string="Design Builder")
    project_design_builder_contact1 = fields.Many2one('res.partner', string="Design Builder 1 Contact 1")
    project_design_builder_contact2 = fields.Many2one('res.partner', string="Design Builder 1 Contact 2")
    project_ss_contractor = fields.Many2one('res.partner', string="Super Structure Contractor")
    project_ss_contractor_contact1 = fields.Many2one('res.partner', string="Super Structure Contractor 1 Contact 1")
    project_ss_contractor_contact2 = fields.Many2one('res.partner', string="Super Structure Contractor 1 Contact 2")

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

    project_building_contractor1 = fields.Many2one('res.partner', string="Building Contractor")
    project_civil_structural_eng1 = fields.Many2one('res.partner', string="")

    contractor1 = fields.Many2one('res.partner', string="Contractor 1")
    contractor1_contact1 = fields.Many2one('res.partner', string="Contractor 1 Contact 1")
    contractor1_contact2 = fields.Many2one('res.partner', string="Contractor 1 Contact 2")
    
    project_sub_contractor1 = fields.Many2one('res.partner', string="Subcontractor 1")
    project_sub_contractor1_contact1 = fields.Many2one('res.partner', string="Subcontractor 1 Contact 1")
    project_sub_contractor1_contact2 = fields.Many2one('res.partner', string="Subcontractor 1 Contact 2")

    turnkey_contractor1 = fields.Many2one('res.partner', string="Turnkey Contractor 1")
    turnkey_contractor1_contact1 = fields.Many2one('res.partner', string="Turnkey Contractor 1 Contact 1")
    turnkey_contractor1_contact2 = fields.Many2one('res.partner', string="Turnkey Contractor 1 Contact 2")
    
    # project_civil_work_contractor = fields.Many2one('res.partner', string="Civil Work Contractor")
    # pcw_contractor_contact1 = fields.Many2one('res.partner', string="Contact 1")
    # pcw_contractor_contact2 = fields.Many2one('res.partner', string="Contact 2")
    project_owner1 = fields.Many2one('res.partner', string="Owner 1")
    project_owner1_contact1 = fields.Many2one('res.partner', string="Owner 1 Contact 1")
    project_owner1_contact2 = fields.Many2one('res.partner', string="Owner 1 Contact 2")
    
    # project_it_subcon = fields.Many2one('res.partner', string="IT Subcon",domain=lambda self: [('partner_types.name', '=', 'IT Subcon')])
    # project_bs_subcon = fields.Many2one('res.partner', string="Building Services Subcon")
    # project_bs_subcon_contact1 = fields.Many2one('res.partner', string="Contact 1")
    # project_bs_subcon_contact1 = fields.Many2one('res.partner', string="Contact 2")
    # project_design_engineer = fields.Many2one('res.partner', string="Design Engineer")
    # project_management_consultant = fields.Many2one('res.partner', string="Management Consultant",domain=lambda self: [('partner_types.name', '=', 'Management Consultant')])
    # project_master_planner = fields.Many2one('res.partner', string="Master Planner",domain=lambda self: [('partner_types.name', '=', 'Master Planner')])
    # project_operator = fields.Many2one('res.partner', string="Operator",domain=lambda self: [('partner_types.name', '=', 'Operator')])
    # project_lift_subcon = fields.Many2one('res.partner', string="Lift Subcon",domain=lambda self: [('partner_types.name', '=', 'Lift Subcon')])
    # # project_contact = fields.Many2one('res.partner', string="Project Contact",domain=[('type', '=', 'contact')])



    #parties involved#
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    project_value = fields.Monetary('Project Value(Million)', currency_field='company_currency', tracking=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    other_info = fields.Text('Other Info')
    element_info = fields.Text('Building Elements Included')
    customer = fields.Many2one('res.partner',string='Customer Name')
    position = fields.Char(string="Position")
    contact_no = fields.Char(string="Contact No.")
    ref = fields.Char(string='Reference', index=True)
    status_id = fields.Many2one('project.crm.status', string="Project Status2")
    stage_id = fields.Selection([('new','New'),('validated','Validated'),('duplicate','Duplicate'),('cancelled','Cancelled')], default='new')
    opportunity_count = fields.Integer("Opportunity", compute='_compute_opportunity_count')
    opportunity_count_ids = fields.Many2many('crm.lead', compute="_compute_opportunity_count", string='Opportunities Count', help='Technical field used for stat button')
    created_by = fields.Many2one('res.users',string="", default=lambda self: self.env.user)
    validate_by = fields.Many2one('res.users','Validate By')
    bu_company = fields.Many2one('res.company', string='Business Unit', index=True, default=lambda self: self.env.company.id)
    address1 = fields.Char("Address")
    province1 = fields.Char("Province")
    postcode1 = fields.Char("Postcode")
    country1 = fields.Char("Country")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    team_id = fields.Many2one('crm.team', string='Sales Team', default=lambda self: self._default_team_id(self.env.uid),
        index=True, tracking=True, help='When sending mails, the default email address is taken from the Sales Team.')
    project_stage_id = fields.Many2one('project.crm.stage', string='Project Stage', ondelete='restrict', tracking=True, index=True, copy=False,
        group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    bu_project_ids = fields.One2many('bu.project.id', 'bu_line_id',string="BU Project ID")
    # bu_pjt_ids = fields.One2many('crm.lead', 'bu_lines_id',string="BU Project ID")
    bu_id = fields.Char("Business Unit ID")
    town = fields.Char("Town")
    project_id = fields.Many2one('project.crm', string="Project", ondelete='cascade', index=True, copy=False, readonly=True, default=_default_project_id)
    project_owner_type = fields.Many2one('project.owner.type', string="Owner Type")
    project_development_type = fields.Many2one('project.dev.type', string="Project Development Type")
    project_site_area = fields.Char("Site Area")
    project_floor_area = fields.Char("Floor Area")
    project_building_storeys = fields.Char("Storeys")
    project_timestamp = fields.Datetime("Timestamp")
    project_refid = fields.Char("Project Refid")
    project_version = fields.Char("Version")
    project_remarks = fields.Text('Remarks')
    project_keywords = fields.Char("Keywords")
    bci_region = fields.Char("BCI Region")
    timetable_remarks = fields.Char("Timetable Remarks")
    us_value = fields.Char("US Value")
    foreign_participation = fields.Boolean("Foreign Participation")
    major = fields.Boolean("Major")
    project_language = fields.Char("Language")
    project_last = fields.Boolean("Last")
    project_notes = fields.Text("Project Notes")
    project_green_building_rating = fields.Char("Green Building Rating")
    project_status_description = fields.Char("Project Status Description")
    project_units_residential = fields.Char("Project Units Residential")
    project_units_industrial = fields.Char("Project Units Industrial")
    project_category1 = fields.Many2one('project.crm.category')
    project_category2 = fields.Many2one('project.crm.category')
    project_category3 = fields.Many2one('project.crm.category')
    project_category4 = fields.Many2one('project.crm.category')
    project_category5 = fields.Many2one('project.crm.category')
    project_category6 = fields.Many2one('project.crm.category')
    project_category7 = fields.Many2one('project.crm.category')
    project_category8 = fields.Many2one('project.crm.category')

    project_subcategory1 = fields.Many2one('project.crm.category')
    project_subcategory2 = fields.Many2one('project.crm.category')
    project_subcategory3 = fields.Many2one('project.crm.category')
    project_subcategory4 = fields.Many2one('project.crm.category')
    project_subcategory5 = fields.Many2one('project.crm.category')
    project_subcategory6 = fields.Many2one('project.crm.category')
    project_subcategory7 = fields.Many2one('project.crm.category')
    project_subcategory8 = fields.Many2one('project.crm.category')
    master_project_ids = fields.One2many('master.project','bci_related_project',string="Related Master")
    project_categ = fields.Many2one('project.crm.categ', string="Project Category")
    p_category = fields.Many2many('project.crm.category', string="Category")

    @api.depends('project_category1','project_category2','project_category3','project_category4'
                    ,'project_category5','project_category6','project_category7','project_category8')
    @api.onchange('project_category1')
    def set_category_many2many(self):
        # lead.meeting_ids = [(4, self.id)] 
        bci = self.env['project.crm'].search([])

        for b in bci:
            if(b.project_category1):
                b.p_category = [(4, b.project_category1.id)]
            if(b.project_category2):
                b.p_category = [(4, b.project_category2.id)]
            if(b.project_category3):
                b.p_category = [(4, b.project_category3.id)]
            if(b.project_category4):
                b.p_category = [(4, b.project_category4.id)]
            if(b.project_category5):
                b.p_category = [(4, b.project_category5.id)]
            if(b.project_category6):
                b.p_category = [(4, b.project_category6.id)]
            if(b.project_category7):
                b.p_category = [(4, b.project_category7.id)]
            if(b.project_category8):
                b.p_category = [(4, b.project_category8.id)]
            if(b.project_subcategory1):
                b.p_category = [(4, b.project_subcategory1.id)]
            if(b.project_subcategory2):
                b.p_category = [(4, b.project_subcategory2.id)]
            if(b.project_subcategory3):
                b.p_category = [(4, b.project_subcategory3.id)]
            if(b.project_subcategory4):
                b.p_category = [(4, b.project_subcategory4.id)]
            if(b.project_subcategory5):
                b.p_category = [(4, b.project_subcategory5.id)]
            if(b.project_subcategory6):
                b.p_category = [(4, b.project_subcategory6.id)]
            if(b.project_subcategory7):
                b.p_category = [(4, b.project_subcategory7.id)]
            if(b.project_subcategory8):
                b.p_category = [(4, b.project_subcategory8.id)]


    def set_parent(self):
        categ = self.env['project.crm.category'].search([])
        bci = self.env['project.crm'].search([])

        for val in bci:
            for c in categ:
                if(c.name == val.project_subcategory1.name):
                    parent_1 = val.project_category1.id
                    c.write({'parent_id':parent_1})
                if(c.name == val.project_subcategory2.name):
                    parent_2 = val.project_category2.id
                    c.write({'parent_id':parent_2})
                if(c.name == val.project_subcategory3.name):
                    parent_3 = val.project_category3.id
                    c.write({'parent_id':parent_3})
                if(c.name == val.project_subcategory4.name):
                    parent_4 = val.project_category4.id
                    c.write({'parent_id':parent_4})
                if(c.name == val.project_subcategory5.name):
                    parent_5 = val.project_category5.id
                    c.write({'parent_id':parent_5})
                if(c.name == val.project_subcategory6.name):
                    parent_6 = val.project_category6.id
                    c.write({'parent_id':parent_6})
                if(c.name == val.project_subcategory7.name):
                    parent_7 = val.project_category7.id
                    c.write({'parent_id':parent_7})
                if(c.name == val.project_subcategory8.name):
                    parent_8 = val.project_category8.id
                    c.write({'parent_id':parent_8})


    def get_set_id(self):
        lead_id = self.env.context.get('default_lead_id', False)
        lead_name = self.env.context.get('default_lead_name', False)
        lead_p_id = self.env.context.get('default_lead_project_id', False)
        val = self.env['crm.lead'].sudo().search([('id','=',lead_id)])


        if(self.id):
            val.write({'sub_project_code':val.crm_project_id,'crm_bci_id':self.bci_project_code})
            self.write({'project_code':lead_p_id})

    def set_not_applicable(self):
        lead_id = self.env.context.get('default_lead_id', False)
        lead_name = self.env.context.get('default_lead_name', False)
        lead_p_id = self.env.context.get('default_lead_project_id', False)
        val = self.env['crm.lead'].sudo().search([('id','=',lead_id)])


        if(self.id):
            val.write({'crm_bci_id':'N/A'})

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

    def get_bci_data_from_csv(self):
        values = []
        included_cols = [1]
        with open('/home/aziz/Desktop/KK/ProjectMaster.csv', newline='') as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                values.append(row)

        return values

    # def update_bci_from_csv(self):

        # t = today.strftime("%d/%m/%Y")
        # today_date = datetime.strptime(t,"%d/%m/%Y")
        # leads = self.env['crm.lead'].sudo().search([])
        # vals = self.get_bci_status_from_csv()
        
        # for l in leads:
        #     for v in vals:
        #         if(v[2]):
        #             if(l.crm_bci_id == v[0]):
        #                 if(v[1] == 'Construction'):
        #                     if(datetime.strptime(v[2],"%d/%m/%Y") < today_date):
        #                         l.write({'bci_complete_status':True, 'bci_project_stage':2})




    def copy_bci_project_to_master_wizard(self):

        for b in self:
            self.env['master.project'].sudo().create({
                        'name':b.name,
                        'is_bci_project':True,
                        'project_keywords':b.project_keywords,
                        'project_code':'/',
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

        return self.copy_message()


    @api.depends('crm_bci_id')
    def copy_bci_project_to_master(self):
        requestor_id = self._get_user_id()
        comp = self._get_user_company_id()
        # users = self.env['res.users'].search(['id','=',requestor_id.id])
        master = self.env['master.project'].search([])

        exist_in_master = []

        for m in master:
            if m.bci_project_code:
                exist_in_master.append(m.bci_project_code)


        for b in self:
            if(b.bci_project_code in exist_in_master):
                action = self.env.ref('project_crm_chg.master_project_action')
                msg = _('The following BCI Project already exist in the Master List.')
                raise RedirectWarning(msg, action.id, _('Show Project'))
            elif(b.bci_project_code not in exist_in_master):
                self.env['master.project'].sudo().create({
                        'requestor': requestor_id,
                        'requestor_company': comp,
                        'name':b.name,
                        'is_bci_project':True,
                        'bci_related_project':b.id,
                        'project_keywords':b.project_keywords,
                        'project_code':'/',
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
        message_id = self.env['message.wizard'].create({'message': _("Project successfully created!")})
        return {
            'name': _('Successfull'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            # pass the id
            'res_id': message_id.id,
            'target': 'new'
        }




    def generate_leads(self):
        requestor_id = self._get_user_id()
        comp = self._get_user_company_id()
        partner = self.env.user.partner_id
        master = self.env['master.project'].search([])
        leads = self.env['crm.lead'].search([])
        level = self._get_user_new_lead_level()

        exist_in_master = []
        exist_in_leads = []

        for m in master:
            if m.bci_project_code:
                exist_in_master.append(m.bci_project_code)

        for l in leads:
            if l.crm_bci_id:
                if(l.company_id.id == comp):
                    exist_in_leads.append(l.crm_bci_id)

        # lev = []

        # for v in level:
        #     if(v.company_id.id == comp):
        #         if(v.name == 'New Lead'):
        #         # print("FFFFFFFFFF ", v.name)
        #             lev.append(v.id)


        for b in self:
            # print("XXXX ", b.name)
            for m in master:
                if(b.bci_project_code in exist_in_master):
                    if(b.bci_project_code not in exist_in_leads):
                        self.env['crm.lead'].sudo().create({
                        # 'sub_project_code': b.project_code,
                        'crm_bci_id': b.bci_project_code,
                        # 'master_id': m.id,
                        'bci_province1':b.province1,
                        'name': b.name,
                        'project_type': b.project_type,
                        #'crm_project_level': level,
                        'user_id': requestor_id,
                        # 'crm_prj_own_sales': partner.id,
                        # 'crm_prj_own_mark': partner.id,
                        'crm_title': b.name,
                        'company_id': comp,
                        'crm_prj_value': b.project_value,
                        'crm_startdate': b.start_date or '',
                        'crm_enddate': b.end_date or '',
                        'crm_prj_town': b.town,
                        'street': b.street,
                        'street2': b.street2,
                        'city': b.city,
                        'state_id': b.state_id.id or '',
                        'zip': b.zip,
                        'country_id': b.country_id.id or '',
                        'crm_prj_addr': str(b.street)+" ,"+str(b.street2)+" ,"+str(b.city)+" ,"+str(b.zip)+" ,"+str(b.state_id.name)+" ,"+str(b.country_id.name),
                        'bci_region': b.bci_region,
                        'bci_ownership_type': b.project_owner_type.id,
                        'bci_project_category': b.project_category1.id,
                        'bci_project_stage': b.project_stage_id.id,
                        'bci_project_value': b.project_value,
                        'bci_start_date': b.start_date,
                        'bci_end_date': b.end_date,
                        'bci_project_remarks': b.project_remarks,
                        'bci_element_info': b.element_info,
                        'crm_prj_dev1':[(6,0, b.project_developer1.ids)],
                        'crm_prj_arc1':[(6,0, b.project_architect1.ids)],
                        'crm_prj_cseng1':[(6,0, b.consulting_engineer1.ids)],
                        'crm_prj_qs1':[(6,0, b.project_quantity_surveyor1.ids)],
                        'crm_cntrctrs':[(6,0, b.project_main_contractor1.ids),(6,0, b.project_main_contractor2.ids),(6,0, b.contractor1.ids),(6,0, b.turnkey_contractor1.ids)],
                        'crm_sbcns_aplctrs':[(6,0, b.project_sub_contractor1.ids)],
            })

                        message_id = self.env['message.wizard'].create({'message': _("Project successfully created!")})
                        return {
                            'name': _('Successfull'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'message.wizard',
                            'res_id': message_id.id,
                            'target': 'new'
                        }  
                    if(b.bci_project_code in exist_in_leads):                          
                        message_id = self.env['message.wizard'].create({'message': _("Project already exist in your company's CRM!")})
                        return {
                            'name': _('Exist!'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'message.wizard',
                            'res_id': message_id.id,
                            'target': 'new'
                        }  


                elif(b.bci_project_code not in exist_in_master):
                    self.env['master.project'].sudo().create({
                            'requestor': requestor_id,
                            'requestor_company': comp,
                            'name':b.name,
                            'stage_id':'validated',
                            'province1':b.province1,
                            'is_bci_project':True,
                            'bci_related_project':b.id,
                            'project_keywords':b.project_keywords,
                            'project_code':self.env['ir.sequence'].get('master.project1') or '/',
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
                    # for v in level:
                        # if(v.company_id.id == comp):
                    # if(v.name == 'New Lead'):
                    #     print("XXXX ", v.name)
                    #     print("YYYY ", v.id)
                    self.env['crm.lead'].sudo().create({
                        # 'sub_project_code': b.project_code,
                        # 'master_id': m.id,
                        'crm_bci_id': b.bci_project_code,
                        'bci_province1':b.province1,
                        'name': b.name,
                        'user_id': requestor_id,
                        # 'crm_prj_own_sales': partner.id,
                        # 'crm_prj_own_mark': partner.id,
                        'crm_title': b.name,
                        'company_id': comp,
                        'crm_project_level': level,#self.env['crm.project.level'].search([('company_id','=',comp),('name','=','New Lead')]).id,
                        'crm_prj_value': b.project_value,
                        'crm_startdate': b.start_date,
                        'crm_enddate': b.end_date,
                        'crm_prj_town': b.town,
                        'street': b.street,
                        'street2': b.street2,
                        'city': b.city,
                        'state_id': b.state_id.id or '',
                        'zip': b.zip,
                        'country_id': b.country_id.id or '',
                        'crm_prj_addr': str(b.street)+" ,"+str(b.street2)+" ,"+str(b.city)+" ,"+str(b.zip)+" ,"+str(b.state_id.name)+" ,"+str(b.country_id.name),
                        #add province################
                        'bci_region': b.bci_region,
                        'bci_ownership_type': b.project_owner_type.id,
                        'bci_project_category': b.project_category1.id,
                        'bci_project_stage': b.project_stage_id.id,
                        'bci_project_value': b.project_value,
                        'bci_start_date': b.start_date,
                        'bci_end_date': b.end_date,
                        'bci_project_remarks': b.project_remarks,
                        'bci_element_info': b.element_info,
                        'crm_prj_dev1':[(6,0, b.project_developer1.ids)],
                        'crm_prj_arc1':[(6,0, b.project_architect1.ids)],
                        'crm_prj_cseng1':[(6,0, b.consulting_engineer1.ids)],
                        'crm_prj_qs1':[(6,0, b.project_quantity_surveyor1.ids)],
                        'crm_cntrctrs':[(6,0, b.project_main_contractor1.ids),(6,0, b.project_main_contractor2.ids),(6,0, b.contractor1.ids),(6,0, b.turnkey_contractor1.ids)],
                        'crm_sbcns_aplctrs':[(6,0, b.project_sub_contractor1.ids)],
                        })

                    

                    # message_id = self.env['message.wizard'].create({'message': _("Project successfully created!")})
                    # return {
                    #     'name': _('Successfull'),
                    #     'type': 'ir.actions.act_window',
                    #     'view_mode': 'form',
                    #     'res_model': 'message.wizard',
                    #     # pass the id
                    #     'res_id': message_id.id,
                    #     'function': self.set_master_ids(),
                    #     'target': 'new'
                    # }
                    return self.set_master_ids()

    def set_master_ids(self):
        today_date = date.today().strftime("%Y-%m-%d")
        # domain.extend([('create_date', '<', limit_date), ('team_id', '=', False), ('user_id', '=', False)])
        master = self.env['master.project'].search([])
        lead = self.env['crm.lead'].search([])
        no_master = []

        for l in lead:
            # new_date = l.create_date.strftime("%Y-%m-%d")
            if(l.create_date.strftime("%Y-%m-%d") == today_date):
                no_master.append(l.id)


        print("LIST  ", no_master)

        for ll in lead:
            if(ll.id in no_master):
                for m in master:
                    if(ll.crm_bci_id == m.bci_project_code):
                        ll.write({'master_id': m.id, 'sub_project_code':m.project_code})

        message_id = self.env['message.wizard'].create({'message': _("Project successfully created for your company!")})
        return {
            'name': _('Successfull'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            # pass the id
            'res_id': message_id.id,
            'target': 'new'
        }


    def action_view_opportunity(self):
        '''
        This function returns an action that displays the leads from project.
        '''
        action = self.env.ref('crm.crm_lead_opportunities').read()[0]
        action['domain'] = [('id', 'in', self.opportunity_count_ids.ids)]
        return action

    def action_validate_multi(self):
        validated_by_id = self.env.user
        for rec in self:
            rec.write({'stage_id': 'validated', 'validate_by':validated_by_id.id})
            name = rec.name
            if(rec.element_info == False):
                comp = rec.env['res.company'].search([])
                for c in comp:
                    rec.env['crm.lead'].create({
                        'name': name,
                        'project_id': rec.id,
                        # 'planned_revenue': self.planned_revenue,
                        # 'bu_responsible_id': c.id or '',
                        'bu_id': c.id,
                        'user_id': False,
                        'company_id': c.id,
                        'project_info': rec.other_info,
                        'project_element_info': rec.element_info,
                        'date_created': fields.Date.today(),
                        })

            if(rec.element_info != False):
                keywords = rec.env['project.crm.keywords'].search([])
                text = rec.element_info
                list_element = []
                list_key = []
                list_k = []

                for lk in keywords:
                    list_key.append(lk.name)
                
                for w in text.split("\n"):
                    list_element.append(w)


                for k in list_key:
                    list_k.append(k)


                match = [t for t in list_element if any(s in t for s in list_k)]

                comp = rec.env['res.company'].search([])

                for m in match:
                    for a in keywords:
                        if(a.name in m):
                            for c in comp:
                                if(a.company_id.id == c.id):
                                    rec.env['crm.lead'].create({
                                        'name': name + m,
                                        'project_id': rec.id,
                                        # 'planned_revenue': self.planned_revenue,
                                        # 'bu_responsible_id': c.id or '',
                                        'bu_id': c.id,
                                        'user_id': False,
                                        'company_id': c.id,
                                        'project_info': rec.other_info,
                                        'project_element_info': rec.element_info,
                                        'date_created': fields.Date.today(),
                                        })
                


    def action_validate(self):
        validated_by_id = self.env.user
        self.write({'stage_id': 'validated', 'validate_by':validated_by_id.id})
        return self.auto_create_leads()

    def action_duplicate(self):
        return self.write({'stage_id': 'duplicate'})

    def _stage_find(self, team_id=False, domain=None, order='sequence'):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :returns crm.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for lead in self:
            if lead.team_id:
                team_ids.add(lead.team_id.id)
        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_id', '=', False), ('team_id', 'in', list(team_ids))]
        else:
            search_domain = [('team_id', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.crm.stage'].search(search_domain, order=order, limit=1)


    def auto_create_leads(self):
        name = self.name
        if(self.element_info == False):
            comp = self.env['res.company'].search([])
            for c in comp:
                self.env['crm.lead'].create({
                    'name': name,
                    'project_id': self.id,
                    # 'planned_revenue': self.planned_revenue,
                    # 'bu_responsible_id': c.id or '',
                    'bu_id': c.id,
                    'user_id': False,
                    'company_id': c.id,
                    'project_info': self.other_info,
                    'project_element_info': self.element_info,
                    'date_created': fields.Date.today(),
                    })

        if(self.element_info != False):
            keywords = self.env['project.crm.keywords'].search([])
            text = self.element_info
            list_element = []
            list_key = []
            list_k = []

            for lk in keywords:
                list_key.append(lk.name)
            
            for w in text.split("\n"):
                list_element.append(w)


            for k in list_key:
                list_k.append(k)


            match = [t for t in list_element if any(s in t for s in list_k)]

            comp = self.env['res.company'].search([])

            for m in match:
                for a in keywords:
                    if(a.name in m):
                        for c in comp:
                            if(a.company_id.id == c.id):
                                self.env['crm.lead'].create({
                                    'name': name + m,
                                    'project_id': self.id,
                                    # 'planned_revenue': self.planned_revenue,
                                    # 'bu_responsible_id': c.id or '',
                                    'bu_id': c.id,
                                    'user_id': False,
                                    'company_id': c.id,
                                    'project_info': self.other_info,
                                    'project_element_info': self.element_info,
                                    'date_created': fields.Date.today(),
                                    })
            


    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        stage_ids = self.env['project.crm.stage'].search([])
        return stage_ids

    @api.model
    def create(self, vals):
        obj = super(ProjectCRM, self).create(vals)
        if obj.project_code == '/':
            number = self.env['ir.sequence'].get('project.crm') or '/'
            obj.write({'project_code': number})
        return obj



# class GSMAutoAssignKeyword(models.Model):
#     _name = 'gsm.assign'
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = 'Business Unit Keyword (Assign)'

#     name = fields.Char("Keyword")
#     company_id = fields.Many2many('res.company',string="Business Unit")
#     next_generate_date = fields.Date('Next Assign Date')
#     project_value = fields.Char("Value Greater than")
#     active = fields.Boolean("Active")

#     @api.model
#     def assign_bu(self):
#         bci_list = self.env['project.stage'].search([])

#         bci_general_text = []

#         for b in bci_list:
#             bci.





class ProjectOwnerType(models.Model):
    _name = 'project.owner.type'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Project Owner Type'


    name = fields.Char('Type')


class ProjectDevelopmentType(models.Model):
    _name = 'project.dev.type'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Project Development Type'


    name = fields.Char('Type')



class BuProjectId(models.Model):
    _name = 'bu.project.id'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'BU Project ID'


    name = fields.Char('Bu Project ID')
    bu_line_id = fields.Many2one('project.crm', string='BU Reference', required=True, ondelete='cascade', index=True, copy=False)
    bu_company_id = fields.Many2one('res.company', string='Business Unit', index=True)
    # project_id = fields.Many2one(related='bu_line_id.project_id', string="Project", readonly=False)
    # client_name = fields.Many2one(related='order_id.partner_id', store=True, string='client name')
    

class ProjectCrmStage(models.Model):
    _name = 'project.crm.stage'
    _inherit = ['mail.thread.cc','mail.thread.cc']
    _rec_name = 'name'
    _order = "sequence, name, id"
    _description = 'Stage for project'

    name = fields.Char("Stage")
    stage_code = fields.Char("Code")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    fold = fields.Boolean('Folded in project stages',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    team_id = fields.Many2one('crm.team', string='Sales Team', ondelete='set null',
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')

class ProjectCrmCategory(models.Model):
    _name = 'project.crm.category'
    _inherit = ['mail.thread.cc','mail.thread.cc']
    _description = 'Category for each project'

    name = fields.Char("Category")
    parent_id = fields.Many2one('project.crm.category', string="Parent Category")
    category_notes = fields.Text('Notes')

class ProjectCrmStatus(models.Model):
    _name = 'project.crm.status'
    _inherit = ['mail.thread.cc','mail.thread.cc']
    _description = 'Status for each project'

    status_code = fields.Char("Code")
    name = fields.Char("Status")
    color = fields.Integer('Color Index')

class ProjectCrmKeywords(models.Model):
    _name = 'project.crm.keywords'
    _inherit = ['mail.thread.cc','mail.thread.cc']
    _description = 'Keywords from project to auto-generate leads'

    name = fields.Char("Keyword")
    # auto_assign = fields.Many2one('res.partner', string="Auto-assign")
    company_id = fields.Many2one('res.company', string="Company")
