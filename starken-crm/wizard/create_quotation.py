# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Lead2Quotation(models.TransientModel):

    _name = 'crm.quotation'
    _description = 'Generate a new quotation'

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

    def _default_opportunity_user_partner(self):
        context = self._context
        current_uid = context.get('uid')
        val = self.env['res.users'].browse(self._context.get('uid'))
        return val.partner_id.id

    def _default_get_all(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val

    def _get_developer_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_dev1)>0:
            for v in val.crm_prj_dev1:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_arc_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_arc1)>0:
            for v in val.crm_prj_arc1:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_cseng_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_cseng1)>0:
            for v in val.crm_prj_cseng1:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_epicor_c_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_trdng_hses)>0:
            for v in val.crm_trdng_hses:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_dist_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_distributor)>0:
            for v in val.crm_prj_distributor:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_qs_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_qs1)>0:
            for v in val.crm_prj_qs1:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_tenderer_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_tenderer)>0:
            for v in val.crm_tenderer:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_contractors_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_cntrctrs)>0:
            for v in val.crm_cntrctrs:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_sbcns_aplctrs_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_sbcns_aplctrs)>0:
            for v in val.crm_sbcns_aplctrs:
                value.append(v.id)
                print("XXXX ",value)

        return [('id', 'in', value)]

    def _get_default_line(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.crm_products

    def _get_allowed_company(self):
        val = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        value = []
        for v in val:
            value.append(v.id)
        
        domain = [('id', 'in', value)]
        return domain

    def _get_default_company(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        return val.company_id.id

    # def get_midah_quotation_product_group(self):
    #     val = self.env['crm.lead'].browse(self._context.get('active_ids'))

    quote_to_type = fields.Selection([('ec','Epicor Customer'),('developer','Developer'),
                                      ('architect','Architect'),
                                      ('c_engineer','Consultant Engineer'),
                                      ('qs','Quantity Surveyor'),
                                      ('tenderer','Tenderer'),
                                      ('contractor','Contractor'),
                                      ('dist','Distributor'),
                                      ('sa','Subcons/Applicators')], default='ec', string="Quote To")
    crm_prj_dev = fields.Many2one('res.partner', string='Developer Listed', domain=_get_developer_from_many2many)
    crm_prj_arc = fields.Many2one('res.partner', string='Architect Listed', domain=_get_arc_from_many2many)
    crm_prj_cseng = fields.Many2one('res.partner', string='Consultant Engineer Listed', domain=_get_cseng_from_many2many)
    crm_prj_qs = fields.Many2one('res.partner', string='Quantity Surveyor (QS) Listed', domain=_get_qs_from_many2many)
    crm_tenderer = fields.Many2one('res.partner', string='Tenderer Listed', domain=_get_tenderer_from_many2many)
    crm_cntrctrs = fields.Many2one('res.partner', string='Contractor Listed', domain=_get_contractors_from_many2many)
    crm_sbcns_aplctrs = fields.Many2one('res.partner', string='Subcons/Applicators Listed', domain=_get_sbcns_aplctrs_from_many2many)
    crm_trdng_hses = fields.Many2one('res.partner',string='Epicor Customer', domain=_get_epicor_c_from_many2many)
    crm_prj_distributor = fields.Many2one('res.partner',string='Distributor', domain=_get_dist_from_many2many)
    crm_quotation_company = fields.Many2one('res.company',string='Company',domain=_get_allowed_company,default=_get_default_company)#domain=[('id','in',[4,5,12,13])])
    midah_quotation_product_group = fields.Selection([('fd','Midah FD'),('td','Midah TD'),
                                      ('accessories','Midah Accessories'),
                                      ('mf','Kempurna MF'),
                                      ('ir','Epic IR')],string="Product Group")
    # crm_prj_distributor = fields.Many2many('res.partner','crm_lead_crm_distributor_ir_attachments_rel', 'crm_id', 'partner_id', string='Distributor', domain="[('partner_type.name', 'ilike', 'Distributor')]")
    """ Newly added """

    def createquotation(self):
        v = self._default_get_all()
        action = self.env.ref("sale_crm.sale_action_quotations_new").read()[0]

        line_value = []
        line = self._get_default_line()
        for l in line:
            line_value.append((0,0,{
                'product_id': l.crm_prdct.id,
                'product_uom_qty': l.crm_prdct_qty,
                'mtr_sq_per_plt':l.mtr_sq_per_plt,
                'no_pcs_per_plt':l.no_pcs_per_plt,
                'plt_per_dlv':l.plt_per_dlv,
                }))

        if(self.crm_prj_dev.id):
                action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_prj_dev.id,
                'default_partner_id': self.crm_prj_dev.id,
                'default_team_id': v.team_id.id or False,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type or False,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }
                
        if(self.crm_prj_arc.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_prj_arc.id,
                'default_partner_id': self.crm_prj_arc.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
                       
            }

        if(self.crm_prj_cseng.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_prj_cseng.id,
                'default_partner_id': self.crm_prj_cseng.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }

        if(self.crm_prj_qs.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_prj_qs.id,
                'default_partner_id': self.crm_prj_qs.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }

        if(self.crm_tenderer.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_tenderer.id,
                'default_partner_id': self.crm_tenderer.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }

        if(self.crm_cntrctrs.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_cntrctrs.id,
                'default_partner_id': self.crm_cntrctrs.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }

        if(self.crm_sbcns_aplctrs.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_sbcns_aplctrs.id,
                'default_partner_id': self.crm_sbcns_aplctrs.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }
        if(self.crm_trdng_hses.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_trdng_hses.id,
                'default_partner_id': self.crm_trdng_hses.id,
                'default_epicor_partner_id': self.crm_trdng_hses.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }
        if(self.crm_prj_distributor.id):
            action['context'] = {
                'search_default_opportunity_id': v.id,
                'default_crm_project_id': v.id,
                'search_default_partner_id': self.crm_prj_distributor.id,
                'default_partner_id': self.crm_prj_distributor.id,
                'default_team_id': v.team_id.id,
                'default_campaign_id': v.campaign_id.id or False,
                'default_medium_id': v.medium_id.id or False,
                'default_origin': v.name,
                'default_source_id': v.source_id.id or False,
                'default_company_id': self.crm_quotation_company.id or v.env.company.id,
                'default_tag_ids': v.tag_ids.ids,
                'default_project_quoted_name': v.name,
                'default_customer_type': v.customer_type,
                'default_delivery_zone': v.delivery_zone.id or False,
                'default_order_line': line_value,
                'default_midah_quotation_product_group': self.midah_quotation_product_group,
            }

        return action
