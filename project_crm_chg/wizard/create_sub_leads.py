# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Lead2SubLeadBusinessUnit(models.TransientModel):

    _name = 'crm.lead2sublead.businessunit'
    _description = 'Generate and assign new lead from to child unit'
    # _inherit = 'crm.lead'

    def _default_project(self):
        return self.env['crm.lead'].browse(self._context.get('active_ids')).id

    def _default_project_all_values(self):
        return self.env['crm.lead'].browse(self._context.get('active_ids'))

    def _default_opportunity_name(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.name

    def _default_opportunity_value(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.crm_prj_value

    # def _default_opportunity_project_id(self):
    #     val = self.env['crm.lead'].browse(self._context.get('active_ids'))
    #     return val.project_value

    def _default_opportunity_start_date(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.bci_start_date

    def _default_opportunity_end_date(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.bci_end_date

    def _default_opportunity_town(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.crm_prj_town

    def _default_opportunity_street(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.street

    def _default_opportunity_street2(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.street2

    def _default_opportunity_city(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.city

    def _default_opportunity_zip(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.zip

    def _default_opportunity_state(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.state_id.id

    def _default_opportunity_state_name(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.state_id.name

    def _default_opportunity_country(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.country_id.id

    def _default_opportunity_country_name(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.country_id.name

    def _default_opportunity_user_id(self):
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.id

    def _default_gsm(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.sub_project_code

    def _default_bci_id(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.crm_bci_id

    def _default_opportunity_user_partner(self):
        context = self._context
        current_uid = context.get('uid')
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.partner_id.id


    name = fields.Char('Lead', default=_default_opportunity_name)
    project_value = fields.Char('Value', default=_default_opportunity_value)
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    team_id = fields.Many2one('crm.team', 'Sales Team', index=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    sub_project_id = fields.Many2one('crm.lead', string='Project', default=_default_project)
    bu_responsible_id = fields.Many2many('res.users', string="Responsible BU",index=True, tracking=True)
    bu_id = fields.Many2many('res.company', string="Business Unit",index=True, tracking=True,domain="[('id','child_of',4)]")

    # @api.depends('crm_bci_id')

    def createsublead(self):

        # context = self._context
        # current_uid = context.get('uid')
        user_id = self._default_opportunity_user_id()
        related_user = self._default_opportunity_user_partner()
        name = self.name
        project_value = self.project_value
        # project_id = self.project_id
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
        gsm_id = self._default_gsm() or ''
        bci_id = self._default_bci_id() or ''
        # print("XXXX ", user_id,related_user,name)

        # for b in bu_responsible_id:
        for bu in self.bu_id:
            self.env['crm.lead'].sudo().create({
                'sub_master_id': self._default_project(),
                'sub_project_code': gsm_id,
                'crm_bci_id': bci_id,
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
                'bci_region': self._default_project_all_values().bci_region or False,
                'bci_ownership_type': self._default_project_all_values().bci_ownership_type.id or False,
                'bci_project_category': self._default_project_all_values().bci_project_category.id or False,
                'bci_project_stage': self._default_project_all_values().bci_project_stage.id or False,
                # 'bci_project_status': b.project_status.id,
                'bci_project_value': self._default_project_all_values().bci_project_value or False,
                'bci_start_date': self._default_project_all_values().bci_start_date or False,
                'bci_end_date': self._default_project_all_values().bci_end_date or False,
                'bci_project_remarks': self._default_project_all_values().bci_project_remarks or False,
                'bci_element_info': self._default_project_all_values().bci_element_info or False,
                'crm_prj_dev1':[(6,0, self._default_project_all_values().crm_prj_dev1.ids)] or False,
                'crm_prj_arc1':[(6,0, self._default_project_all_values().crm_prj_arc1.ids)] or False,
                'crm_prj_cseng1':[(6,0, self._default_project_all_values().crm_prj_cseng1.ids)] or False,
                'crm_prj_qs1':[(6,0, self._default_project_all_values().crm_prj_qs1.ids)] or False,
                'crm_cntrctrs':[(6,0, self._default_project_all_values().crm_cntrctrs.ids)] or False,
                'crm_sbcns_aplctrs':[(6,0, self._default_project_all_values().crm_sbcns_aplctrs.ids)] or False,
                })

        return {'type': 'ir.actions.act_window_close'}