from re import template
from odoo import api, fields, models
from datetime import date

class Lead2Survey(models.TransientModel):

    _name = 'crm.survey'
    _inherit = 'survey.user_input'
    _description = 'Generate a new survey'

    def _get_developer_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_dev1)>0:
            for v in val.crm_prj_dev1:
                value.append(v.id)

        return [('id', 'in', value)]

    def _get_arc_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_arc1)>0:
            for v in val.crm_prj_arc1:
                value.append(v.id)

        return [('id', 'in', value)]

    def _get_dist_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_prj_distributor)>0:
            for v in val.crm_prj_distributor:
                value.append(v.id)
        
        return [('id', 'in', value)]

    def _get_contractors_from_many2many(self):
        val = self.env['crm.lead'].browse(self._context.get('active_ids'))
        value = []
        if len(val.crm_cntrctrs)>0:
            for v in val.crm_cntrctrs:
                value.append(v.id)

        return [('id', 'in', value)]

    total = fields.Integer('Total Customer')
    survey_id = fields.Many2one('survey.survey', string='Survey', required=False)
    cust_type = fields.Selection([
            ('developer','Developer'),
            ('architect', 'Architect'),
            ('contractor', 'Contractor'),
            ('distributor', 'Distributor'),
        ], string="Customer type")
    survey_type = fields.Many2one('survey.survey', string="Survey type")
    crm_prj_devs = fields.Many2many('res.partner', 'crm_leads_crm_survey_devs', 'crm_id', 'partner_id', string='Developer Listed', domain=_get_developer_from_many2many)
    crm_prj_arcs = fields.Many2many('res.partner', 'crm_leads_crm_survey_arcs', 'crm_id', 'partner_id', string='Architect Listed', domain=_get_arc_from_many2many)
    crm_cntrctrs = fields.Many2many('res.partner', 'crm_leads_crm_survey_cntrctrs', 'crm_id', 'partner_id', string='Contractor Listed', domain=_get_contractors_from_many2many)
    crm_prj_distributors = fields.Many2many('res.partner', 'crm_leads_crm_survey_distributors', 'crm_id', 'partner_id',string='Distributor', domain=_get_dist_from_many2many)

    @api.onchange('crm_prj_devs','crm_prj_arcs','crm_cntrctrs','crm_prj_distributors')
    def set_total(self):
        count = 0
        if self.crm_prj_devs:
            count += len(self.crm_prj_devs)

        if(self.crm_prj_arcs):
            count += len(self.crm_prj_arcs)

        if(self.crm_cntrctrs):
            count += len(self.crm_cntrctrs)

        if(self.crm_prj_distributors):
            count += len(self.crm_prj_distributors)

        self.total = count

    def send_survey(self):
      template_id = self.env.ref('starken-crm.mail_template_user_input_invite').id
      template = self.env['mail.template'].browse(template_id)

      email_list = []

      if(self.crm_prj_devs):
        for dev in self.crm_prj_devs:
          email_list.append(dev.email)

      if(self.crm_prj_arcs):
        for arc in self.crm_prj_arcs:
          email_list.append(arc.email)

      if(self.crm_cntrctrs):
        for cnt in self.crm_cntrctrs:
          email_list.append(cnt.email)

      if(self.crm_prj_distributors):
        for dist in self.crm_prj_distributors:
          email_list.append(dist.email)
			
      for el in email_list:
        if el:
          template.email_to = el
          
      if len(email_list) > 0:
        template.send_mail(self.id, force_send=True)

    def print_report(self):
      today = date.today()
      t = today.strftime("%d/%m/%Y")
      data = {
            'id': self.id,
            'model': self._name,
            'form': {
                'create_date': t,
                'dev_count': len(self.crm_prj_devs),
                'arc_count': len(self.crm_prj_arcs),
                'cntrctrs_count': len(self.crm_cntrctrs),
                'dist_count': len(self.crm_prj_distributors),
                'total': self.total,
                'survey_type': self.survey_type.title,
            },
        }
      return self.env.ref('project_crm_chg.report_survey_letter').report_action(self, data=data)
