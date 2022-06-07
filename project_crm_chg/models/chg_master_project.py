# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID,_
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import RedirectWarning,UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')

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

class ProjectCRMMaster(models.Model):
    _name = 'master.project'
    _inherit = ['mail.thread.cc','mail.thread.cc','mail.thread', 'mail.activity.mixin']

    _description = "Project/CRM Master"


    def _get_user_id(self):
        return self.env.uid

    def _get_user_company_id(self):
        return self.env.company.id

    def _default_project_id(self):
        return self.env['master.project'].browse(self._context.get('active_ids'))

    def _default_team_id(self, user_id):
        domain = [('use_leads', '=', True)] if self._context.get('default_type') != "lead" or self.type != 'lead' else [('use_opportunities', '!=', True)]
        return self.env['crm.team']._get_default_team_id(user_id=user_id, domain=domain)

    def _default_stage_id(self):
        team = self._default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id

    combine_project_name = fields.Char("Combine Project Name")
    bci_related_project = fields.Many2one('project.crm',string="BCI Related")
    province1 = fields.Char("Province")
    address = fields.Text("Full Address")
    name = fields.Char("Project Name")
    requestor = fields.Many2one('res.users', string="Request By")
    requestor_company = fields.Many2one('res.company', string="Requestor's Company")
    is_related_project = fields.Boolean("Is Related Project?", default=True)
    is_bci_project = fields.Boolean("BCI Project?", default=True)
    project_code = fields.Char("GSM Project ID")
    project_type = fields.Char("Project Type")
    bci_project_code = fields.Char("BCI Project ID")
    project_location = fields.Char("Project Location")
    #parties involved#
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
    
    # project_civil_work_contractor = fields.Many2one('res.partner', string="Civil Work Contractor")
    # pcw_contractor_contact1 = fields.Many2one('res.partner', string="Contact 1")
    # pcw_contractor_contact2 = fields.Many2one('res.partner', string="Contact 2")
    project_owner1 = fields.Many2one('res.partner', string="Owner 1")
    project_owner1_contact1 = fields.Many2one('res.partner', string="Owner 1 Contact 1")
    project_owner1_contact2 = fields.Many2one('res.partner', string="Owner 1 Contact 2")
    reject_reason = fields.Text("Rejected Reason")
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
    project_level_to_filter = fields.Many2one(related='crmlead_ids.crm_project_level',string="Project Level",store=True)
    bu_to_filter = fields.Many2one(related='crmlead_ids.company_id',string="Business Unit Involved",store=True)


    #parties involved#
    # bu_involved_ids = fields.Selection([('starken_aac','Starken AAC Sdn. Bhd.'),
    #                              ('starken_aac2','Starken AAC 2 Sdn. Bhd'),
    #                              ('concrete_holding','Chin Hin Concrete Holding Sdn Bhd'),
    #                              ('epic_diversity','Epic Diversity Sdn. Bhd.'),
    #                              ('gcast','Gcast'),
    #                              ('kempurna','Kempurna Sdn. Bhd.'),
    #                              ('metex_steel','Metex Steel Sdn. Bhd.'),
    #                              ('midah_group','Midah Group'),
    #                              ('midah_industries','Midah Industries Sdn. Bhd.'),
    #                              ('signature_kitchen','Signature International Berhad'),
    #                              ('starken_drymix','Starken Drymix Solutions'),
    #                              ('uhpc','UHPC'),],string="Company Involves")
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
    stage_id = fields.Selection([('new','New'),('waiting','Waiting Approval'),('validated','Validated'),('duplicate','Duplicate'),('cancelled','Cancelled')], default='new',tracking=True)
    opportunity_count = fields.Integer("Opportunity", compute='_compute_opportunity_count')
    opportunity_count_ids = fields.Many2many('crm.lead', compute="_compute_opportunity_count", string='Opportunities Count', help='Technical field used for stat button')
    created_by = fields.Many2one('res.users',string="PIC", default=lambda self: self.env.user)
    validate_by = fields.Many2one('res.users','Validate By')
    # bu_company = fields.Many2one('res.company', string='Business Unit', index=True, default=lambda self: self.env.company.id)
    lead_ids = fields.Many2many('crm.lead', string="Leads")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    team_id = fields.Many2one('crm.team', string='Sales Team', default=lambda self: self._default_team_id(self.env.uid),
        index=True, tracking=True, help='When sending mails, the default email address is taken from the Sales Team.')
    project_stage_id = fields.Many2one('project.crm.stage', string='BCI Project Stage', ondelete='restrict', tracking=True, index=True, copy=False,
        group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    # bu_project_ids = fields.One2many('bu.project.id', 'bu_line_id',string="BU Project ID")
    # bu_prjt_ids = fields.One2many('crm.lead', 'bu_lines_master_id',string="BU Project ID")
    crmlead_ids = fields.One2many('crm.lead', 'master_id',domain="[(1,'=',1)]",store=True)
    # bu_id = fields.Char("Business Unit ID")
    town = fields.Char("Town")
    project_id = fields.Many2one('master.project', string="", ondelete='cascade', index=True, copy=False, readonly=True, default=_default_project_id)
    project_owner_type = fields.Many2one('project.owner.type', string="Owner Type")
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
    project_language = fields.Char("Language")
    project_last = fields.Boolean("BCI Project Last")
    project_notes = fields.Text("Project Notes")
    project_green_building_rating = fields.Char("Green Building Rating")
    project_status_description = fields.Char("Project Status Description")
    project_units_residential = fields.Char("Project Units Residential")
    project_units_industrial = fields.Char("Project Units Industrial")
    project_category1 = fields.Many2one('project.crm.category',string="Category 1")
    project_category2 = fields.Many2one('project.crm.category',string="Category 2")
    project_category3 = fields.Many2one('project.crm.category',string="Category 3")
    project_category4 = fields.Many2one('project.crm.category',string="Category 4")
    project_category5 = fields.Many2one('project.crm.category',string="Category 5")
    project_category6 = fields.Many2one('project.crm.category',string="Category 6")
    project_category7 = fields.Many2one('project.crm.category',string="Category 7")
    project_category8 = fields.Many2one('project.crm.category',string="Category 8")

    project_subcategory1 = fields.Many2one('project.crm.category',string="Sub-Category 1")
    project_subcategory2 = fields.Many2one('project.crm.category',string="Sub-Category 2")
    project_subcategory3 = fields.Many2one('project.crm.category',string="Sub-Category 3")
    project_subcategory4 = fields.Many2one('project.crm.category',string="Sub-Category 4")
    project_subcategory5 = fields.Many2one('project.crm.category',string="Sub-Category 5")
    project_subcategory6 = fields.Many2one('project.crm.category',string="Sub-Category 6")
    project_subcategory7 = fields.Many2one('project.crm.category',string="Sub-Category 7")
    project_subcategory8 = fields.Many2one('project.crm.category',string="Sub-Category 8")
    non_bci_title = fields.Char(string="Non-BCI Title")
    project_categ = fields.Many2one('project.crm.categ', string="Project Category")
    urllink = fields.Char('Link')
    p_category = fields.Many2many('project.crm.category', string="Category")
    gsm_project_level_to_filter = fields.Many2one(related='crmlead_ids.parent_project_level',string="GSM Project Level",store=True)
    bu_to_filter = fields.Many2one(related='crmlead_ids.company_id',string="Business Unit Involved",store=True)

    @api.depends('project_category1','project_category2','project_category3','project_category4'
                    ,'project_category5','project_category6','project_category7','project_category8')
    @api.depends('project_category1')
    def set_category_many2many(self):
        # lead.meeting_ids = [(4, self.id)] 
        bci = self.env['master.project'].search([])

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

# total = fields.Float(compute="_compute_bci_info")



    @api.depends('name','project_type')
    @api.onchange('project_type')
    def set_new_name(self):
        master = self.env['master.project'].search([])
        for val in master:
            if val.name:
                if val.project_type:
                    val.write({
                        'combine_project_name': val.project_type+' : ' + val.name
                    })

    @api.depends('bci_related_project')
    def get_all_bci_info(self):
        master = self.env['master.project'].search([])
        for val in master:
            if val.bci_related_project:
                val.write({
                    'project_type':val.bci_related_project.project_type,
                    'project_category1':val.bci_related_project.project_category1.id,
                    'project_category2':val.bci_related_project.project_category2.id,
                    'project_category3':val.bci_related_project.project_category3.id,
                    'project_category4':val.bci_related_project.project_category4.id,
                    'project_category5':val.bci_related_project.project_category5.id,
                    'project_category6':val.bci_related_project.project_category6.id,
                    'project_category7':val.bci_related_project.project_category7.id,
                    'project_category8':val.bci_related_project.project_category8.id,
                    'project_subcategory1':val.bci_related_project.project_subcategory1.id,
                    'project_subcategory2':val.bci_related_project.project_subcategory2.id,
                    'project_subcategory3':val.bci_related_project.project_subcategory3.id,
                    'project_subcategory4':val.bci_related_project.project_subcategory4.id,
                    'project_subcategory5':val.bci_related_project.project_subcategory5.id,
                    'project_subcategory6':val.bci_related_project.project_subcategory6.id,
                    'project_subcategory7':val.bci_related_project.project_subcategory7.id,
                    'project_subcategory8':val.bci_related_project.project_subcategory8.id,
                    })

    def set_validated(self):
        master = self.env['master.project'].search([])
        for m in master:
            m.write({"stage_id": 'validated'})

    def get_bci_stage(self):
        master = self.env['master.project'].search([])
        for m in master:
            if(m.bci_related_project):
                m.write({
                    'project_stage_id':m.bci_related_project.project_stage_id.id
                    })

        leads = self.env['crm.lead'].search([])
        for l in leads:
            if(l.master_bci_related):
                l.write({
                    'bci_project_stage':l.master_bci_related.project_stage_id.id
                    })

    @api.depends('bci_project_code')
    def copy_bci_info_to_master(self):
        # non_exist = self._get_non_existing_master()
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
                if(b.bci_project_code == a.bci_project_code):
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
                        'crm_cntrctrs':[(6,0, b.project_main_contractor1.ids),(6,0, b.project_main_contractor2.ids),(6,0, b.contractor1.ids),(6,0, b.turnkey_contractor1.ids)],
                        'crm_sbcns_aplctrs':[(6,0, b.project_sub_contractor1.ids)],
                        # 'master_id': b,
                        })



    @api.depends('bci_project_code')
    def get_gsm_id(self):
        master = self.env['master.project'].search([])
        leads = self.env['crm.lead'].search([])

        for m in master:
            for l in leads:
                if(m.bci_project_code == l.crm_bci_id):
                    m.write({"project_code": l.crm_project_id})


    @api.depends('crm_bci_id')
    def link_bci_master(self):
        master = self.env['master.project'].search([])
        bci = self.env['project.crm'].search([])
        # if self.crm_bci_id:
        for m in master:
            for l in bci:
                if m.bci_project_code:
                    if m.bci_project_code == l.bci_project_code:
                        m.bci_related_project = l.id

    #@api.depends('crm_bci_id')
    def link_from_bci_to_master(self):
        master = self.env['master.project'].search([])
        bci = self.env['project.crm'].search([])

        for m in master:
            if(m.is_bci_project == True):
                if(not m.bci_related_project):
                    for b in bci:
                        if(m.bci_project_code == b.bci_project_code):
                            m.write({'bci_related_project':b.id})    


    def generate_leads(self):
        requestor_id = self._get_user_id()
        comp = self._get_user_company_id()
        partner = self.env.user.partner_id
        master = self.env['master.project'].search([])
        leads = self.env['crm.lead'].search([])

        # exist_in_master = []
        exist_in_leads = []

        # for m in master:
        #     if m.bci_project_code:
        #         exist_in_master.append(m.bci_project_code)

        for l in leads:
            if l.crm_bci_id:
                if(l.company_id.id == comp):
                    exist_in_leads.append(l.crm_bci_id)

        comp_exist_in_leads = []

        for la in leads:
            if la.crm_bci_id:
                comp_exist_in_leads.append(la.company_id.id)



        for b in self:
            if(b.bci_project_code in exist_in_leads):
                # if(comp in comp_exist_in_leads):
                    # print("XXXX  ",comp)
                    # print("YYYY  ",comp_exist_in_leads)                          
                    message_id = self.env['message.wizard'].create({'message': _("Project already exist in your company's CRM!")})
                    return {
                        'name': _('Exist!'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'message.wizard',
                        'res_id': message_id.id,
                        'target': 'new'
                    } 

            elif(b.bci_project_code not in exist_in_leads):
                self.env['crm.lead'].sudo().create({
                    'sub_project_code': b.project_code,
                    'crm_bci_id': b.bci_project_code,
                    'master_id': b.id,
                    'bci_province1':b.province1,
                    'name': b.name,
                    'team_id': False,
                    'user_id': requestor_id,
                    # 'crm_prj_own_sales': partner.id,
                    # 'crm_prj_own_mark': partner.id,
                    'crm_title': b.name,
                    'company_id': comp,
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


               # m.write({"province1": b.province1})

    @api.model
    def action_master_to_approved(self):
        action = self.env.ref('project_crm_chg.project_master_action_pipeline').read()[0]
        user_team_id = self.env.user.sale_team_id.id
        if user_team_id:
            # To ensure that the team is readable in multi company
            user_team_id = self.search([('id', '=', user_team_id)], limit=1).id
        else:
            user_team_id = self.search([], limit=1).id
            action['help'] = _("""<p class='o_view_nocontent_smiling_face'>Add new opportunities</p><p>
    Looks like you are not a member of a Sales Team. You should add yourself
    as a member of one of the Sales Team.
</p>""")
            if user_team_id:
                action['help'] += "<p>As you don't belong to any Sales Team, Odoo opens the first one by default.</p>"

        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        if user_team_id:
            action_context['default_team_id'] = user_team_id

        action['context'] = action_context
        return action

    # @api.depends('crm_bci_id')
    def update_from_bci_to_master(self):
        master = self.env['master.project'].search([])
        bci = self.env['project.crm'].search([])

        for b in bci:
            for a in master:
                if(a.bci_project_code == b.bci_project_code):
                    a.write({
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

                })

    @api.depends('bci_project_code')
    def get_gsm_id2(self):
        master = self.env['master.project'].search([])
        leads = self.env['crm.lead'].search([])

        # for m in master:
        #     for l in leads:
        #         if(m.bci_project_code == l.crm_bci_id):
        #             m.write({"project_code": l.sub_project_code})
        for l in leads:
            for m in master:
                if(not m.project_code):
                    if(l.master_id.id == m.id):
                        m.write({"project_code": l.sub_project_code})

    # @api.multi
    # def try_get_lead(self,fields_list):
    # def try_get_lead(self):
    #     # res = super(ProjectCRM, self).default_get(fields_list)
    #     leads = self.env['crm.lead'].search([])
    #     active_ids = self.id
    #     for a in leads:
    #         if(a.project_id.id == active_ids):
    #             print("XXXX ", a.name)
    #             # print("YYYY ", a.project_id.id)
                # print("ZZZZ ", active_ids)
        # vals = [(0, 0, {'field_1': value_1, 'field_2': value_2}),
        #         (0, 0, {'field_1': value_1, 'field_2': value_2})]
        # res.update({'your_o2m_field': vals})
        # return res

    # @api.model
    # def default_get(self, fields):
    #     vals = super(ProjectCRM, self).default_get(fields)
    #     vals['bu_project_id'] = self.id
    #     library_management_lines = [(5,0,0)]
    #     books_rec = self.env['crm.lead'].search([])
    #     for rec in books_rec:
    #         line = (0,0,{
    #             'library_management_id' : self.id,
    #             'book_id': rec.id,
    #             'issue_date': date.today(),
    #         })
    #         library_management_lines.append(line)
    #     vals['library_management_line_ids'] = library_management_lines
    #     return vals
    # @api.multi
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         name = record.project_developer_contact1
    #         if record.project_developer:
    #             name = record.name.name + "," + record.project_developer_contact1.function
    #         res.append((record.id, name))
    #     return res

    # @api.depends_context('company')
    # def _compute_display_info(self):
    #     for record in self:
    #         record.display_info = record.info + record.company_info

    # @api.depends('project_code')
    def insert_bu(self):
        master = self.env['master.project'].search([])
        leads = self.env['crm.lead'].search([])
 
        for m in master:
            for l in leads:
                    if(l.crm_bci_id == m.bci_project_code):
                        for a in m.lead_ids:
                            m.update({
                                'lead_ids':[(3,0,l.ids)]
                                })



    def _compute_opportunity_count(self):
        for project in self:
            project.opportunity_count_ids = self.env['crm.lead'].search([('master_id', '=', project.id)])
            project.opportunity_count = len(project.opportunity_count_ids)

    def action_view_opportunity(self):
        '''
        This function returns an action that displays the leads from project.
        '''
        action = self.env.ref('project_crm_chg.crm_lead_opportunities_from_master').read()[0]
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
                                        'bu_id': c.id,
                                        'user_id': False,
                                        'company_id': c.id,
                                        'project_info': rec.other_info,
                                        'project_element_info': rec.element_info,
                                        'date_created': fields.Date.today(),
                                        })
                
    def action_validate_all(self):
        # validated_by_id = self.env.user
        master = self.env['master.project'].search([])
        for m in master:
            m.write({'stage_id': 'validated'})
        # return self.auto_create_leads()

    def action_validate(self):
        validated_by_id = self.env.user
        self.write({'stage_id': 'validated', 'validate_by':validated_by_id.id})
        if(self.bci_project_code):
            number = self.env['ir.sequence'].get('master.project1')
            self.write({'project_code': number})
        if(not self.bci_project_code):
            if(self.project_code == '/'):
                number2 = self.env['ir.sequence'].get('master.project2')
                self.write({'project_code': number2})
        self.validated_notification()
        return self.auto_create_leads_for_requestor()


    def validated_notification(self, create_id = False):
        self_id = self.env.uid
        # lop_name = False
        # if 'name' in vals:
        #     lop_name = vals['name']
        # else:
        lop_name = self.name
        if self.requestor:
            if self.requestor.id != self_id and self.requestor.id != False:
                self.notify_requestor(lop_name, 'Requestor', self.requestor.id, self_id, create_id, True)

        cu_partner = self.env['res.users'].sudo().search([('id','=',self_id)], limit=1)
        if cu_partner:
            cu_partner = cu_partner.partner_id.id

        if self.requestor.id:
            if cu_partner:
                if self.requestor.id != cu_partner:
                    if self.stage_id == 'validated':
                        self.notify_requestor(lop_name, 'Requestor', self.requestor.id, self_id, create_id )

    def waiting_notification(self, create_id = False):
        self_id = self.env.uid
        # lop_name = False
        # if 'name' in vals:
        #     lop_name = vals['name']
        # else:
        lop_name = self.name
        if self.requestor:
            if self.requestor.id != self_id and self.requestor.id != False:
                self.notify_gsm(lop_name, 'Requestor', self.requestor.id, self_id, create_id, True)

        cu_partner = self.env['res.users'].sudo().search([('id','=',self_id)], limit=1)
        if cu_partner:
            cu_partner = cu_partner.partner_id.id

        if self.requestor.id:
            if cu_partner:
                if self.requestor.id != cu_partner:
                    if self.stage_id == 'validated':
                        self.notify_gsm(lop_name, 'Requestor', self.requestor.id, self_id, create_id )


    def notify_requestor(self, lop_name, title, id_to_send, sender_id, create_id, is_user_id = False):
        email_obj = False
        email_template_name = 'project_master_validated_email'
        if not is_user_id:
            recv_user = self.env['res.users'].sudo().search([('partner_id','=',id_to_send)], limit=1)
            sndr_user = self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
            if recv_user and sndr_user:
                email_obj = { 'email_list' : [recv_user.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }
        else:
            recv_user = self.env['res.users'].sudo().search([('id','=',id_to_send)], limit=1)
            sndr_user = self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
            if recv_user and sndr_user:
                 email_obj = { 'email_list' : [recv_user.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }

        message = "Project %s has been verified." % (lop_name)

        if email_obj:
            self.send_email(email_obj['email_list'], message, email_template_name, email_obj['contexts'], create_id)

    def notify_gsm(self, lop_name, title, id_to_send, sender_id, create_id, is_user_id = False):
        email_obj = False
        email_template_name = 'project_master_non_bci_created_email'
        if not is_user_id:
            recv_user = self.env['res.users'].sudo().search([()])
            for ru in recv_user:
                if(ru.name == 'Shi Qing'):
                    sndr_user = self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
                    if recv_user and sndr_user:
                        email_obj = { 'email_list' : [ru.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }
                if(ru.name == 'Nicole Ling'):
                    sndr_user = self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
                    if recv_user and sndr_user:
                        email_obj = { 'email_list' : [ru.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }   
        else:
            recv_user = self.env['res.users'].sudo().search([('id','=',id_to_send)], limit=1)
            sndr_user = self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
            if recv_user and sndr_user:
                 email_obj = { 'email_list' : [recv_user.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }

        message = "Project %s has been created and waiting for approval." % (lop_name)

        if email_obj:
            self.send_email(email_obj['email_list'], message, email_template_name, email_obj['contexts'], create_id)



    def send_email(self, email_tos, subject, email_template_name, add_cntxt=False, create_id_override=False):
        context = False
        if add_cntxt:
            context = add_cntxt
        else:
            context = {}
        su_id = self.env['res.partner'].sudo().browse(SUPERUSER_ID)
        s_if = False
        if create_id_override:
            s_if = create_id_override
        else:
            s_if = self.id
        template_id = self.env['ir.model.data'].sudo().get_object_reference('project_crm_chg', email_template_name)[1]
        template_browse = self.env['mail.template'].sudo().browse(template_id)
        context['urllink'] = self.get_url_link()
        if template_browse and email_tos:
           values = template_browse.with_context(context).generate_email(s_if, fields=None)
           values['subject'] = subject
           values['email_to'] = ','.join(email_tos)
           values['email_from'] = su_id.email
           values['res_id'] = s_if
           if not values['email_to'] and not values['email_from']:
              return False
           msg = self.env['mail.mail'].sudo().create(values)
           immediate_send = True
           scheduler_id = self.env['ir.model.data'].sudo().get_object_reference('mail', 'ir_cron_mail_scheduler_action')[1]
           if scheduler_id:
              scheduler_act = self.env['ir.cron'].sudo().browse(scheduler_id)
              if scheduler_act:
                 if not scheduler_act.active:
                    immediate_send = False
           if immediate_send:
              msg.sudo().send()
           return True
        return False

    def get_url_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        return base_url

    def action_duplicate(self):
        return self.write({'stage_id': 'duplicate'})

    def action_cancel(self):
        return self.write({'stage_id': 'cancelled'})

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

    def auto_create_leads_for_requestor(self):
        name = self.name

        if(self.requestor):
            self.env['crm.lead'].create({
                'name': name,
                'bci_name': name,
                'sub_project_code':self.project_code,
                'company_id': self.requestor_company.id,
                'master_id': self.id,
                'crm_title': self.name,
                'user_id': self.requestor.id,
                'crm_prj_value': self.project_value,
                'crm_startdate': self.start_date,
                'crm_enddate': self.end_date,
                'crm_prj_town': self.town,
                'street': self.street,
                'street2': self.street2,
                'city': self.city,
                'state_id': self.state_id.id or '',
                'zip': self.zip,
                'country_id': self.country_id.id or '',
                'crm_prj_addr': str(self.street)+" ,"+str(self.street2)+" ,"+str(self.city)+" ,"+str(self.zip)+" ,"+str(self.state_id.name)+" ,"+str(self.country_id.name),
                'bci_region': self.bci_region,
                'bci_ownership_type': self.project_owner_type.id,
                'bci_project_category': self.project_category1.id,
                'bci_project_stage': self.project_stage_id.id,
                'bci_project_value': self.project_value,
                'bci_start_date': self.start_date,
                'bci_end_date': self.end_date,
                'bci_project_remarks': self.project_remarks,
                'bci_element_info': self.element_info,
                'crm_prj_dev1':[(6,0, self.project_developer1.ids)],
                'crm_prj_arc1':[(6,0, self.project_architect1.ids)],
                'crm_prj_cseng1':[(6,0, self.consulting_engineer1.ids)],
                'crm_prj_qs1':[(6,0, self.project_quantity_surveyor1.ids)],
                'crm_cntrctrs':[(6,0, self.project_main_contractor1.ids),(6,0, self.project_main_contractor2.ids),(6,0, self.contractor1.ids),(6,0, self.turnkey_contractor1.ids)],
                'crm_sbcns_aplctrs':[(6,0, self.project_sub_contractor1.ids)],
                })
        message_id = self.env['message.wizard'].create({'message': _("Requested project approved. Sub-Project successfully created for %s!" % self.requestor_company.name)})
        return {
            'name': _('Approved'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            # pass the id
            'res_id': message_id.id,
            'target': 'new'
        }

    def auto_create_leads(self):
        name = self.name
        exc_comp = [1,6]
        if(self.element_info == False):
            comp = self.env['res.company'].search([('id','not in',exc_comp)])
            for c in comp:
                self.env['crm.lead'].create({
                    'name': name,
                    'bu_id': c.id,
                    'user_id': False,
                    'company_id': c.id,
                    'bci_name': name,
                    'bci_region':self.bci_region or '',
                    'bci_ownership_type':self.project_owner_type.id or '',
                    'bci_start_date':self.start_date or False,
                    'bci_end_date':self.end_date or False,
                    'bci_project_value':self.project_value or '',
                    'bci_project_category':self.project_category1.id or '',
                    'bci_project_remarks':self.project_remarks or '',
                    'bci_element_info':self.element_info or '',
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
                                    # 'project_id': self.id,
                                    # 'planned_revenue': self.planned_revenue,
                                    # 'bu_responsible_id': c.id or '',
                                    'bci_region':b.bci_region,
                                    'bci_ownership_type':b.project_owner_type.id,
                                    'bci_start_date':b.start_date,
                                    'bci_end_date':b.end_date,
                                    'bci_project_value':b.project_value,
                                    'bci_project_category':b.project_category1.id,
                                    'bci_project_remarks':b.project_remarks,
                                    'bci_element_info':b.element_info,

                })
            


    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        stage_ids = self.env['project.crm.stage'].search([])
        return stage_ids

        
    # def set_seq_id(self):
    #     if(self.project_code == '/'):
    #         if(self.bci_project_code):
    #             number = self.env['ir.sequence'].get('master.project1') or '/'
    #             self.write({'project_code': number})
    #         if(not self.bci_project_code):
    #             number2 = self.env['ir.sequence'].get('master.project2') or '/'
    #             self.write({'project_code': number2})
    
    def change_stage_to_waiting(self):
        
        # if self.stage_id == 'new':
        #     self.write({'stage_id':'waiting'})
        #     self.waiting_notification()

        message_id = self.env['message.wizard'].create({'message': _("Project successfully created and waiting for GSM Team to verify! ")})
        return {
            'name': _('Successfull'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            # pass the id
            'res_id': message_id.id,
            'target': 'new'
        }

    def get_url_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        return base_url

    @api.model
    def create(self,vals):
        requestor_id = self._get_user_id()
        comp = self._get_user_company_id()
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # copied_url = base_url+'/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        # vals['urllink'] = copied_url
        # res['record_status'] = '1'
        obj = super(ProjectCRMMaster, self).create(vals)

        # if(self.project_code == '/'):
        if(obj.bci_project_code):
            number = self.env['ir.sequence'].get('master.project1')
            obj.write({'project_code': number})
        if(not obj.bci_project_code):
            number2 = '/'
            obj.write({'project_code': number2,'requestor':requestor_id
                ,'requestor_company':comp})

        return obj

        


