# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CustomActivityWizard(models.Model):
    _inherit = 'mail.activity'
    _description = 'Wizard for custom activity'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    calendar_event = fields.Many2one('calendar.event','Meeting Details')
    applicant_ids = fields.Many2one('hr.applicant', string="Applicant", default=_default_applicant)
    contact_activity = fields.Selection([
        ('log_an_engagement', 'Log an Engagement'),
        ('wss_reject', 'WSS Reject'),
        ('contact_reject', 'Contact Reject'),
        ('schedule_for_application', 'Schedule for Application'),
        ('banned', 'Banned'),
        ('blacklist', 'Blacklist'),
        ('dead', 'Dead')
        ], "Contact Activity", store=True)
    application_activity = fields.Selection([
        ('wss_reject', 'WSS Reject'),
        ('contact_reject', 'Contact Reject'),
        ('kiv', 'Keep-In-View'),
        ('first_iv', 'Schedule for First Interview'),
        ('banned', 'Banned'),
        ('blacklist', 'Blacklist'),
        ('dead', 'Dead')
        ], "Application Activity", store=True)
    interview_activity = fields.Selection([
        ('wss_reject', 'WSS Reject'),
        ('contact_reject', 'Contact Reject'),
        ('kiv', 'Keep-In-View'),
        ('second_iv', 'Scheduled for Second Interview'),
        ('third_iv', 'Scheduled for Third Interview'),
        ('employment_offer', 'Offer Contract'),
        ('banned', 'Banned'),
        ('blacklist', 'Blacklist'),
        ('dead', 'Dead')
        ], "Interview Activity", store=True)
    contract_activity = fields.Selection([
        ('wss_reject', 'WSS Reject'),
        ('contact_reject', 'Contact Reject'),
        ('kiv', 'Keep-In-View'),
        ('convert_to_employee', 'Convert to Employee'),
        ('banned', 'Banned'),
        ('blacklist', 'Blacklist'),
        ('dead', 'Dead')
        ], "Employment Offer Activity", store=True)
    is_contact = fields.Boolean("In Contact Stage", default=False)
    is_application = fields.Boolean("In Application Stage", default=False)
    is_iv = fields.Boolean("In Interview Stage", default=False)
    is_contract = fields.Boolean("In Contract Stage", default=False)
    type_of_engagement = fields.Selection([
        ('call_attempt', 'Call - Attempt'),
        ('call_follow_up', 'Call - Follow Up'),
        ('call_other', 'Call - Other'),
        ('call_cold', 'Call - Cold'),
        ('call_offer', 'Call - Offer'),
        ('call_received', 'Call Received'),
        ('call_back', 'Call Back'),
        ('whatsapp_cold', 'Whatsapp - Cold'),
        ('whatsapp_follow_up', 'Whatsapp - Follow Up'),
        ('whatsapp_other', 'Whatsapp - Other'),
        ('whatsapp_offer', 'Whatsapp - Offer'),
        ('whatsapp_received', 'Whatsapp Received'),
        ('whatsapp_reply', 'Whatsapp Reply'),
        ('sms_cold', 'SMS - Cold'),
        ('sms_follow_up', 'SMS - Follow Up'),
        ('sms_other', 'SMS - Other'),
        ('sms_offer', 'SMS - Offer'),
        ('sms_received', 'SMS Received'),
        ('sms_reply', 'SMS Reply'),
        ], "Type of Engagement", store=True)
    engagement_status = fields.Selection([
        ('answered', 'Answered'),
        ('not_answered', 'Not Answered'),
        ('no_reply', 'No Reply'),
        ('not_interested', 'Not Interested'),
        ('please_call_back', 'Please Call Back'),
        ('kiv_nsl', 'Keep-In-View - No Suitable Location'),
        ('kiv_nsp', 'Keep-In-View - No Suitable Positions'),
        ('kiv_se', 'Keep-In-View - Salary Expectation'),
        ('schedule_for_application', 'Schedule for Application'),
        ('other', 'Other'),
        ], "Engagement Status", store=True)
    status_call = fields.Selection([
        ('answered', 'Answered'),
        ('not_answered', 'Not Answered'),
        ], "Call Status", store=True)
    status_call_categ = fields.Selection([
        ('not_interested', 'Not Interested'),
        ('please_call_back', 'Please Call Back'),
        ('schedule_for_application', 'Schedule for Application'),
        ('other', 'Other')
        ], "Call Status Category", store=True)
    status_call_categ_other = fields.Text("Other")
    contact_reject_reason = fields.Many2one('contactreject.reason',"Contact Reject Reason")
    wss_reject_reason = fields.Many2one('wssreject.reason',"WSS Reject Reason")
    #substage_reject = fields.Char('Sub Stage')
    comment = fields.Text('Comment')

    @api.multi
    @api.onchange('applicant_ids')
    def get_hr_applicant_model_id(self):
        val = self.env['ir.model'].search([])
        vals = self.env['hr.applicant'].browse(self._context.get('active_ids'))
        if vals:
            for v in val:
                if(v.model == 'hr.applicant'):
                    val1 = v.id
                    val2 = vals
            self.res_model_id = val1
            self.res_id = val2

    @api.multi
    def action_done2(self):
        """ Wrapper without feedback because web button add context as
        parameter, therefore setting context to feedback """
        return self.action_close_dialog()

    def action_feedback2(self, feedback=False):
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))
        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.message_ids[0]

        #self.unlink()
        return message.ids and message.ids[0] or False

    @api.multi
    @api.onchange('applicant_ids')
    def get_applicant_main_stage(self):
        current_stage = self.applicant_ids.stage_id
        if(current_stage.name == 'Contact'):
            self.is_contact = True
        if(current_stage.name == 'Application'):
            self.is_application = True
        if(current_stage.name == 'Interview'):
            self.is_iv = True
        if(current_stage.name == 'Employment Offer'):
            self.is_contract = True

    @api.multi
    @api.onchange('engagement_status')
    def applicant_engagement_status(self):
        vals = self.env['hr.applicant'].browse(self._context.get('active_ids'))
        change_from_wizard = self.engagement_status
        if(change_from_wizard == 'answered'):
                vals.write({'engagement_status': 'answered','record_status':'0'})
        if(change_from_wizard == 'not_answered'):
                vals.write({'engagement_status': 'not_answered','record_status':'0'})
        if(change_from_wizard == 'no_reply'):
                vals.write({'engagement_status': 'no_reply','record_status':'0'})
        if(change_from_wizard == 'not_interested'):
                vals.write({'engagement_status': 'not_interested','record_status':'0'})
        if(change_from_wizard == 'please_call_back'):
                vals.write({'engagement_status': 'please_call_back','record_status':'0'})
        if(change_from_wizard == 'kiv_nsl'):
                vals.write({'engagement_status': 'kiv_nsl','record_status':'0'})
        if(change_from_wizard == 'kiv_nsp'):
                vals.write({'engagement_status': 'kiv_nsp','record_status':'0'})
        if(change_from_wizard == 'kiv_se'):
                vals.write({'engagement_status': 'kiv_se','record_status':'0'})
        if(change_from_wizard == 'schedule_for_application'):
                vals.write({'engagement_status': 'schedule_for_application','record_status':'0'})

    @api.multi
    @api.onchange('contact_activity')
    def change_applicant_contact_sub_stage(self):
        if self.is_contact == True:
            current_stage = self.applicant_ids.contact_stage
            change_from_wizard = self.contact_activity
            vals = self.env['hr.applicant'].browse(self._context.get('active_ids'))
            default_sub_stage_id_contact1 = self.env['contact.substage'].search([('name', '=', 'Nuturing')]).id
            default_sub_stage_id_contact2 = self.env['application.substage'].search([('name', '=', 'New')]).id
            default_sub_stage_id_contact3 = self.env['contact.substage'].search([('name', '=', 'Dead')]).id
            new_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Application')]).id
            banned_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Banned')]).id
            blacklisted_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
            if(change_from_wizard != 'convert_to_application'):
                vals.write({'contact_stage': default_sub_stage_id_contact1})
            if(change_from_wizard == 'convert_to_application'):
                vals.write({'application_stage': default_sub_stage_id_contact2,'stage_id':new_main_stage_id,'application':True,'enquiry':False,})
            if(change_from_wizard == 'banned'):
                vals.write({'stage_id':banned_main_stage_id,'application':False,'enquiry':False,'banned': True})
            if(change_from_wizard == 'blacklist'):
                vals.write({'stage_id':blacklisted_main_stage_id,'application':False,'enquiry':False,'blacklist':True})
            if(change_from_wizard == 'dead'):
                vals.write({'contact_stage': default_sub_stage_id_contact3})

    @api.multi
    @api.onchange('application_activity')
    def change_applicant_application_sub_stage(self):
        if self.is_application == True:
            current_stage = self.applicant_ids.application_stage
            change_from_wizard = self.application_activity
            vals = self.env['hr.applicant'].browse(self._context.get('active_ids'))
            default_sub_stage_id_application1 = self.env['application.substage'].search([('name', '=', 'Wss Reject')]).id
            default_sub_stage_id_application2 = self.env['application.substage'].search([('name', '=', 'Contact Reject')]).id
            default_sub_stage_id_application3 = self.env['application.substage'].search([('name', '=', 'Keep-In-View')]).id
            default_sub_stage_id_application4 = self.env['interview.substage'].search([('name', '=', 'New')]).id
            default_sub_stage_id_application5 = self.env['application.substage'].search([('name', '=', 'Dead')]).id
            new_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Interview')]).id
            banned_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Banned')]).id
            blacklisted_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
            if(change_from_wizard == 'wss_reject'):
                vals.write({'application_stage': default_sub_stage_id_application1})
            if(change_from_wizard == 'contact_reject'):
                vals.write({'application_stage': default_sub_stage_id_application2})
            if(change_from_wizard == 'kiv'):
                vals.write({'application_stage': default_sub_stage_id_application3})
            if(change_from_wizard == 'dead'):
                vals.write({'application_stage': default_sub_stage_id_application5})
            if(change_from_wizard == 'first_iv'):
                vals.write({'interview_stage': default_sub_stage_id_application4,'stage_id':new_main_stage_id,'iv':True,'enquiry':False,'application':False})
            if(change_from_wizard == 'banned'):
                vals.write({'stage_id':banned_main_stage_id,'application':False,'enquiry':False,'banned': True})
            if(change_from_wizard == 'blacklist'):
                vals.write({'stage_id':blacklisted_main_stage_id,'application':False,'enquiry':False,'blacklist':True})

    @api.multi
    @api.onchange('interview_activity')
    def change_applicant_iv_sub_stage(self):
        if self.is_iv == True:
            current_stage = self.applicant_ids.interview_stage
            change_from_wizard = self.interview_activity
            vals = self.env['hr.applicant'].browse(self._context.get('active_ids'))
            default_sub_stage_id_interview1 = self.env['interview.substage'].search([('name', '=', 'Wss Reject')]).id
            default_sub_stage_id_interview2 = self.env['interview.substage'].search([('name', '=', 'Contact Reject')]).id
            default_sub_stage_id_interview3 = self.env['interview.substage'].search([('name', '=', 'Keep-In-View')]).id
            default_sub_stage_id_interview4 = self.env['interview.substage'].search([('name', '=', 'Scheduled for Second Interview')]).id
            default_sub_stage_id_interview5 = self.env['interview.substage'].search([('name', '=', 'Scheduled for Third Interview')]).id
            default_sub_stage_id_interview6 = self.env['interview.substage'].search([('name', '=', 'Dead')]).id
            default_sub_stage_id_emp = self.env['employmentoffer.substage'].search([('name', '=', 'New')]).id
            new_main_stage_id1 = self.env['hr.recruitment.stage'].search([('name', '=', 'Employment Offer')]).id
            banned_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Banned')]).id
            blacklisted_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
            if(change_from_wizard == 'wss_reject'):
                vals.write({'interview_stage': default_sub_stage_id_interview1})
            if(change_from_wizard == 'contact_reject'):
                vals.write({'interview_stage': default_sub_stage_id_interview2})
            if(change_from_wizard == 'kiv'):
                vals.write({'interview_stage': default_sub_stage_id_interview3})
            if(change_from_wizard == 'second_iv'):
                vals.write({'interview_stage': default_sub_stage_id_interview4})
            if(change_from_wizard == 'third_iv'):
                vals.write({'interview_stage': default_sub_stage_id_interview5})
            if(change_from_wizard == 'employment_offer'):
                vals.write({'employment_offer_stage': default_sub_stage_id_emp,'stage_id':new_main_stage_id1,'contract_proposal':True, 'iv':False})
            if(change_from_wizard == 'dead'):
                vals.write({'interview_stage': default_sub_stage_id_interview6})
            if(change_from_wizard == 'banned'):
                vals.write({'stage_id':banned_main_stage_id,'application':False,'enquiry':False,'banned': True})
            if(change_from_wizard == 'blacklist'):
                vals.write({'stage_id':blacklisted_main_stage_id,'application':False,'enquiry':False,'blacklist':True})

    @api.multi
    @api.onchange('contract_activity')
    def change_applicant_contract_sub_stage(self):
        if self.is_contract == True:
            current_stage = self.applicant_ids.employment_offer_stage
            change_from_wizard = self.contract_activity
            vals = self.env['hr.applicant'].browse(self._context.get('active_ids'))
            default_sub_stage_id_contract1 = self.env['employmentoffer.substage'].search([('name', '=', 'WSS Reject')]).id
            default_sub_stage_id_contract2 = self.env['employmentoffer.substage'].search([('name', '=', 'Contact Reject')]).id
            default_sub_stage_id_contract3 = self.env['employmentoffer.substage'].search([('name', '=', 'Keep-In-View')]).id
            default_sub_stage_id_contract4 = self.env['employmentoffer.substage'].search([('name', '=', 'convert_to_employee')]).id
            default_sub_stage_id_contract5 = self.env['employmentoffer.substage'].search([('name', '=', 'Dead')]).id
            new_main_stage_id1 = self.env['hr.recruitment.stage'].search([('name', '=', 'Employee')]).id
            banned_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Banned')]).id
            blacklisted_main_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
            if(change_from_wizard == 'wss_reject'):
                vals.write({'employment_offer_stage': default_sub_stage_id_contract1})
            if(change_from_wizard == 'contact_reject'):
                vals.write({'employment_offer_stage': default_sub_stage_id_contract2})
            if(change_from_wizard == 'kiv'):
                vals.write({'employment_offer_stage': default_sub_stage_id_contract3})
            if(change_from_wizard == 'convert_to_employee'):
                vals.write({'stage_id':new_main_stage_id1,'convert_to_emp':True,'contract_proposal':False})
            if(change_from_wizard == 'dead'):
                vals.write({'employment_offer_stage': default_sub_stage_id_contract5})
            if(change_from_wizard == 'banned'):
                vals.write({'stage_id':banned_main_stage_id,'application':False,'enquiry':False,'banned': True})
            if(change_from_wizard == 'blacklist'):
                vals.write({'stage_id':blacklisted_main_stage_id,'application':False,'enquiry':False,'blacklist':True})

    @api.multi
    def save_activity(self):
        for app in self.applicant_ids:
            print("Hello")
        return {'type': 'ir.actions.act_window_close'}
