from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
import xlrd
import csv
from datetime import date, datetime
import textwrap
import logging
import json


_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = 'crm.lead'


    def _get_my_default_company(self):
        company_ids = self.env.user.company_id.id
        val = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        item_ids_list = []

        for item in val:
            item_ids_list.append(item.id)

        domain = [('epicor_customer_id', '!=', False),('bu', 'in', item_ids_list)]
        return domain

    def _get_default_team_member(self):
        return self.change_value_team()


    # @api.onchange('team_id')
    # def get_member_ids(self):
    #     val = []
    #     if(self.team_id):
    #         for a in self.team_id.member_ids:
    #             val.append(a.id)

    #     domain = [('id','in',val)]
    #     return domain

        # for u in user_ids:
        #     if(u.partner_id.id == self.crm_prj_team_leader.id):
        #         domain = [()]

    # def _auto_get_related_partner(self):
    #     if(self.user_id):
    #         self.write({'related_user_id': self.user_id.partner_id})
    @api.depends('ir_quoted_amount','fd_quoted_amount','td_quoted_amount','accessories_quoted_amount','mf_quoted_amount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        #for order in self:
        amount_all = 0.0
        amount_all += self.fd_quoted_amount + self.td_quoted_amount + self.accessories_quoted_amount + self.mf_quoted_amount + self.ir_quoted_amount
        self.update({
            'amount_total': amount_all,
         })

    team_id = fields.Many2one('crm.team', string='Team')
    related_master = fields.Many2one('master.project',string="Related Master",ondelete='cascade')
    sub_project_code = fields.Char("GSM Project ID")
    user_id = fields.Many2one('res.users', string='Created By', index=True, tracking=False, default=lambda self: self.env.user, domain="[('user_ids', '!=', False)]")
    project_owner = fields.Many2one('res.partner', string="Project Owner")
    # related_user_id = fields.Many2one('res.partner',string="Project Owner",compute=_auto_get_related_partner, store=True)
    crm_project_id = fields.Char('Project ID', default="", index=True)
    crm_bci_id = fields.Char('BCI ID', default="", index=True)
    # crm_gsm_id = fields.Char('GSM ID', default="", index=True)
    crm_title = fields.Text('Project Title',store=True)
    crm_category = fields.Many2one('starken_crm.lead.category', string='Category')
    crm_startdate = fields.Date('Start Date')
    crm_enddate = fields.Date('End Date')
    crm_ibs = fields.Boolean('IBS')
    crm_gbi = fields.Boolean('GBI')
    crm_prj_status = fields.Selection([('won', 'Won'), ('lost','Lost'), ('pending','Pending')], string='Project Status')
    crm_prj_level = fields.Selection([('specifying', 'Specifying'), ('specified', 'Specified'), ('secure', 'Secure')])
    crm_prj_sec_date = fields.Date('Project Secure Date')
    crm_prj_spcd_date = fields.Date('Project Specified Date')
    crm_prj_spcy_date = fields.Date('Project Specifying Date')
    crm_des_build = fields.Boolean('Design And Build')
    crm_photo = fields.Many2many('ir.attachment', 'crm_lead_crm_photo_ir_attachments_rel', 'crm_id', 'attachment_id', string='Photo')
    crm_cstmr_srvy_sent = fields.Boolean('Customer Survey Sent')
    crm_block_m3 = fields.Float('Block m3')
    crm_block_m2 = fields.Float('Block m2')
    crm_panel_m3 = fields.Float('Panel m3')
    crm_panel_m2 = fields.Float('Panel m2')
    crm_ttl_panel_value = fields.Float('Total Panel Value', compute="calculate_panel_cost", store=True)
    crm_prj_own_mark = fields.Many2one('res.partner', string='Project Owner (Marketing)', domain="[('user_ids', '!=', False),('user_ids.company_id', '=', company_id)]", required=False,tracking=True)
    crm_prj_team_leader = fields.Many2one('res.partner', string='Team Leader', domain="[('user_ids', '!=', False),('user_ids.company_id', '=', company_id)]", required=False,tracking=True)
    gsm_assign_to = fields.Many2one('res.partner', string='GSM Assign To', domain="[('user_ids', '!=', False),('user_ids.company_id', '=', company_id)]", required=False,tracking=True)
    # related_crm_prj_own_mark = fields.Many2one('res.partner',string="Project Owner (Marketing)1")
    crm_prj_own_sales = fields.Many2one('res.partner', string='Project Owner (Sales)', domain="[('user_ids', '!=', False),('user_ids.company_id', '=', company_id)]",tracking=True)
    crm_prj_signature_sales = fields.Many2one('res.partner', string='Project Sales',tracking=True)
    # related_crm_prj_own_sales = fields.Many2one('res.partner',string="Project Owner (Sales)1")
    crm_prj_mgr = fields.Many2one('res.partner', string='Project Manager', domain="[('user_ids', '!=', False)]")
    crm_prj_dev = fields.Many2one('res.partner', string='Developer1', domain="[('partner_type.name', 'ilike', 'Developers')]")
    crm_prj_arc = fields.Many2one('res.partner', string='Architect1', domain="[('partner_type.name', 'ilike', 'Architects')]")
    crm_prj_cseng = fields.Many2one('res.partner', string='Consultant Engineer1', domain="[('partner_type.name', 'ilike', 'Consultant Engineers')]")
    crm_prj_qs = fields.Many2one('res.partner', string='Quantity Surveyor (QS)1', domain="[('partner_type.name', 'ilike', 'Quantity Surveyors')]")
    """ Newly added """
    crm_prj_town = fields.Char("Town")
    crm_prj_value = fields.Char("Project Value (M)")

    crm_dsc_info = fields.Char('Description Information')
    crm_prj_addr = fields.Text('Project Address')
    crm_ctc_roles = fields.Many2many('res.partner', 'crm_lead_crm_ctc_roles_ir_attachments_rel', 'crm_id', 'partner_id', string='Contacts Roles')
    crm_products =  fields.One2many('starken_crm.lead.products', 'crm_id', string='Products',copy=True)
    
    crm_prj_dev1 = fields.Many2many('res.partner','crm_lead_crm_dev_ir_attachments_rel', 'crm_id', 'partner_id',string='Developer', domain="[('partner_type.name', 'ilike', 'Developer')]")
    # crm_prj_dev2 = fields.Many2many('res.partner','lead_partner_id',string='Developer', domain="[('partner_type.name', 'ilike', 'Developers')]")
    # crm_prj_dev2 = fields.Many2one('res.partner',string='Developer2', domain="[('partner_type.name', 'ilike', 'Developers')]")
    crm_prj_arc1 = fields.Many2many('res.partner','crm_lead_crm_arc_ir_attachments_rel', 'crm_id', 'partner_id', string='Architect', domain="[('partner_type.name', 'ilike', 'Architect')]")
    crm_prj_cseng1 = fields.Many2many('res.partner','crm_lead_crm_cseng_ir_attachments_rel', 'crm_id', 'partner_id', string='Consultant Engineer', domain="[('partner_type.name', 'ilike', 'Consultant Engineer')]")
    crm_prj_qs1 = fields.Many2many('res.partner','crm_lead_crm_qs_ir_attachments_rel', 'crm_id', 'partner_id', string='Quantity Surveyor (QS)', domain="[('partner_type.name', 'ilike', 'Quantity Surveyor')]")    
    crm_prj_distributor = fields.Many2many('res.partner','crm_lead_crm_distributor_ir_attachments_rel', 'crm_id', 'partner_id', string='Distributor', domain="[('partner_type.name', 'ilike', 'Distributor')]")
    crm_cntrctrs = fields.Many2many('res.partner', 'crm_lead_crm_cntrctrs_ir_attachments_rel', 'crm_id', 'partner_id', string='Contractors', domain="[('partner_type.name', 'ilike', 'Contractor')]")
    crm_sbcns_aplctrs = fields.Many2many('res.partner', 'crm_lead_crm_sbcns_aplctrs_ir_attachments_rel', 'crm_id', 'partner_id', string='Subcons/Applicators', domain="[('partner_type.name', 'ilike', 'Subcon')]")
    crm_trdng_hses = fields.Many2many('res.partner', 'crm_lead_crm_trdng_hses_ir_attachments_rel', 'crm_id', 'partner_id', string='Epicor Customer', domain=_get_my_default_company)
    crm_tenderer = fields.Many2many('res.partner', 'crm_lead_crm_tenderer_ir_attachments_rel', 'crm_id', 'partner_id', string='Tenderer', domain="[('user_ids', '=', False)]")
    priority = fields.Selection([('0', '0%'), ('1', '25%'), ('2', '50%'), ('3', '75%'), ('4', '100%')], string='Priority', index=True, default='0')
    cst_probability = fields.Float('Probability', default=0, store=False, compute='get_probability_by_star')
    key_account = fields.Many2one('res.partner', 'Key Account', domain="[('parent_id', '=', False)]")
    customer_type = fields.Selection([
        ('project', 'Project'),
        ('retail', 'Retail'),
    ], string='Customer Type')
    delivery_zone = fields.Many2one('delivery.zone')
    concept_drawing = fields.Char('Concept Drawing')
    shop_drawing = fields.Char('Shop Drawing')
    crm_prj_customer = fields.Many2one('res.partner')
    crm_customer_num = fields.Char("Customer Num.")
    crm_customer_id = fields.Char("Customer ID")
    crm_customer_reg = fields.Char("Customer Reg.")
    done = fields.Boolean("DONE?",default=False)
    duplicate = fields.Boolean("Duplicate",default=False)
    bci_region = fields.Char("BCI Region")
    bci_ownership_type = fields.Many2one('project.owner.type', string="BCI Ownership Type")
    bci_project_category = fields.Many2one('project.crm.category', string="BCI Project Category")
    bci_project_stage = fields.Many2one('project.crm.stage', string="BCI Project Stage")
    bci_project_status = fields.Many2one('project.crm.status', string="BCI Project Status")
    bci_project_value = fields.Char("BCI Project Value(Million)")
    bci_start_date = fields.Date("BCI Start Date")
    bci_end_date = fields.Date("BCI End Date")
    bci_project_remarks = fields.Text("BCI Project Remarks")
    bci_element_info = fields.Text("BCI Element Info")
    bci_name = fields.Char("BCI Name")
    bci_complete_status = fields.Boolean("Completed Status", default=False)
    bci_complete_status_name = fields.Char("BCI Status", store=True)
    plant_id = fields.Many2one('bu.plant',string="Plant")
    sale_amount_total2 = fields.Monetary(compute='_compute_sale_data2', string="Sum of Orders", help="Untaxed Total of Confirmed Orders", currency_field='company_currency')
    quotation_count2 = fields.Integer(compute='_compute_sale_data2', string="Number of Quotations")
    sale_order_count2 = fields.Integer(compute='_compute_sale_data2', string="Number of Sale Orders")
    order2_ids = fields.One2many('sale.order', 'crm_project_id', string='Orders')
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    fd_quoted_amount = fields.Monetary(string='FD Quoted Amount',currency_field='company_currency', store=True, readonly=False,  tracking=4)
    td_quoted_amount = fields.Monetary(string='TD Quoted Amount',currency_field='company_currency', store=True, readonly=False,  tracking=4)
    accessories_quoted_amount = fields.Monetary(string='Accessories Quoted Amount',currency_field='company_currency', store=True, readonly=False,  tracking=4)
    mf_quoted_amount = fields.Monetary(string='MF Quoted Amount',currency_field='company_currency', store=True, readonly=False,  tracking=4)
    ir_quoted_amount = fields.Monetary(string='IR Quoted Amount',currency_field='company_currency', store=True, readonly=False,  tracking=4)
    amount_total = fields.Monetary(string='Total Potential Value',currency_field='company_currency', compute='_amount_all', store=True, readonly=False,  tracking=4)
    survey_count = fields.Integer('Surveys', compute='_compute_survey_count')
    # company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")

    @api.depends('survey_count')
    def _compute_survey_count(self):
        surveys = self.env['survey.survey'].search([])
        survey_cnt = 0
        for lead in surveys:
            if lead.state == 'open':
                survey_cnt += 1
        self.survey_count = survey_cnt

    def action_view_survey(self):
        # breakpoint()
        self.ensure_one()
        action = self.env.ref('survey.action_survey_form').read()[0]
        return action

    @api.depends('order2_ids.state', 'order2_ids.currency_id', 'order2_ids.amount_untaxed', 'order2_ids.date_order', 'order2_ids.company_id')
    def _compute_sale_data2(self):
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.order2_ids:
                if order.state in ('draft', 'sent'):
                    quotation_cnt += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id, order.date_order or fields.Date.today())
            lead.sale_amount_total2 = total
            lead.quotation_count2 = quotation_cnt
            lead.sale_order_count2 = sale_order_cnt

    def action_view_sale_quotation2(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_crm_project_id': self.id
        }
        action['domain'] = [('crm_project_id', '=', self.id), ('state', 'in', ['draft', 'sent'])]
        quotations = self.mapped('order2_ids').filtered(lambda l: l.state in ('draft', 'sent'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    def action_view_sale_order2(self):
        action = self.env.ref('sale.action_orders').read()[0]
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_crm_project_id': self.id,
        }
        action['domain'] = [('crm_project_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.mapped('order_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action

    @api.onchange('team_id2')
    def compute_crm_prj_signature_sales_domain(self):
        team = self.team_id2
        if(team):
            val = []
            for a in team.member_ids:
                val.append(a.partner_id.id)
            return {'domain': {'crm_prj_signature_sales': [('id', 'in', val)]}}


    @api.onchange('team_id2')
    def _get_default_team_leader(self):
        user_ids = self.env['res.users'].search([])
        team = self.team_id2
        if(team):
            self.crm_prj_team_leader = team.user_id.partner_id.id

        val = []
        for a in team.member_ids:
            val.append(a.partner_id.id)

    @api.onchange('crm_prj_team_leader')
    def autochange_mark(self):
        if(self.crm_prj_team_leader):
            self.crm_prj_own_mark = self.crm_prj_team_leader.id

    @api.onchange('crm_prj_signature_sales')
    def autochange_sales(self):
        if(self.crm_prj_signature_sales):
            self.crm_prj_own_sales = self.crm_prj_signature_sales.id

    @api.model
    def _onchange_lead_values(self, crm_prj_team_leader):
        """ returns new values when user_id has changed """
        if not crm_prj_team_leader:
            return {}
        if crm_prj_team_leader and self._context.get('team_id2'):
            team = self.env['crm.team'].browse(self._context['team_id2'])
            if crm_prj_team_leader in team.member_ids.ids or crm_prj_team_leader == team.crm_prj_team_leader.id:
                return {}
        team_id2 = self._default_team_id(crm_prj_team_leader)
        return {'team_id2': team_id2}

    @api.onchange('crm_prj_team_leader')
    def _onchange_lead_mark(self):
        """ When changing the user, also set a team_id or restrict team id to the ones user_id is member of. """
        users = self.env['res.users'].search([])
        for u in users:
            if(self.crm_prj_team_leader.id == u.partner_id.id):
                if u.sale_team_id:
                    values = self._onchange_lead_values(u.id)
                    self.update(values)

    @api.model
    def _onchange_signature_sales_values(self, crm_prj_signature_sales):
        """ returns new values when user_id has changed """
        if not crm_prj_signature_sales:
            return {}
        if crm_prj_signature_sales and self._context.get('team_id2'):
            team = self.env['crm.team'].browse(self._context['team_id2'])
            if crm_prj_signature_sales in team.member_ids.ids or crm_prj_signature_sales == team.crm_prj_signature_sales.id:
                return {}
        team_id2 = self._default_team_id(crm_prj_signature_sales)
        return {'team_id2': team_id2}

    @api.onchange('crm_prj_signature_sales')
    def _onchange_signature_sales(self):
        """ When changing the user, also set a team_id or restrict team id to the ones user_id is member of. """
        users = self.env['res.users'].search([])
        for u in users:
            if(self.crm_prj_signature_sales.id == u.partner_id.id):
                if u.sale_team_id:
                    values = self._onchange_signature_sales_values(u.id)
                    self.update(values)


    @api.model
    def _onchange_mark_values(self, crm_prj_own_mark):
        """ returns new values when user_id has changed """
        if not crm_prj_own_mark:
            return {}
        if crm_prj_own_mark and self._context.get('team_id2'):
            team = self.env['crm.team'].browse(self._context['team_id2'])
            if crm_prj_own_mark in team.member_ids.ids or crm_prj_own_mark == team.crm_prj_own_mark.id:
                return {}
        team_id2 = self._default_team_id(crm_prj_own_mark)
        return {'team_id2': team_id2}

    @api.onchange('crm_prj_own_mark')
    def _onchange_prj_mark(self):
        """ When changing the user, also set a team_id or restrict team id to the ones user_id is member of. """
        users = self.env['res.users'].search([])
        for u in users:
            if(self.crm_prj_own_mark.id == u.partner_id.id):
                if u.sale_team_id:
                    values = self._onchange_mark_values(u.id)
                    self.update(values)


    @api.model
    def _onchange_own_sales_values(self, crm_prj_own_sales):
        """ returns new values when user_id has changed """
        if not crm_prj_own_sales:
            return {}
        if crm_prj_own_sales and self._context.get('team_id2'):
            team = self.env['crm.team'].browse(self._context['team_id2'])
            if crm_prj_own_sales in team.member_ids.ids or crm_prj_own_sales == team.crm_prj_own_sales.id:
                return {}
        team_id2 = self._default_team_id(crm_prj_own_sales)
        return {'team_id2': team_id2}

    @api.onchange('crm_prj_own_sales')
    def _onchange_prj_sales(self):
        """ When changing the user, also set a team_id or restrict team id to the ones user_id is member of. """
        users = self.env['res.users'].search([])
        for u in users:
            if(self.crm_prj_own_sales.id == u.partner_id.id):
                if u.sale_team_id:
                    values = self._onchange_own_sales_values(u.id)
                    self.update(values)

    def compute_status_name(self):
        leads = self.env['crm.lead'].sudo().search([])
        for l in leads:
            if(l.bci_complete_status == False):
                l.write({'bci_complete_status_name': 'Ongoing'})
            if(l.bci_complete_status == True):
                l.write({'bci_complete_status_name': 'Completed'})

    @api.onchange('bci_complete_status')
    def set_complete_status_name(self):
        for rec in self:
            if rec.bci_complete_status == True:
                # rec.write({'bci_complete_status_name': 'Completed'})
                rec.bci_complete_status_name = 'Completed'
            else:
                rec.bci_complete_status_name = 'Ongoing'
                # rec.write({'bci_complete_status_name': 'Ongoing'})

    def mark_as_duplicate2(self):
        stage_id = self.env['crm.stage'].sudo().search([('name','=','Duplicate')]).id
        leads = self.env['crm.lead'].sudo().search([])
        for a in leads:
            if(a.duplicate == True):
                # print("XXX ",a.stage_id.name)
                a.write({'stage_id': stage_id})

    def mark_as_duplicate(self):
        stage_id = self.env['crm.stage'].sudo().search([('name','=','Duplicate')]).id
        if(self.id):
            self.write({'duplicate': True,'stage_id': stage_id})

    def get_all_id(self):

        if(self.id):
            self.write({'duplicate': True,'stage_id': stage_id})


    def get_bci_status_from_csv(self):
        values = []
        included_cols = [1]
        # file_path = ('/home/aziz/Downloads/bci.project_information.csv')
        with open('/home/aziz/Downloads/bci.project_information.csv', newline='') as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                values.append(row)

        return values

    def set_lead_bci_status_from_csv(self):
        today = date.today()
        # print("Today's date:", today)
        # print("TODAY  ", today.strftime("%m/%d/%Y %H:%M:%S"))
        t = today.strftime("%d/%m/%Y")
        today_date = datetime.strptime(t,"%d/%m/%Y")
        leads = self.env['crm.lead'].sudo().search([])
        vals = self.get_bci_status_from_csv()
        
        for l in leads:
            for v in vals:
                # date_object = datetime.strftime(v[2], "%m/%d/%Y %H:%M:%S")
                # l.bci_end_date = datetime.strftime(l.bci_end_date, "%m/%d/%Y %H:%M:%S")
                if(v[2]):
                    # date_v2 = datetime.strptime(v[2],"%d/%m/%Y")
                    # print("AAAAAAAAA ", type(today_date))
                    # print("BBBBBBBBB ", type(date_v2))
                    if(l.crm_bci_id == v[0]):
                        if(v[1] == 'Construction'):
                            if(datetime.strptime(v[2],"%d/%m/%Y") < today_date):
                        
                                # print("LEAD  ", l.name)
                                l.write({'bci_complete_status':True, 'bci_project_stage':2})



    def get_done_list(self):
        # df = pd.read_excel("/home/aziz/Desktop/EXCEL/DONESORTING.xlsx", header=None)
        file_path = ('/home/aziz/Desktop/EXCEL/aaa.xlsx')

    # Import complete excel workbook
        excel_workbook = xlrd.open_workbook(file_path)
        # Import specific sheet by index
        excel_sheet = excel_workbook.sheet_by_index(0)

        # Create array for each row
        relevantData = []
        ids = self.env['crm.lead'].sudo().search([])
        # Loop through each row of excel sheet 
        for row in range(excel_sheet.nrows): #nrows returns number of rows
            # If even
            if row % 2 != 0:
                # Convert row to array and append to relevantData array
                # relevantData.append(rowToArray(row))

                val = list(map(int, excel_sheet.cell_value(row,0).split()))
            # print(val)
                for i in ids:
                    for v in val:
                        if (v==i.id) :
                            i.write({'done': True})

    # def _auto_get_related_partner(self):
    #     if(self.user_id):
    #         self.write({'related_user_id': self.user_id.partner_id})


    def insert_partner(self):
        # slf = self.env['crm.lead'].search([('crm_prj_dev','!=',False)])
        # part = super(Lead, self).create(vals)
        all_lead_data = self.env['crm.lead'].sudo().search([])
        for data in all_lead_data:
            if data.crm_prj_dev:
                if len(data.crm_prj_dev1.ids) > 0:
                    continue
                try:
                    data.crm_prj_dev1 = [(6, 0, [data.crm_prj_dev.id])]
                except Exception as e:
                    raise ValidationError(u'ERROR! \n{}'.format(e))


    def insert_partner2(self):
        # slf = self.env['crm.lead'].search([('crm_prj_dev','!=',False)])
        # part = super(Lead, self).create(vals)
        all_lead_data = self.env['crm.lead'].sudo().search([])
        for data in all_lead_data:
            if data.crm_prj_arc:
                if len(data.crm_prj_arc1.ids) > 0:
                    continue
                try:
                    data.crm_prj_arc1 = [(6, 0, [data.crm_prj_arc.id])]
                except Exception as e:
                    raise ValidationError(u'ERROR! \n{}'.format(e))

    def insert_partner3(self):
        # slf = self.env['crm.lead'].search([('crm_prj_dev','!=',False)])
        # part = super(Lead, self).create(vals)
        all_lead_data = self.env['crm.lead'].sudo().search([])
        for data in all_lead_data:
            if data.crm_prj_cseng:
                if len(data.crm_prj_cseng1.ids) > 0:
                    continue
                try:
                    data.crm_prj_cseng1 = [(6, 0, [data.crm_prj_cseng.id])]
                except Exception as e:
                    raise ValidationError(u'ERROR! \n{}'.format(e))

    def insert_partner4(self):
        # slf = self.env['crm.lead'].search([('crm_prj_dev','!=',False)])
        # part = super(Lead, self).create(vals)
        all_lead_data = self.env['crm.lead'].sudo().search([])
        for data in all_lead_data:

            if data.crm_prj_qs:
                if len(data.crm_prj_qs1.ids) > 0:
                    continue
                try:
                    data.crm_prj_qs1 = [(6, 0, [data.crm_prj_qs.id])]
                except Exception as e:
                    raise ValidationError(u'ERROR! \n{}'.format(e))

    @api.onchange('customer_type', 'delivery_zone')
    def onchange_customer_and_delivery(self):
        self.ensure_one()
        for line in self.crm_products:
            line.product_on_change()

    @api.onchange('priority')
    def get_probability_by_star(self):
        for rec in self:
            rec.cst_probability = (int(rec.priority) / 4 * 100)

    @api.onchange('crm_panel_m3')
    def calculate_panel_cost(self):
        price_to_use = 0.0
        default_pricing = self.env['ir.config_parameter'].\
            sudo().get_param('panelm3price')
        default_global_pricing = self.env['panel.pricing.policy'].search([
            ('product_id', '=', False),
            ('delivery_zone', '=', False)
        ], limit=1)
        if default_global_pricing:
            price_to_use = float(default_global_pricing.price)
        elif default_pricing:
            price_to_use = float(default_pricing)
        else:
            price_to_use = 0.0
        for rec in self:
            if rec.crm_panel_m3 and price_to_use:
                rec.crm_ttl_panel_value = rec.crm_panel_m3 * price_to_use
            else:
                rec.crm_ttl_panel_value = 0.0

    @api.model
    def create(self, vals):
        self.pown_sales_check(vals, True)
        vals = self.set_project_values_on_status(vals)
        print("XXXXXXXXXXXX ",vals)
        # if vals.get('crm_project_id', '') == '':
        #     vals['crm_project_id'] = self.env['ir.sequence'].sudo().next_by_code('crm.lead.prj_sequence') or ''
        result = super(Lead, self).create(vals)
        self.pown_assignment_notification(vals, result.id)
        if vals.get('crm_prj_status', False):
            self._rebuild_pls_frequency_table_threshold()
        return result

    def write(self, vals):
        vals = self.move_tenderer_if_any(vals)
        vals = self.set_project_values_on_status(vals)
        self.pown_sales_check(vals)
        # if not self.env.user.has_group('sales_team.group_sale_manager'):
        #     if not self.get_permission_to_adjust(self.env.uid):
        #         raise UserError('You cannot modify this project. You must be the Project Owner, Project Owner(Sales) or Project Owner(Marketing) to modify.')
        pre_write_data = False
        if 'stage_id' in vals:
            pre_write_data = {'new_stage' : self.env['crm.stage'].sudo().browse(vals['stage_id']).name, 'old_stage' : self.stage_id.name}
        rslt = super(Lead, self).write(vals)
        # if pre_write_data:
        #     if 'new_stage' in pre_write_data:
        #         self.notify_stage_change_to_hos(pre_write_data)
        self.pown_assignment_notification(vals)
        if vals.get('crm_prj_status', False):
            self._rebuild_pls_frequency_table_threshold()
        return rslt

    def name_get(self):
        rslt = []
        for rec in self:
            name = textwrap.shorten(rec.name, width=10, placeholder="...")
            # name = textwrap.wrap(rec.name, 7, break_long_words=False)

            if rec.company_id:
                crm_name = '%s' % (rec.name)
                #crm_name += str(name)
                rslt.append((rec.id, crm_name))
            else:
                rslt.append((rec.id, name))
        return rslt

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search(['|',
                                ('crm_project_id', operator, name),
                                ('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    def set_project_values_on_status(self, values):
        prj_sts = values.get('crm_prj_status', False)
        if prj_sts:
            if prj_sts == 'lost':
                values['probability'] = 0
                values['active'] = False
            if prj_sts == 'won':
                stage_id = self._stage_find(domain=[('is_won', '=', True)])
                values['stage_id'] = stage_id.id
                values['probability'] = 100
        return values

    def pown_sales_check(self, vals, create_mode=False):
        if create_mode:
            if 'crm_prj_own_sales' in vals:
                    if 'crm_prj_own_mark' not in vals:
                        raise UserError('Project Owner (Marketing) cannot be empty if Project Owner (Sales) is set')
        else:
            current_psal = False
            current_pmar = False
            if 'crm_prj_own_sales' in vals:
                current_psal = vals['crm_prj_own_sales']
            elif not current_psal:
                current_psal = self.crm_prj_own_sales

            if current_psal:
                current_pmar = self.crm_prj_own_mark
                if 'crm_prj_own_mark' in vals:
                    current_pmar = vals['crm_prj_own_mark']
                if not current_pmar:
                    raise UserError('Project Owner (Marketing) cannot be empty if Project Owner (Sales) is set')

    def move_tenderer_if_any(self, vals):
        tenderers = vals.get('crm_tenderer', False)
        contractors = vals.get('crm_cntrctrs', [])
        complete_ignore = True
        if tenderers:
            ignore_first = True
            list_of_id_to_maintain = []
            for tender in tenderers:
                if ignore_first:
                    list_of_id_to_maintain = tender[2]
                    ignore_first = False
                else:
                    if tender[0] == 1:
                        val_dict = tender[2]
                        if 'selection_f' in val_dict:
                            if val_dict['selection_f'] == True:
                                contractors.append((4, tender[1]))
                                list_of_id_to_maintain.remove(tender[1])
                                complete_ignore = False
            if not complete_ignore:
                vals['crm_tenderer'] = [(6, False, list_of_id_to_maintain)]
                vals['crm_cntrctrs'] = contractors

        return vals

    def pown_assignment_notification(self, vals, create_id = False):
        self_id = self.env.uid
        lop_name = False
        lop_id = False
        if 'name' in vals:
            lop_name = vals['name']
        else:
            lop_name = self.name
        if 'id' in vals:
            lop_id = vals['id']
        else:
            lop_id = self.id
        if 'user_id' in vals:
            if vals['user_id'] != self_id and vals['user_id'] != False:
                self.notify_project_owner_assignment(lop_name, 'Project Owner', vals['user_id'], self_id, create_id, True)

        cu_partner = self.env['res.users'].sudo().search([('id','=',self_id)], limit=1)
        if cu_partner:
            cu_partner = cu_partner.partner_id.id

        if 'gsm_assign_to' in vals:
            if cu_partner:
                if vals['gsm_assign_to'] != cu_partner and vals['gsm_assign_to'] != False:
                    self.notify_gsm_assignment_to(lop_name,lop_id, 'GSM Assign To', vals['gsm_assign_to'], self_id, create_id )
            else:
                if vals['gsm_assign_to'] != False:
                    self.notify_gsm_assignment_to(lop_name,lop_id, 'GSM Assign To', vals['gsm_assign_to'], self_id, create_id )


        if 'crm_prj_own_sales' in vals:
            if cu_partner:
                if vals['crm_prj_own_sales'] != cu_partner and vals['crm_prj_own_sales'] != False:
                    self.notify_project_owner_assignment(lop_name, 'Project Owner (Sales)', vals['crm_prj_own_sales'], self_id, create_id )
            else:
                if vals['crm_prj_own_sales'] != False:
                    self.notify_project_owner_assignment(lop_name, 'Project Owner (Sales)', vals['crm_prj_own_sales'], self_id, create_id )

        if 'crm_prj_own_mark' in vals:
            if cu_partner:
                if vals['crm_prj_own_mark'] != cu_partner and vals['crm_prj_own_mark'] != False:
                    self.notify_project_owner_assignment(lop_name, 'Project Owner (Marketing)', vals['crm_prj_own_mark'],self_id, create_id )
            else:
                if vals['crm_prj_own_mark'] != False:
                    self.notify_project_owner_assignment(lop_name, 'Project Owner (Marketing)', vals['crm_prj_own_mark'],self_id, create_id )

    def notify_gsm_assignment_to(self, lop_name,lop_id, title, id_to_send, sender_id, create_id, is_user_id = False):
        email_obj = False
        email_template_name = 'emt_gsm_assign_email'
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

        message = "You were assigned a leads by GSM - %s" % (lop_name)

        if email_obj:
            self.send_email(email_obj['email_list'], message, email_template_name, email_obj['contexts'], create_id)


    def notify_project_owner_assignment(self, lop_name, title, id_to_send, sender_id, create_id, is_user_id = False):
        email_obj = False
        email_template_name = 'emt_set_as_prown_email'
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

        message = "Project %s has been assigned to you as a %s" % (lop_name, title)

        if email_obj:
            self.send_email(email_obj['email_list'], message, email_template_name, email_obj['contexts'], create_id)

    def unlink(self):
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            if not self.get_permission_to_adjust(self.env.uid):
                raise UserError('You cannot delete this project. You must be the Project Owner, Project Owner(Sales) or Project Owner(Marketing) to delete.')
        return super(Lead, self).unlink()

    def notify_stage_change_to_hos(self, stage_changes_data):
        email_list = []
        email_template_name = 'emt_hos_stage_change_notf_email'
        hoses = self.env['res.users'].sudo().search([('groups_id','ilike','Head of Sales Group')])
        message = "Project %s stage has changed from %s to %s" % (self.name,stage_changes_data['old_stage'],stage_changes_data['new_stage'])
        for hos in hoses:
            email_list.append(hos.email)
        if len(email_list) > 0:
            self.send_email(email_list, message, email_template_name, {'past_stage' : stage_changes_data['old_stage']})

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
        template_id = self.env['ir.model.data'].sudo().get_object_reference('starken-crm', email_template_name)[1]
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

    def get_permission_to_adjust(self, check_id):
        # If no project manager set, allow to proceed.
        if not self.user_id and not self.crm_prj_own_mark and not self.crm_prj_own_sales:
            return True

        # If not belong to any one of this field. Return as not allowed.
        # Check if user is the project manager
        if self.user_id:
            if self.user_id.id == check_id:
                return True
        # Check if user is the project manager marketing
        if self.crm_prj_own_mark:
            if self.is_user_linked_partner_id_match(check_id, self.crm_prj_own_mark.id):
                return True
        # Check if user is the project manager sales
        if self.crm_prj_own_sales:
            if self.is_user_linked_partner_id_match(check_id, self.crm_prj_own_sales.id):
                return True

        return False

    def is_user_linked_partner_id_match(self, user_id, partner_id):
        c_user = self.env['res.users'].sudo().search([('id','=',user_id)], limit=1)

        if c_user:
            if c_user.partner_id.id == partner_id:
                return True

        return False

    def action_set_won(self):
        for lead in self:
            lead.write({'crm_prj_status': 'won'})
        return True

    def action_set_lost(self, **additional_values):
        result = self.write({'crm_prj_status': 'lost', **additional_values})
        return result

    def marked_to_be_moved_as_contractor(self):
        return True

    # def action_sale_quotations_new(self):
    #     if not self.partner_id:
    #         return self.env.ref("sale_crm.crm_quotation_partner_action").read()[0]
    #     else:
    #         return self.action_new_quotation()

    def action_new_quotation_123(self):
        action = self.env.ref("sale_crm.sale_action_quotations_new").read()[0]
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_team_id': self.team_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': self.tag_ids.ids,
            'default_crm_products': self.crm_products.crm_prdct.name
        }
        return action
