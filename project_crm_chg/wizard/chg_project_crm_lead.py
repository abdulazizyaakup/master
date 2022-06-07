# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Message', required=True,readonly=True)

    # @api.multi
    def action_ok(self):
        """ close wizard"""
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _(' Project'),
        #     'view_type': 'form',
        #     'view_mode': 'tree, form',
        #     'res_model': 'project.crm',
        #     'view_id': False,
        #     'views': [(self.env.ref('project_crm_chg.crm_case_tree_view_leads_after_wizard').id, 'tree')],
        #     'context': {},
        #     'domain': domain,
        #     'target': 'new2',
        # }
        return {'type': 'ir.actions.act_window_close'}


class CrmAssignTo(models.TransientModel):

    _name = 'crm.assign'
    _description = 'Assign Sub-project to respective salesperson'

    def _default_lead_id(self):
        return self.env['crm.lead'].browse(self._context.get('active_ids'))
        # return lead.project_id

    def _default_opp_name(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.name

    name = fields.Char('Opportunity',default=_default_opp_name)
    lead_id = fields.Many2one('crm.lead', string='Lead', default=_default_lead_id)
    # project_id = fields.Many2one('project.crm', string='Project', default=_default_project_id)
    user_id = fields.Many2one('res.users', string="Salesperson",index=True, tracking=True)
    bu_responsible_id = fields.Many2one('res.users', string="Responsible BU",index=True, tracking=True, default=lambda self:self.env.user.id)

    def writelead(self):
        res = self.lead_id
        res.write({'bu_responsible_id': self.bu_responsible_id.id,
                   'user_id': self.user_id.id})

        return {'type': 'ir.actions.act_window_close'}


class Project2LeadBusinessUnit(models.TransientModel):

    _name = 'crm.project2lead.businessunit'
    _description = 'Generate and assign new lead from project main lead'
    # _inherit = 'crm.lead'

    def _default_project(self):
        return self.env['project.crm'].browse(self._context.get('active_ids'))

    def _default_opportunity_name(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.name

    def _default_opportunity_value(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.project_value

    def _default_opportunity_project_id(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.project_value

    def _default_opportunity_start_date(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.start_date

    def _default_opportunity_end_date(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.end_date

    def _default_opportunity_town(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.town

    def _default_opportunity_street(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.street

    def _default_opportunity_street2(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.street2

    def _default_opportunity_city(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.city

    def _default_opportunity_zip(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.zip

    def _default_opportunity_state(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.state_id.id

    def _default_opportunity_state_name(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.state_id.name

    def _default_opportunity_country(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.country_id.id

    def _default_opportunity_country_name(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.country_id.name

    def _default_opportunity_user_id(self):
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.id


###################################

    def _default_opportunity_bci_region(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.bci_region

    def _default_opportunity_project_owner_type(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.project_owner_type.id

    def _default_opportunity_start_date(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.start_date

    def _default_opportunity_end_date(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.end_date

    def _default_opportunity_project_category1(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.project_category1.id

    def _default_opportunity_project_remarks(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.project_remarks

    def _default_opportunity_element_info(self):
        val = self.env['project.crm'].browse(self._context.get('active_ids'))
        return val.element_info




###################################

    def _default_opportunity_user_partner(self):
        context = self._context
        current_uid = context.get('uid')
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.partner_id.id


    name = fields.Char('Opportunity', default=_default_opportunity_name)
    project_value = fields.Char('Value', default=_default_opportunity_value)
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    team_id = fields.Many2one('crm.team', 'Sales Team', index=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    project_id = fields.Many2one('project.crm', string='Project', default=_default_project)
    bu_responsible_id = fields.Many2many('res.users', string="Project Owner",index=True, tracking=True)
    bu_id = fields.Many2many('res.company', string="Business Unit",index=True, tracking=True)

    def createlead(self):
        user_id = self.bu_responsible_id.id
        related_user = self._default_opportunity_user_partner()
        name = self.name
        project_value = self.project_value
        project_id = self.project_id
        start_date = self._default_opportunity_start_date()
        end_date = self._default_opportunity_end_date()
        town = self._default_opportunity_town()
        street = self._default_opportunity_street()
        street2 = self._default_opportunity_street2() or ''
        city = self._default_opportunity_city() or ''
        state = self._default_opportunity_state() or ''
        state_name = self._default_opportunity_state_name() or ''
        zip = self._default_opportunity_zip() or ''
        country_id = self._default_opportunity_country() or ''
        country_name = self._default_opportunity_country_name() or '' 
        bu_responsible_id = self.bu_responsible_id
        region = self._default_opportunity_bci_region() or ''
        owner_type = self._default_opportunity_project_owner_type() or ''
        project_category1 = self._default_opportunity_project_category1() or ''
        project_remarks = self._default_opportunity_project_remarks() or ''
        project_element = self._default_opportunity_element_info() or ''
        
        for bu in bu_responsible_id:
            self.env['crm.lead'].create({
                'user_id': user_id,
                'name': name,
                'crm_title': name,
                'crm_prj_value': project_value,
                'user_id': False,
                'crm_startdate': start_date,
                'crm_enddate': end_date,
                'company_id': bu.company_id.id or '',
                'crm_prj_town': town,
                'street': street,
                'street2': street2,
                'city': city,
                'state_id': state or '',
                'zip': zip,
                'country_id': country_id or '',
                'crm_prj_addr': str(street)+" ,"+str(street2)+" ,"+str(city)+" ,"+str(zip)+" ,"+str(state_name)+" ,"+str(country_name),
                'bci_region':region,
                'bci_ownership_type':owner_type,
                'bci_start_date':start_date,
                'bci_end_date':end_date,
                'bci_project_value':project_value,
                'bci_project_category':project_category1,
                'bci_project_remarks':project_remarks,
                'bci_element_info':project_element,
                })

        return {'type': 'ir.actions.act_window_close'}


class Project2LeadBusinessUnit2(models.TransientModel):

    _name = 'crm.project2lead.businessunit2'
    _description = 'Generate and assign new lead from project main lead'

    def _default_project(self):
        return self.env['master.project'].browse(self._context.get('active_ids')).id

    def _default_project_all_values(self):
        return self.env['master.project'].browse(self._context.get('active_ids'))

    def _default_opportunity_name(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.name

    def _default_opportunity_gsm_number(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.project_code

    def _default_opportunity_value(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.project_value

    def _default_opportunity_project_id(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.project_value

    def _default_opportunity_start_date(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.start_date

    def _default_opportunity_end_date(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.end_date

    def _default_opportunity_town(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.town

    def _default_bci_id(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.bci_project_code

    def _default_opportunity_street(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.street

    def _default_opportunity_street2(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.street2

    def _default_opportunity_city(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.city

    def _default_opportunity_zip(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.zip

    def _default_opportunity_state(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.state_id.id

    def _default_opportunity_state_name(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.state_id.name

    def _default_opportunity_country(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.country_id.id

    def _default_opportunity_country_name(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.country_id.name

    def _default_opportunity_user_id(self):
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.id

    def _default_opportunity_user_partner(self):
        context = self._context
        current_uid = context.get('uid')
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.partner_id.id


    name = fields.Char('Opportunity', default=_default_opportunity_name)
    project_value = fields.Char('Value', default=_default_opportunity_value)
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    team_id = fields.Many2one('crm.team', 'Sales Team', index=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    project_id = fields.Many2one('master.project', string='Project', default=_default_project)
    bu_responsible_id = fields.Many2many('res.users', string="Responsible BU",index=True, tracking=True)
    bu_id = fields.Many2many('res.company', string="Business Unit",index=True, tracking=True)

    def createlead2(self):
        user_id = self._default_opportunity_user_id()
        related_user = self._default_opportunity_user_partner()
        name = self.name
        project_value = self.project_value
        project_id = self.project_id
        start_date = self._default_opportunity_start_date()
        end_date = self._default_opportunity_end_date()
        town = self._default_opportunity_town()
        street = self._default_opportunity_street()
        street2 = self._default_opportunity_street2() or ''
        city = self._default_opportunity_city() or ''
        state = self._default_opportunity_state() or ''
        state_name = self._default_opportunity_state_name() or ''
        zip = self._default_opportunity_zip() or ''
        country_id = self._default_opportunity_country() or ''
        country_name = self._default_opportunity_country_name() or '' 
        bu_responsible_id = self.bu_responsible_id
        gsm_id = self._default_opportunity_gsm_number() or ''
        bci_id = self._default_bci_id() or ''

        leads = self.env['crm.lead'].search([])

        existing = []
        for l in leads:
            for bu in self.bu_id:
                if(l.crm_bci_id):
                    if(l.company_id.id == bu.id):
                        existing.append(l.crm_bci_id)

        # print("XXXXXXXXXXXX ", existing)
        
        # for a in self.bu_id:
        #     print("XXXXXXXXXXXX2 ", a.id)    

        if(bci_id in existing):
            # print(bci_id,"  xxxxx  ", existing)
            message_id = self.env['message.wizard'].create({'message': _("Project already exist in you company's CRM!")})
            return {
                'name': _('Exist!'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': message_id.id,
                'target': 'new'
            }

        else:       
            for bu in self.bu_id:
                self.env['crm.lead'].sudo().create({
                    'sub_project_code': gsm_id,
                    'master_id': self._default_project(),
                    'name': name,
                    'crm_title': name,
                    'company_id': bu.id,
                    'crm_prj_value': project_value,
                    'crm_startdate': start_date,
                    'crm_enddate': end_date,
                    'crm_prj_town': town,
                    'street': street,
                    'street2': street2,
                    'city': city,
                    'state_id': state or '',
                    'zip': zip,
                    'country_id': country_id or '',
                    'crm_prj_addr': str(street)+" ,"+str(street2)+" ,"+str(city)+" ,"+str(zip)+" ,"+str(state_name)+" ,"+str(country_name),
                    'bci_region': self._default_project_all_values().bci_region,
                    'bci_ownership_type': self._default_project_all_values().project_owner_type.id,
                    'bci_project_category': self._default_project_all_values().project_category1.id,
                    'bci_project_stage': self._default_project_all_values().project_stage_id.id,
                    'bci_project_value': self._default_project_all_values().project_value,
                    'bci_start_date': self._default_project_all_values().start_date,
                    'bci_end_date': self._default_project_all_values().end_date,
                    'bci_project_remarks': self._default_project_all_values().project_remarks,
                    'bci_element_info': self._default_project_all_values().element_info,
                    'crm_prj_dev1':[(6,0, self._default_project_all_values().project_developer1.ids)],
                    'crm_prj_arc1':[(6,0, self._default_project_all_values().project_architect1.ids)],
                    'crm_prj_cseng1':[(6,0, self._default_project_all_values().consulting_engineer1.ids)],
                    'crm_prj_qs1':[(6,0, self._default_project_all_values().project_quantity_surveyor1.ids)],
                    'crm_cntrctrs':[(6,0, self._default_project_all_values().project_main_contractor1.ids),(6,0, self._default_project_all_values().project_main_contractor2.ids),(6,0, self._default_project_all_values().contractor1.ids),(6,0, self._default_project_all_values().turnkey_contractor1.ids)],
                    'crm_sbcns_aplctrs':[(6,0, self._default_project_all_values().project_sub_contractor1.ids)],
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
        return {'type': 'ir.actions.act_window_close'}

class CheckExistingLeads(models.TransientModel):

    _name = 'crm.check.lead'
    _description = 'Check and listed existing lead based on keyword'

    def _default_project_name(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        return val.project_keywords

    def check(self):
        keyword = self._default_project_name()
        leads = self.env['crm.lead'].search([])

        key = keyword.split()
        new_key = []
        project_title = []
        
        for ky in key:
            if len(ky) > 3:
                new_key.append(ky)

        for l in leads:
            if(l.crm_title):
                project_title.append(l.crm_title)
        for s in project_title:
            for k in new_key:
                matched = [k for k in s if s in k]

        #         if matched:
        
                if matched:
                    print(matched)
                    # print("OUTPUT ::: ", k ," IS MATCHED IN ", s.crm_title, " ID ", s.id)

        

    #     return {'type': 'ir.actions.act_window_close'}