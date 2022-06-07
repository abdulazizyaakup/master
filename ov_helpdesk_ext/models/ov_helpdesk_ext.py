# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

AVAILABLE_QUALITY = [
    ('0', 'Poor'),
    ('1', 'Normal'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent')
]

class OvHelpdeskExt(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_nric = fields.Char('Nric')
    partner_phone_no = fields.Char(string='Phone No.')
    quality_of_contact = fields.Selection(AVAILABLE_QUALITY, "Quality of Contact", default='0')
    job_id = fields.Many2one('hr.job', "Applied Job")


    @api.multi
    def create_applicant(self):
        """ Create an hr.applicant from the helpdesk ticket inquiry for a job """
        default_stage_id_applicant = self.env['hr.recruitment.stage'].search([('name', '=', 'Inquiry')]).id
        default_stage_id_ticket = self.env['helpdesk.ticket'].search([('name', '=', 'In Progress')]).id
        applicant = False
        for vals in self:
            if vals.partner_name:
                applicant = self.env['hr.applicant'].create({
                    'name': vals.partner_name or '',
                    'partner_name': vals.partner_name or '',
                    'nric': vals.partner_nric or False,
                    'quality_of_contact': vals.quality_of_contact,
                    'stage_id': default_stage_id_applicant,
                    'mobile_no1': vals.partner_phone_no or False})

                #applicant.write({'emp_id': employee.id})
                # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # copied_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (employee.id, self._name)
                # applicant.write({'link_url': copied_url})
                # vals.job_id.message_post(
                #     body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                #     subtype="hr_recruitment.mt_job_applicant_hired")
            else:
                raise UserError(_('You must define an Name for this applicant.'))
        # self.write({'stage_id': default_stage_id_ticket})
        applicant_action = self.env.ref('hr_recruitment.action_hr_job_applications')
        dict_act_window = applicant_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = applicant.id
        return dict_act_window