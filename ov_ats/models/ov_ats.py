# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request
import logging
import json
from urllib.request import urlopen, Request
import random
import string
import uuid
from pushbullet import Pushbullet
import requests
#from pushbullet.pushbullet import PushBullet
logger = logging.getLogger(__name__)



class ApplicantBlacklistDetails(models.Model):
    _name = 'application.blacklist.details'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Applicant Blacklist Details'
    
    # employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    applicant_id = fields.Many2one('hr.applicant', string="ATS Record")
    name = fields.Char("Name")
    blacklist_date = fields.Date("Blacklisted Date")
    blacklist_reason = fields.Text("Reason")


class ApplicantBannedDetails(models.Model):
    _name = 'application.banned.details'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Applicant Banned Details'
    
    # employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    applicant_id = fields.Many2one('hr.applicant', string="ATS Record")
    name = fields.Char("Name")
    banned_date = fields.Date("Banned Date")
    banned_site = fields.Many2many('project.site','project_site_hr_applicant_rel', 'hr_applicant_id', 'project_site_id', string="Working Days Preference")
    banned_reason = fields.Text("Reason")


class ResApplicant(models.Model):
    _name = 'res.applicant'

    is_applicant = fields.Boolean('Is Applicant?')
    is_projectsite = fields.Boolean('Is Project Site')
    name = fields.Char('Name')
    postal_code = fields.Char('Postal Code')
    lat = fields.Char('Latitude')
    lng = fields.Char('Longitude')
    applicant_ids = fields.Many2one('hr.applicant', 'Applicant', ondelete='cascade', index=True)
    applicant_name = fields.Char("Applicant's Name")
    site_ids = fields.Many2one('project.site', 'Project Site', ondelete='cascade', index=True)


    @api.onchange('applicant_ids')
    def _get_applicant_name(self):
        self.applicant_name = self.applicant_ids.full_name or self.applicant_ids.call_application_name or ''
# class OnemapAddress(models.Model):
#     _name = 'onemap.address'
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = 'Onemap Address'

#     postal_code = fields.Char("Postal Code")
#     address = fields.Text("Address")


class ApplicantRaces(models.Model):
    _name = 'applicant.races'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Races'

    name = fields.Char("Race")


class CallPreferredSite(models.Model):
    _name = 'callpref.site'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Preferred Type of Work Site'

    name = fields.Char('Site')

class PreferredLocation(models.Model):
    _name = 'preferred.location'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Preferred Working Location'

    name = fields.Char('Location')
    postalcode = fields.Char('Postal Code')

class ContactStage(models.Model):
    _name = 'contact.substage'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Contact Sub Stages'
    
    name = fields.Char('Stage')

class ApplicationStage(models.Model):
    _name = 'application.substage'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Application Sub Stages'
    
    name = fields.Char('Stage')

class InterviewStage(models.Model):
    _name = 'interview.substage'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Interview Sub Stages'
    
    name = fields.Char('Stage')

class EmploymentOfferStage(models.Model):
    _name = 'employmentoffer.substage'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Employement Offer Sub Stages'
    
    name = fields.Char('Stage')

class UploadedFile(models.Model):
    _name = 'uploaded.file'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Uploaded Files'

    title = fields.Char("Document Title")
    name = fields.Char("Document Name")
    description = fields.Char("Description")
    #filetype = fields.Selection([('ic_work_permit', 'IC / Work Permit'),('driving_license', 'Driving License'),('passport', 'Passport'),('training', 'Training'),('documents', 'Documents'),('others', 'Others')], "Type", store=True)
    filetype = fields.Selection([
        ('application_form','Application Form'),
        ('nric','NRIC'),('work_permit','Work Permit'),
        ('passport','Passport'),
        ('social_visit_pass','Social Visit Pass'),
        ('certificate_of_good_conduct','Certificate of Good Conduct'),
        ('identification_card','Identification Card'),
        ('letter_of_appointment','Letter of Appointment'),
        ('pre_employment_briefing_on_job_functions','Pre-Employment Briefing on Job Functions'),
        ('pre_employment_briefing_on_administration','Pre Employment Briefing On Administration'),
        ('plrd_security_licence','PLRD Security Licence'),
        ('bank_account_particulars_document','Bank Account Particulars Document'),
        ('plrd_screening_document','PLRD Screening Document'),
        ('plrd_training_records_document','PLRD Training Records Document'),
        ('plrd_notification_document','PLRD Notification Document'),
        ('medical_report','Medical Report'),
        ('logistics_issuance_document','Logistics Issuance Document')], "Type", store=True)
    file = fields.Binary("File",attachment=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False)

class EducationalBackground(models.Model):
    _name = 'edu.back'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Educational Background'

    name = fields.Char('School')
    hqa = fields.Char('Highest Qualification Result')
    year = fields.Char('Year')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

class NoLevelResult(models.Model):
    _name = 'nolevel.result'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GCE N/O Level Result'

    name = fields.Char('Subject')
    grade = fields.Char('Grade')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

class ALevelResult(models.Model):
    _name = 'alevel.result'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GCE A Level Result'

    name = fields.Char('Subject')
    grade = fields.Char('Grade')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

class LanguagesSpokenWritten(models.Model):
    _name = 'language.spokenwritten'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Languages'

    name = fields.Char('Language')
    proficiency_spoken = fields.Selection([('poor', 'Poor'),('fair', 'Fair'),('fluent', 'Fluent')], "Spoken", store=True)
    proficiency_written = fields.Selection([('poor', 'Poor'),('fair', 'Fair'),('good', 'Good')], "Written", store=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

class LanguagesDialect(models.Model):
    _name = 'language.dialect'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Dialect'

    name = fields.Char('Dialect')
    proficiency_dialect = fields.Selection([('poor', 'Poor'),('fair', 'Fair'),('fluent', 'Fluent')], "Spoken", store=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)


class CareerHistory(models.Model):
    _name = 'career.history'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Career History'

    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    name = fields.Char('Company Name')
    position_held = fields.Char('Position Held')
    gross_sal = fields.Char('Gross Salary')
    reason_leave = fields.Text('Reason Leaving')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

class FriendRelative(models.Model):
    _name = 'friend.relative'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Friends / Relative working with WSS'

    name = fields.Char('Name')
    relationship = fields.Char('Relationship')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

class NegativeCharacterTraits(models.Model):
    _name = 'negative.character'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Negative Character Traits'

    name = fields.Char('Character')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant")

class CallPreferredTypeWorkSite(models.Model):
    _name = 'call.prefsite'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Call Preferred Type Work Site'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    name = fields.Char('Name')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant",default=_default_applicant)

class PositiveCharacterTraits(models.Model):
    _name = 'positive.character'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Positive Character Traits'

    name = fields.Char('Character')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant")

class DaysAvail(models.Model):
    _name = 'days.avail'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Working Days Preference'

    name = fields.Char('Days')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant")


class ContactRejectReason(models.Model):
    _name = 'contactreject.reason'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Reason for WSS Reject'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    name = fields.Char('Reason')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant",default=_default_applicant)

class WssRejectReason(models.Model):
    _name = 'wssreject.reason'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Reason for WSS Reject'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    name = fields.Char('Reason')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant",default=_default_applicant)

class WssCampaign(models.Model):
    _name = 'wss.campaign'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'WSS Campaign'

    # def _default_applicant(self):
    #     return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    name = fields.Char('Name')
    #applicant_ids = fields.Many2one('hr.applicant', string="Applicant",default=_default_applicant)

class CurrentLastCompany(models.Model):
    _name = 'current.last.company'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Current / Last Company'

    name = fields.Char('Company Name')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant")

class PreferredSiteSuitable(models.Model):
    _name = 'preferredsuitable.site'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Preferred Site Suitable'

    name = fields.Char('Site')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant")

class PreferredSite(models.Model):
    _name = 'preferred.site'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Preferred Type of Projects'

    name = fields.Char('Site')
    applicant_ids = fields.Many2many('hr.applicant', string="Applicant")

class DrivingLicense(models.Model):
    _name = 'driving.license'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Driving License'

    name = fields.Char('License')
    applicant_id = fields.Many2many('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)

AVAILABLE_QUALITY = [
    ('0', 'Poor'),
    ('1', 'Normal'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent')
]

STATUS = [
    ('0', 'Older'),
    ('1', 'New')
]

class Ats(models.Model):
    _inherit = 'hr.applicant'
    _order = "date_last_stage_update desc"

    def _default_contact_stage_id(self):
        val = self.env['contact.substage'].search([('name','=','New')])
        return val.id

    def _default_application_stage_id(self):
        val = self.env['application.substage'].search([('name','=','New')])
        return val.id

    def _default_interview_stage_id(self):
        val = self.env['interview.substage'].search([('name','=','New')])
        return val.id

    def _default_employment_offer_stage_id(self):
        val = self.env['employmentoffer.substage'].search([('name','=','New')])
        return val.id

    def _default_online_ref_no(self,string_length=10):
        """Returns a random string of length string_length."""
        random = str(uuid.uuid4()) # Convert UUID format to a Python string.
        random = random.upper() # Make all characters uppercase.
        random = random.replace("-","") # Remove the UUID '-'.
        return random[0:string_length]

    # def _default_one_map(self):
    #     return self.get_iframe_one_map()
    #########################################
    #lang_ids = fields.One2many('language.spokenwritten', 'applicant_id', string="Language(s)")
    sms_account = fields.Many2one('pushbulletsms.conf','SMS Sender Account')
    whatsapp_account = fields.Many2one('whatsapp.wassenger.conf','Whatsapp Sender Account')
    read_by_ids = fields.Many2many('res.users','res_users_hr_applicant_rel', 'hr_applicant_id', 'res_users_id',  string="Read By", default=lambda self: self.env.user, store=True)
    is_ex_employee = fields.Boolean("Is Ex-Employee?", default=False, help="Ex-Employee")
    resignation_ids = fields.One2many('employee.resignation.details','applicant_id',string="Resignation Records")
    created_by_id = fields.Many2one('res.users', "Created By", track_visibility="onchange", default=lambda self: self.env.uid)
    message_unread =  fields.Boolean("Unread", default=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    record_status = fields.Selection(STATUS, "Record Status",readonly=True)
    sms_track_ids = fields.One2many('pushbullet.sms.track','applicant_id',string="SMS History",track_visibility='onchange')
    whatsapp_track_ids = fields.One2many('whatsapp.wassenger.track','applicant_id',string="Whatsapp History",track_visibility='onchange')
    #days_avail_ids = fields.Many2many('days.avail','days_avail_hr_applicant_rel', 'hr_applicant_id', 'days_avail_id', string="Working Days Preference")
    sms_count = fields.Integer(compute='_get_sms_count', string="Number of SMS")
    initial_mobile_code = fields.Selection([
        ('sg','[SG]'),
        ('my','[MY]'),
        ('ph','[PH]')
        ], "Code", store=True,default='sg')
    initial_mobile_no = fields.Char("Contact No.", size=32)
    name = fields.Char('Prospects',default=lambda obj:obj.env['ir.sequence'].next_by_code('hr.applicant'))
    online_ref_no = fields.Char('Online Ref. No.',default=_default_online_ref_no)
    call_application_name = fields.Char('Prospect Name', required=True)
    call_individual_pwm_grade = fields.Selection([
        ('so', 'Security Officer'),
        ('sso', 'Senior Security Officer'),
        ('ss', 'Security Supervisor'),
        ('sss', 'Senior Security Supervisor'),
        ('cso', 'Chief Security Officer')
        ], "Individual PWM Grade", store=True)
    gender = fields.Selection([
        ('male','Male'),
        ('female','Female')
        ], "Gender", store=True)
    call_gender = fields.Selection([
        ('male','Male'),
        ('female','Female')
        ], "Gender", store=True)
    mobile_no1 = fields.Char("Contact No.", size=12, required=True)
    call_mobile_no1 = fields.Char("Contact No.", size=12)
    call_project_site = fields.Many2one('project.site', "Project Site Name")
    nationality = fields.Selection([
        ('singaporean', 'Singaporean'),
        ('pr', 'Singapore Permanent Resident'),
        ('malaysian', 'Malaysian'),
        ('philipines', 'Phillipines')
        ], "Nationality", store=True)
    call_nationality = fields.Selection([
        ('singaporean', 'Singaporean'),
        ('pr', 'Singapore Permanent Resident'),
        ('malaysian', 'Malaysian'),
        ('philipines', 'Phillipines')
        ], "Nationality", store=True)
    call_races = fields.Many2one("applicant.races", "Race")
    call_age = fields.Char('Age')
    call_postal_code = fields.Char("Postal Code",default='')
    races = fields.Many2one("applicant.races", "Races")
    age = fields.Integer('Age')
    postal_code = fields.Char("Postal Code",default='')
    preferred_location1 = fields.Many2one('preferred.location', "Preferred Location")
    call_preferred_location1 = fields.Many2one('preferred.location', "Preferred Location")
    preferred_emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('permanent_relief', 'Permanent Relief'),
        ('relief', 'Relief'),
        ('package', 'Package')
        ], "Preferred Employement Type", store=True)
    emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('permanent_relief', 'Permanent Relief'),
        ('relief', 'Relief'),
        ('package', 'Package')
        ], "Employement Type", store=True)
    call_preferred_emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('permanent_relief', 'Permanent Relief'),
        ('relief', 'Relief'),
        ('package', 'Package')
        ], "Preferred Employement Type", store=True)
    preferred_type_work_site = fields.Selection([
        ('condominium','Condominium'),
        ('shopping_malls','Shopping Malls'),
        ('industrial_bulding','Industrial Building'),
        ('office_buidling','Office Building'),
        ],"Preferred Type of Work Site", store=True)
    shift_preferences = fields.Selection([
        ('day','Day'),
        ('night','Night'),
        ('either','Either')
        ],"Shift Preferrence", store=True)
    call_shift_preferences = fields.Selection([
        ('day','Day'),
        ('night','Night'),
        ('either','Either')
        ],"Shift Preferrence", store=True)
    security_license = fields.Selection([
        ('yes','Yes'),
        ('no','No'),
        ],"Security Licence", store=True)
    call_security_license = fields.Selection([
        ('yes','Yes'),
        ('no','No'),
        ],"Security Licence", store=True)
    campaign = fields.Many2one('wss.campaign','Source',track_visibility='onchange')
    call_campaign = fields.Many2one('wss.campaign','Source',track_visibility='onchange')
    current_last_company = fields.Many2many('current.last.company',string='Current / Last Company')
    call_current_last_company = fields.Many2many('current.last.company',string='Current / Last Company')
    last_type_work_site = fields.Selection([
        ('condominium','Condominium'),
        ('shopping_malls','Shopping Malls'),
        ('industrial_bulding','Industrial Building'),
        ('office_buidling','Office Building'),
        ],"Type of Last Work Site", store=True)
    call_last_type_work_site = fields.Selection([
        ('condominium','Condominium'),
        ('shopping_malls','Shopping Malls'),
        ('industrial_bulding','Industrial Building'),
        ('office_buidling','Office Building'),
        ],"Type of Last Work Site", store=True)
    applicant_reason_for_leaving = fields.Text('Reason for Leaving')
    comment_current_last_commpany = fields.Text('Comments on Current / Last Company')
    current_last_salary = fields.Float('Current / Last Salary')
    type_of_salary = fields.Selection([(' daily','Day'),('monthly','Month')],"Type of Salary", store=True)
    call_applicant_reason_for_leaving = fields.Text('Reason for Leaving')
    call_comment_current_last_commpany = fields.Text('Comments on Current / Last Company')
    call_current_last_salary = fields.Float('Current / Last Salary')
    call_type_of_salary_last = fields.Selection([(' daily','Day'),('monthly','Month')],"Type of Salary", store=True)
    call_type_of_salary_expected = fields.Selection([(' daily','Day'),('monthly','Month')],"Type of Salary", store=True)
    call_site_latitude = fields.Float(string='Site Latitude', digits=(16, 12), store=True)
    call_site_longitude = fields.Float(string='Site Longitude', digits=(16, 12), store=True)
    call_applicant_latitude = fields.Float(string='Applicant Latitude', digits=(16, 12), store=True)
    call_applicant_longitude = fields.Float(string='Applicant Longitude', digits=(16, 12), store=True)
    call_preferred_type_work_site = fields.Many2many('callpref.site', string="Preferred Type of Work Site")
    uploaded_ids = fields.One2many('uploaded.file', 'applicant_id', string="Files")
    #########################################
    update_from_website = fields.Boolean("Updated From Online Form")
    #Computer Literacy
    m_words = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Words", store=True)
    m_excel = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Excel", store=True)
    m_powerpoint = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Power Point", store=True)
    m_outlook = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Outlook", store=True)
    #For Stage
    applicant_image = fields.Binary('Image', attachment=True)
    enquiry = fields.Boolean("Contact", default=True)
    application = fields.Boolean("Application", default=False)
    iv = fields.Boolean("Interview", default=False)
    contract_proposal = fields.Boolean("Employment Offer", default=False)
    convert_to_emp = fields.Boolean("Converted to Employee", default=False)
    banned = fields.Boolean("Banned", default=False)
    blacklist = fields.Boolean("Blacklist", default=False)
    blacklist_note = fields.Text('Blacklisted Reason')
    blacklist_date = fields.Date(string='Blacklisted Date')
    banned_note = fields.Text('Banned Reason')
    banned_date = fields.Date(string='Banned Date')
    #SubStage for Contact
    pref_name = fields.Char('Preffered Name')
    contact_stage = fields.Many2one('contact.substage','Contact Stage',default=_default_contact_stage_id)
    application_stage = fields.Many2one('application.substage','Application Stage',default=_default_application_stage_id)
    interview_stage = fields.Many2one('interview.substage','Interview Stage',default=_default_interview_stage_id)
    employment_offer_stage = fields.Many2one('employmentoffer.substage','Employment Offer Stage',default=_default_employment_offer_stage_id)
    school_ids = fields.One2many('edu.back', 'applicant_id', string="School")
    alevel_ids = fields.One2many('alevel.result', 'applicant_id', string="GCE 'A' Level Result")
    nolevel_ids = fields.One2many('nolevel.result', 'applicant_id', string="GCE 'N'/'O' Level Result")
    lang_ids = fields.One2many('language.spokenwritten', 'applicant_id', string="Language(s)")
    dialect_ids = fields.One2many('language.dialect', 'applicant_id', string="Dialect")
    careerhistory_ids = fields.One2many('career.history', 'applicant_id', string="Career History")
    iv_assessment_ids = fields.One2many('iv.assessment', 'applicant_id', string="Assessment")
    days_avail_ids = fields.Many2many('days.avail','days_avail_hr_applicant_rel', 'hr_applicant_id', 'days_avail_id', string="Working Days Preference")
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
    #nationalservice_ids = fields.One2many('national.service', 'applicant_id', string="National Service")
    nationalservice = fields.Selection([
        ('saf', 'SAF'),
        ('spf', 'SPF'),
        ('scdf', 'SCDF'),
        ('nil', 'Not Served')
        ], "National Service", store=True)
    ns_reason = fields.Text('Reason Not Served')
    rank = fields.Char('Rank')
    pes_grading = fields.Char('PES Grading')
    enlistment_date = fields.Date(string='Enlistment Date')
    operation_ready_date = fields.Date(string='Operation Ready Date')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)
    #other information

    #Details Information Needed
    appointment_reference = fields.Char("Our Ref.")
    description = fields.Text()
    letter_date = fields.Date(string='Date of Issuance of Letter of Appointment')
    commencement_date = fields.Date(string='Commencement Date')
    partner_name = fields.Char("Partner Name")
    full_name = fields.Char("Full Name")
    salutation = fields.Selection([('mr', 'Mr'),('ms', 'Ms'),('mrs', 'Mrs')], "Salutation", store=True)
    unit_no = fields.Char('Unit No.')
    level_no = fields.Char('Level')
    initial_address = fields.Char('I Address')
    address = fields.Char('Address')
    address_status = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('relative', '*Relative / Friend Place')
        ], "Address Type", store=True)
    country_id = fields.Many2one("res.country", "Nationality")
    nationality = fields.Selection([
        ('singaporean', 'Singaporean'),
        ('pr', 'Singapore PR'),
        ('malaysian', 'Malaysian'),
        ('others', 'Others')
        ], "Nationality", store=True)
    nationality_other = fields.Char('Others')
    country_of_birth = fields.Many2one("res.country", "Country of Birth")
    races = fields.Many2one("applicant.races", "Races")
    religion = fields.Char("Religion")
    postal_code = fields.Char("Postal Code",default='')
    country_image = fields.Binary(readonly=True, related='country_id.image')
    project_site = fields.Many2one('project.site', "Project Site Name")
    preferred_location1 = fields.Many2one('preferred.location', "Preferred Location")
    preferred_location2 = fields.Many2one('preferred.location', "Preferred Location 2")
    preferred_location3 = fields.Many2one('preferred.location', "Preferred Location 3")
    quality_of_contact = fields.Selection(AVAILABLE_QUALITY, "Quality of Contact", default='0')
    nric = fields.Char("NRIC No.")
    mobile_no2 = fields.Char("Mobile No. 2", size=32)
    email = fields.Char("Email Address", size=128)
    # source_ids = fields.Many2one('job.source','Source')
    post_source = fields.Selection([
        ('newspaper_advertisement','Newspaper Advertisement'),
        ('word_of_mouth','Word of Mouth'),
        ('website','Website'),
        ('friends_relative','Friend / Relatives'),
        ('osp','One Stop Security Platform'),
        ('others','Others')
        ], "How do you learn of this post?",store=True)
    post_other = fields.Text('Other')
    wss_applied = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Have you ever applied for employment before with William Security Services / William Secure Solution?",store=True)
    wss_applied_other = fields.Text('Please state when and where')
    gender = fields.Selection([
        ('male','Male'),
        ('female','Female')
        ], "Gender", store=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
        ], "Marital Status", store=True)
    driving_license_ids = fields.Many2many('driving.license','driving_license_hr_applicant_rel', 'hr_applicant_id', 'driving_license_id',string='Driving License')
    # driving_license = fields.Selection([
    #     ('class3','Class 3'),
    #     ('class2','Class 2 / 2A / 2B'),
    #     ('no','Nil'),
    #     ('others','Others')
    #     ], "License", store=True)
    # driving_license_other = fields.Char('Others')
    smoke = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Do you smoke?", store=True)
    friend_relative = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Do you have any friends / relatives working with William Security Services?", store=True)
    relative_ids = fields.One2many('friend.relative', 'applicant_id', string="Friends / Relatives")
    six_shift = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Are you able to work 6 shifts per week?", store=True)
    six_shift_no = fields.Char('Please state the number of shifts you can work per week')
    working_weekend = fields.Selection([
        ('yes','Yes'),
        ('no','No'),
        ('one_per_week','I can work at least 1 per week')
        ], "Are you able to work on weekends?", store=True)
    #Emergency Contact
    emergency_name = fields.Char('Name')
    emergency_relation = fields.Char('Relationship')
    emergency_mobile_no = fields.Char('Mobile')
    emergency_phone_no = fields.Char('Phone')
    emergency_address = fields.Text('Address')
    #Educational
    # school1 = fields.Char('School')
    parent_id = fields.Many2one('hr.employee', 'Manager')
    created_by = fields.Many2one('res.users','Created By', default=lambda self: self.env.user)
    interviewer = fields.Many2one('res.users','Interviewer', default=lambda self: self.env.user)
    owner = fields.Many2one('res.users','Owner', default=lambda self: self.env.user)
    recruiter = fields.Many2one('res.users','Recruiter', default=lambda self: self.env.user)
    recruiter_signature = fields.Binary(string="Signature", store=True)
    job_id = fields.Many2one('hr.job', "Applied Job",required=True)
    day_of_source = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
        ], "Day of Source", store=True)
    date_of_source = fields.Date(string='Date of Source',default=lambda self : fields.Date.today())
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer('Age')
    age_range = fields.Selection([
        ('18-19','18-19'),
        ('20-29','20-29'),
        ('30-39','30-39'),
        ('40-49','40-49'),
        ('50-55','50-55'),
        ('56-60','56-60'),
        ('61-65','61-65'),
        ('66-69','66-69'),
        ('70-75','70-75'),
        ('others','Others'),
        ], "Age range", store=True)
    employment_type = fields.Selection([
        ('permanent','Permanent'),
        ('non_permanent','Non Permanent'),
        ('outsourced','Outsourced'),
        ('package','Package'),
        ('others','Others'),
        ],"Deployment Type Preferred", store=True)
    shift_preferences = fields.Selection([
        ('day','Day'),
        ('night','Night'),
        ('none','No Preference')
        ],"Shift Preference", store=True)
    preferred_shift = fields.Selection([
        ('day','Day'),
        ('night','Night'),
        ('none','No Preference')
        ],"Do you have a preferred shift", store=True)
    preferred_site = fields.Selection([
        ('condominium','Condominium'),
        ('factory','Factory'),
        ('light_industrial_bulding','Light Industrial Building'),
        ('office_buidling','Office Building'),
        ('heavy_industrial_building','Heavy Industrial Building'),
        ('shopping_centre','Shopping Centre'),
        ('showroom','Showroom'),
        ('school','School'),
        ('others','Others')
        ],"What type of work site do you prefer?", store=True)
    preferred_site_other = fields.Char('Others')
    preferred_site_suitable = fields.Selection([
        ('condominium','Condominium'),
        ('factory','Factory'),
        ('club_bar','Club / Bar'),
        ('office','Office'),
        ('light_industrial_bulding','Light Industrial'),
        ('events','Events'),
        ('school','School'),
        ('showroom','Showroom'),
        ('hotel_resort','Hotel / Resort'),
        ('shopping_centre','Shopping Centre'),
        ('others','Others')
        ],"Assessed Suitable For", store=True)
    preferred_site_ids = fields.Many2many('preferred.site', string="Preferred Type of Projects")
    preferred_site_suitable_ids = fields.Many2many('preferredsuitable.site', string="Assessed Suitable For")
    preferred_site_suitable_other = fields.Char('Others')
    no_days_avail = fields.Integer("No. of Days Available (Full Week)",default='')
    #days_avail = fields.Many2many('days.available', string="Do you have specific days you can work?")
    days_avail = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('no_pref', 'I do not have specific days I can work')
        ], "Do you have specific days you can work?", store=True)
    no_weekends_avail = fields.Integer("No. of Weekends Available",default='')
    #preferred_site = fields.Many2many('preferred.site', string="Preferred Sites")
    remarks = fields.Text()
    previous_company = fields.Char("Where did you work before this? (Company)")
    previous_working_site = fields.Char("Where did you work before this? (Project Sites)")
    reason_leave = fields.Text()
    pay_like = fields.Char("What was the pay like?")
    remarks_on_prev_comp = fields.Text()
    shift_id = fields.Many2one('salary.package','Salary Code', domain="[('time', '=', shift)]")
    shift_time = fields.Char('Shift Time')
    bs = fields.Boolean('Basic Salary')
    ot = fields.Boolean('Overtime')
    mvc = fields.Boolean('Monthly Variable Component')
    pis = fields.Boolean('Productivity Incentive')
    awbr = fields.Boolean('Attendance & Bonus Reward')
    shift = fields.Selection([
       ('730am730pm','7.30 am – 7.30 pm'),
       ('800am800pm','8.00 am – 8.00 pm'),
       ('800am600pm','8.00 am – 6.00 pm'),
       ('730pm730am','7.30 pm – 7.30 am'),
       ('800pm800am','8.00 pm – 8.00 am'),
       ], "Shift")
    contact_comment = fields.Text('Comment')
    interview_comment = fields.Text('Comment')
    link_url = fields.Char(string='Link')
    #declaration q and a
    illness = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Have you ever suffered, or are suffering from any medical condition, illness, disease, +mental illness or physical impairment? +Includes all forms of nervous breakdown and anxiety disorder", store=True)
    illness_yes = fields.Text('Details')
    criminal_record = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Do you have a criminal record in Singapore?", store=True)
    cr_yes = fields.Text('Details')
    charged_law = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Have you been charged with any offence in a court of law in Singapore or in any other country for which the outcome is pending?", store=True)
    cl_yes = fields.Text('Details')
    investigation_awareness = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Are you aware of being under any current police investigations in Singapore or in any other country following allegations made against you?", store=True)
    ia_yes = fields.Text('Details')
    financial_embarrassment = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Have you been or are you under any financial embarrassment i.e. (a) an undischarged bankrupt, (b) a judgement debtor, (c) have unsecured debts and liabilities of more than 3 months of last-drawn pay, (d) have signed a promissory note or an acknowledgement of indebtedness?", store=True)
    fe_yes = fields.Text('Details')
    broken_service_period = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Have you ever broken any bond or failed to fulfil any minimum service period?", store=True)
    bsp_yes = fields.Text('Details')
    currently_serving_bond = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Are you currently serving bond or any obligatory moral service with any organisation?", store=True)
    csb_yes = fields.Text('Details')
    dismissed_from_service = fields.Selection([
        ('yes','Yes'),
        ('no','No')
        ], "Have you ever been dismissed or discharged from the service of any employer?", store=True)
    dfs_yes = fields.Text('Details')
    #Declaration Signature and Date
    signature = fields.Binary(string="Signature", store=True)
    declaration_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    #IV form
    iv_place = fields.Char('Place of Interview')
    iv_date = fields.Date(string='Date of Interview',default=lambda self : fields.Date.today())
    area_of_resident = fields.Char('Area of Residence')
    higher_educational_qualification = fields.Char('Higher Educational Qualification')
    current_salary = fields.Char('Current / Last Drawn Salary')
    expected_salary = fields.Char('Expected Salary')
    salary_expected = fields.Float('Expected Salary')
    call_salary_expected = fields.Float('Expected Salary')
    work_experience_year = fields.Integer('Year')
    work_experience_month = fields.Integer('Month')
    current_position_held = fields.Char('Current Position Held')
    last_employer = fields.Char('Current / Last Employer')
    earliest_avail = fields.Date(string='Earliest Availability')
    uniform_size_tshirt = fields.Char('Uniform Size (T-Shirt)')
    uniform_size_shirt = fields.Char('Uniform Size (Shirt)')
    site_latitude = fields.Float(string='Site Latitude', digits=(16, 12), store=True)
    site_longitude = fields.Float(string='Site Longitude', digits=(16, 12), store=True)
    applicant_latitude = fields.Float(string='Applicant Latitude', digits=(16, 12), store=True)
    applicant_longitude = fields.Float(string='Applciant Longitude', digits=(16, 12), store=True)
    iframe = fields.Html('Embedded Webpage', sanitize=False, strip_style=False, readonly=True)
    onemap_type = fields.Selection([
        ('TRANSIT','Transit'),
        ('BUS','Bus'),
        ('drive','Drive'),
        ('walk','Walk'),
        ('cycle','Cycle')
        ], "OneMap Type", store=True)
    read_by = fields.Char(string="User", compute='get_read_by')
    """ NEW ADDED """
    have_permit = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
        ], "Have Work Permit?", store=True)
    custom_salary = fields.Boolean("Custom Package", default=False)
    basic_salary = fields.Float("Basic Salary")
    ot = fields.Float("Overtime")
    mvc = fields.Float("Monthly Variable Component")
    pis = fields.Float("Productivity Incentive")
    awbr = fields.Float("Attendance & Bonus Reward")

    _sql_constraints = [('mobile_no1', 'UNIQUE (mobile_no1)',  'Mobile number already registered!'),('call_mobile_no1', 'UNIQUE (call_mobile_no1)',  'Mobile number already registered!')]

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    # @api.multi
    # @api.depends('mobile_no1')
    # def _check_mobile_length(self):
    #     val = self.mobile_no1
    #     if(val == False):
    #         return self._warning(_("Contact No. Empty!"), _("Please insert contact number for this applicant."))

    @api.onchange('call_nationality')
    def _get_nationality(self):
        if self.call_nationality:
            self.nationality = self.call_nationality

    @api.onchange('call_preferred_emp_type')
    def _get_emp_type(self):
        if self.call_preferred_emp_type:
            self.emp_type = self.call_preferred_emp_type

    @api.onchange('date_of_birth')
    @api.depends('date_of_birth')
    @api.multi
    def _cal_age(self):
        if self.date_of_birth:
            years = relativedelta(date.today(), self.date_of_birth).years
            months = relativedelta(date.today(), self.date_of_birth).months
            day = relativedelta(date.today(), self.date_of_birth).days

            self.call_age = str(int(years))# + ' Year/s ' + str(int(months)) + ' Month/s ' + str(day) + ' Day/s'

    @api.multi
    def _get_sms_count(self):
        read_group_res = self.env['pushbullet.sms'].read_group(
            [('name', 'in', self.name)],
            ['name'], ['name'])
        data = dict((res['name'], res['name_count']) for res in read_group_res)
        for record in self:
            record.sms_count = data.get(record.name)

    @api.multi
    def get_sms_count(self):
        read_group_res = self.env['pushbullet.sms'].read_group(
            [('name', 'in', self.name)],
            ['name'], ['name'])
        data = dict((res['name'], res['name_count']) for res in read_group_res)


    @api.onchange('call_postal_code')
    def get_applicant_lang_lat2(self, return_geom=True, get_addr_details=True, page_num=1):
        #search_val = self.postal_code
        self.postal_code = self.call_postal_code
        if self.call_postal_code:
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "N"
            val2 = json.loads(requests.get(url, params={'searchVal': self.call_postal_code,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)
            #val3 = val2['results']
            for i in val2['results']:
                val4_name = i['SEARCHVAL']
                val4 = i['LATITUDE']
                val5 = i['LONGITUDE']
                
                self.call_applicant_latitude = val4
                self.call_applicant_longitude = val5
        val1 = []
        if(self.call_postal_code):
            val1.append(self.call_postal_code)
        self.address = self.call_postal_code

    @api.onchange('postal_code')
    def get_applicant_lang_lat(self, return_geom=True, get_addr_details=True, page_num=1):
        #search_val = self.postal_code
        if self.postal_code:
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "N"
            val2 = json.loads(requests.get(url, params={'searchVal': self.postal_code,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)
            #val3 = val2['results']
            for i in val2['results']:
                val4_name = i['SEARCHVAL']
                val4 = i['LATITUDE']
                val5 = i['LONGITUDE']
                
                self.applicant_latitude = val4
                self.applicant_longitude = val5


    def get_address_on_postal_code(self, return_geom=True, get_addr_details=True, page_num=1):
        #search_val = self.postal_code
        if self.postal_code:
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "Y"
            page_num = 1
            val2 = json.loads(requests.get(url, params={'searchVal': self.postal_code,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)

            for i in val2['results']:
                val4_name = i['SEARCHVAL']
                val4 = i['ADDRESS']
                
    @api.multi
    def get_all_records(self):
        app = []
        all_app = self.env['hr.applicant'].search([])
        for applicants in all_app:
            vals = {
                'id': applicants.id,
                'name': applicants.name,
                'default_whatsapp_account': applicants.whatsapp_account,
                'sender_number': applicants.whatsapp_account.sender_number,
                'receipient_no':applicants.mobile_no1,
                'wassenger_token':applicants.whatsapp_account.wassenger_token,
                }
            app.append(vals)
        return app


    @api.onchange('call_preferred_location1')
    def get_preferred_location_postalcode(self):
        self.call_postal_code = self.call_preferred_location1.postalcode


    @api.onchange('initial_mobile_code')
    def get_mobile_no1(self):
        val1 = self.initial_mobile_code
        if(val1 == 'sg'):
            self.call_mobile_no1 = '+65'
        if(val1 == 'my'):
            self.call_mobile_no1 = '+60'
        if(val1 == 'ph'):
            self.call_mobile_no1 = '+63'

    @api.onchange('call_mobile_no1')
    def get_mobile_no2(self):
        val = self.call_mobile_no1
        self.mobile_no1 = val

    @api.onchange('full_name')
    def get_full_name(self):
        val = self.full_name
        self.call_application_name = val

    @api.depends('read_by')
    def get_read_by(self):
        self.ensure_one()
        val = self.read_by_ids
        vid = []
        for v in val:
            vid.append(v.id)
        if (self.env.uid in vid):
            return
        else:
            self.env.cr.execute("INSERT INTO res_users_hr_applicant_rel (hr_applicant_id, res_users_id) VALUES (%s,%s)", (self.id, self.env.uid))

    @api.onchange('call_project_site')
    def get_site_lang_lat(self):
        for val in self.call_project_site:
            if val:
                self.call_site_latitude = val.site_latitude
                self.call_site_longitude = val.site_longitude

    @api.onchange('project_site')
    def get_site_lang_lat(self):
        for val in self.project_site:
            if val:
                self.site_latitude = val.site_latitude
                self.site_longitude = val.site_longitude

    @api.onchange('onemap_type')
    def get_iframe_one_map(self):
        route_type = self.onemap_type
        app_lat = self.applicant_latitude
        app_long = self.applicant_longitude
        site_lat = self.site_latitude
        site_long = self.site_longitude
        html = """
        <iframe src='https://tools.onemap.sg/amm/amm.html?&marker=latLng:{app_lat},{app_long}!colour:red&marker=latLng:{site_lat},{site_long}!colour:red!rType:{route_type}!rDest:{app_lat},{app_long}&zoomLevl=13&popupWidth=200&popupHeight=500&design=Default' height='850px' width='1040px' scrolling='no' frameborder='0' allowfullscreen='allowfullscreen'></iframe>
        """.format(route_type=route_type, app_lat=app_lat, app_long=app_long, site_lat=site_lat, site_long=site_long)

        self.iframe = html

    @api.multi
    @api.onchange('shift_id')
    def onchange_shift_id(self):
        for shift in self.shift_id:
            if shift:
                self.shift_time = shift.time

    @api.onchange('nric')
    def generate_our_reference(self):
        if self.nric:
            res = list(self.nric)
            if(res[0] == 'S'):
                res[0] = 'P'
                new_res = "".join(res)
                self.appointment_reference = new_res
            elif(res[0] == 'F'):
                res[0] = 'P'
                new_res = "".join(res)
                self.appointment_reference = new_res 
            elif(res[0] != 'S'):
                res1 = self.nric
                res2 = 'P'
                new_res = res2+res1
                self.appointment_reference = new_res 


    @api.multi
    def print_contract_document(self):
        for obj in self:
            if not obj.full_name:
                raise exceptions.ValidationError("Please set Full Name for this candidate.")
            # if not obj.project_site:
            #     raise exceptions.ValidationError("Please set Project Site for this candidate.")
            if not obj.shift:
                raise exceptions.ValidationError("Please set Shift for this candidate.")
            if not obj.shift_id:
                raise exceptions.ValidationError("Please set Salary Code for this employee.")
            elif ((obj.shift == '730am730pm')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily').report_action(self)
            elif ((obj.shift == '800am800pm')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily').report_action(self)
            elif ((obj.shift == '730pm730am')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily').report_action(self)
            elif ((obj.shift == '800pm800am')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily').report_action(self)
            elif ((obj.shift == '730am730pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly').report_action(self)
            elif ((obj.shift == '800am800pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly').report_action(self)
            elif ((obj.shift == '730pm730am')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly').report_action(self)
            elif ((obj.shift == '800pm800am')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly').report_action(self)
            elif ((obj.shift == '800am600pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly').report_action(self)
            else:
                #contract_report = self.env.ref('ov_ats.emp_contract_daily').report_action(self)
                return False
        return contract_report

    @api.multi
    def print_resume_application_form(self):
        application_resume_form = self.env.ref('ov_ats.application_resume_form').report_action(self)
        return application_resume_form

    @api.multi
    def print_interview_record_form(self):
        interview_record_form = self.env.ref('ov_ats.interview_record_form').report_action(self)
        return interview_record_form



    @api.model
    def create(self, vals):
        if vals.get('department_id') and not self._context.get('default_department_id'):
            self = self.with_context(default_department_id=vals.get('department_id'))
        if vals.get('job_id') or self._context.get('default_job_id'):
            job_id = vals.get('job_id') or self._context.get('default_job_id')
            for key, value in self._onchange_job_id_internal(job_id)['value'].items():
                if key not in vals:
                    vals[key] = value
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        if 'stage_id' in vals:
            vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))['value'])
        res = super(Ats, self.with_context(mail_create_nolog=True)).create(vals)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        copied_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (res.id, self._name)
        res['link_url'] = copied_url
        res['record_status'] = '1'
        name = vals.get('name')
        self.env['res.applicant'].create({
            'is_applicant' : True,
            'name':name,
            'postal_code': vals.get('call_postal_code'),
            'lat': vals.get('call_applicant_latitude'),
            'lng': vals.get('call_applicant_longitude'),
            'applicant_ids': res.id,
            })
        return res

    @api.multi
    def write(self, vals):
        # user_id change: update date_open
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        # stage_id: track last stage before update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))['value'])
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
            for applicant in self:
                vals['last_stage_id'] = applicant.stage_id.id
                res = super(Ats, self).write(vals)
        else:
            res = super(Ats, self).write(vals)
        return res



    @api.onchange('mobile_no1')
    def check_mobile(self):
        id_needed = []
        # id_needed2 = []
        wt = self.env['hr.applicant']
        id_needed = wt.search([('mobile_no1', '=', self.mobile_no1)])
        # for a in wt:
        #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #     copied_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (res.id, self._name)
        #     res['link_url'] = copied_url

        job = self.job_id
        name = self.call_application_name
        no = self.mobile_no1
        if no:
            if (no == id_needed.mobile_no1):
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (id_needed.id, id_needed._name)
                #res['link_url'] = url
                return self._warning(_("""<p><b>Mobile number exist in <a href="%s">%s</a></b></p>""" % (url,id_needed.name)), _("Please use other number."))


    def online_application_form(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/ats/applicant/%s/application/edit' % (self.id),
            'target': 'self',
            'res_id': self.id,
        }

    def online_iv_form(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/ats/applicant/%s/iv/edit' % (self.id),
            'target': 'self',
            'res_id': self.id,
        }


    @api.multi
    def reset_as_contact(self):
        default_stage_id_contact = self.env['hr.recruitment.stage'].search([('name', '=', 'Contact')]).id
        default_sub_stage_id_application = self.env['contact.substage'].search([('name', '=', 'New')]).id
        self.write({'application': False,'iv': False,'contract_proposal': False,'convert_to_emp': False,'enquiry': True,'contact_stage': default_sub_stage_id_application,'stage_id': default_stage_id_contact})

    @api.multi
    def add_as_application(self):
        default_stage_id_application = self.env['hr.recruitment.stage'].search([('name', '=', 'Application')]).id
        default_sub_stage_id_application = self.env['application.substage'].search([('name', '=', 'New')]).id
        self.write({'record_status':'0','application': True,'iv': False,'contract_proposal': False,'blacklist': False,'enquiry': False,'contact_stage': default_sub_stage_id_application,'stage_id': default_stage_id_application})

    @api.multi
    def interview_applicant(self):
        default_stage_id_interview = self.env['hr.recruitment.stage'].search([('name', '=', 'Interview')]).id
        self.write({'iv': True ,'application': False,'enquiry': False, 'stage_id': default_stage_id_interview})

    @api.multi
    def contract_proposal_stage(self):
        default_stage_id_contract = self.env['hr.recruitment.stage'].search([('name', '=', 'Employment Offer')]).id
        self.write({'contract_proposal': True,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_contract})

    @api.multi
    def banned_applicant(self):
        default_stage_id_banned = self.env['hr.recruitment.stage'].search([('name', '=', 'Banned')]).id
        self.write({'banned':True,'blacklist': False,'application': False,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_banned})

    @api.multi
    def blacklist_applicant(self):
        default_stage_id_blacklist = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
        self.write({'blacklist': True,'application': False,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_blacklist})

    @api.multi
    def reset_blacklist_applicant(self):
        default_stage_id_blacklist = self.env['hr.recruitment.stage'].search([('name', '=', 'Application')]).id
        self.write({'blacklist': False,'application': True,'enquiry': False, 'stage_id': default_stage_id_blacklist})

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        default_stage_id_employee = self.env['hr.recruitment.stage'].search([('name', '=', 'Employee')]).id
        self.write({'blacklist': False,'application': False,'iv': False,'contract_proposal': False,'convert_to_emp': True,'stage_id': default_stage_id_employee})
        employee = False
        for applicant in self:
            contact_name = False
            # if applicant.partner_id:
            #     address_id = applicant.partner_id.address_get(['contact'])['contact']
            #     contact_name = applicant.partner_id.name_get()[0][1]
            # else :
            #     new_partner_id = self.env['res.partner'].create({
            #         'is_company': False,
            #         'name': applicant.partner_name,
            #         'email': applicant.email_from,
            #         'phone': applicant.partner_phone,
            #         'mobile': applicant.mobile_no1
            #     })
            #     address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.job_id:# and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'id': applicant.id,
                    'related_applicant': applicant.id,
                    'name': applicant.full_name or False,
                    'salutation': applicant.salutation or False,
                    'mobile_phone': applicant.mobile_no1 or False,
                    'work_phone': applicant.partner_phone or False,
                    'postal_code': applicant.call_postal_code or False,
                    'races': applicant.call_races.id or False,
                    'project_site': applicant.call_project_site.id or False,
                    'country_id': applicant.country_id.id or False,
                    'nric': applicant.nric or False,
                    'mobile_no2': applicant.mobile_no2 or False,
                    'have_permit': applicant.have_permit or False,
                    'custom_salary': applicant.custom_salary or False,
                    'basic_salary': applicant.basic_salary or False,
                    'ot': applicant.ot or False,
                    'mvc': applicant.mvc or False,
                    'pis': applicant.pis or False,
                    'awbr': applicant.awbr or False,
                    #'license': applicant.driving_license or False,
                    'gender': applicant.call_gender or False,
                    'age': applicant.call_age or False,
                    'employment_type': applicant.employment_type or False,
                    'shift_preferences': applicant.shift_preferences or False,
                    'commencement_date': applicant.commencement_date or False,
                    'shift': applicant.shift,
                    'shift_id': applicant.shift_id or False,
                    'emp_type': applicant.emp_type,
                    'no_days_avail': applicant.no_days_avail or False,
                    'no_weekends_avail': applicant.no_weekends_avail or False,
                    'preferred_site': applicant.preferred_site or False,
                    'remarks': applicant.remarks or False,
                    'job_id': applicant.job_id.id,
                    'appointment_reference': applicant.appointment_reference or False,
                    'letter_date': applicant.letter_date or False,
                    # 'address_home_id': address_id,
                    # 'department_id': applicant.department_id.id or False,
                    # 'address_id': applicant.company_id and applicant.company_id.partner_id
                    #         and applicant.company_id.partner_id.id or False,
                    # 'work_email': applicant.department_id and applicant.department_id.company_id
                    #         and applicant.department_id.company_id.email or False,
                    # 'work_phone': applicant.department_id and applicant.department_id.company_id
                    #         and applicant.department_id.company_id.phone or False
                            })
                applicant.write({'emp_id': employee.id})
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                copied_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (employee.id, self._name)
                applicant.write({'link_url': copied_url})
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.full_name if applicant.full_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window

    @api.multi
    def _address_as_string(self):
        self.ensure_one()
        #addr = self.project_site.postcode
        #return addr;
        addr = []
        if self.project_site.postcode:
            addr.append(self.project_site.postcode)
        # if not addr:
        #     raise UserError(_("Address missing on partner '%s'.") % self.name)
        return ' '.join(addr)

    @api.model
    def _prepare_url(self, url, replace):
        assert url, 'Missing URL'
        for key, value in replace.items():
            if not isinstance(value, str):
                # for latitude and longitude which are floats
                value = str(value)
            url = url.replace(key, value)
        logger.debug('Final URL: %s', url)
        return url

    @api.multi
    def open_project_site_map(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        map_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (res.id, self._name)

        url = self._prepare_url(
            map_website.address_url,
            {'{ADDRESS}': self._address_as_string()})
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    @api.multi
    def open_map(self):
        self.ensure_one()
        map_website = self.env.user.context_map_website_id
        if not map_website:
            raise UserError(
                _('Missing map provider: '
                  'you should set it in your preferences.'))
        if (map_website.lat_lon_url and hasattr(self, 'partner_latitude') and
                self.partner_latitude and self.partner_longitude):
            url = self._prepare_url(
                map_website.lat_lon_url, {
                    '{LATITUDE}': self.partner_latitude,
                    '{LONGITUDE}': self.partner_longitude})
        else:
            if not map_website.address_url:
                raise UserError(
                    _("Missing parameter 'URL that uses the address' "
                      "for map website '%s'.") % map_website.name)
            url = self._prepare_url(
                map_website.address_url,
                {'{ADDRESS}': self._address_as_string()})
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    @api.multi
    def open_route_map(self):
        self.ensure_one()
        if not self.env.user.context_route_map_website_id:
            raise UserError(
                _('Missing route map website: '
                  'you should set it in your preferences.'))
        map_website = self.env.user.context_route_map_website_id
        if not self.postal_code:
            raise UserError(
                _('Missing start address for route map: '
                  'you should set it in your preferences.'))
        start_partner = self.postal_code
        if (map_website.route_lat_lon_url and
                hasattr(self, 'partner_latitude') and
                self.partner_latitude and self.partner_longitude and
                start_partner.partner_latitude and
                start_partner.partner_longitude):
            url = self._prepare_url(  # pragma: no cover
                map_website.route_lat_lon_url, {
                    '{START_LATITUDE}': start_partner.partner_latitude,
                    '{START_LONGITUDE}': start_partner.partner_longitude,
                    '{DEST_LATITUDE}': self.partner_latitude,
                    '{DEST_LONGITUDE}': self.partner_longitude})
        else:
            if not map_website.route_address_url:
                raise UserError(
                    _("Missing route URL that uses the addresses "
                        "for the map website '%s'") % map_website.name)
            url = self._prepare_url(
                map_website.route_address_url, {
                    '{START_ADDRESS}': start_partner,
                    '{DEST_ADDRESS}': self._address_as_string()})
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    @api.onchange('blacklist')
    def _if_blacklisted(self):
        stage = self.env['hr.recruitment.stage'].browse(self._context.get('active_ids'))
        res = self.stage_id.name
        if self.blacklist == 1:
            res == 'Blacklisted'

    @api.multi
    def action_view_maps(self):
        """ This opens Project Site Maps location
        """
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('ov_ats', 'action_ov_res_applicant')
        
        
        res['domain'] = ['|','|',('is_projectsite', '=', True),('applicant_ids', '=', self),('name', '=', self.name)]
        # res['context'] = {
        #     'default_res_model': 'hr.expense.sheet',
        #     'default_res_id': self.id,
        #     'create': False,
        #     'edit': False,
        # }
        return res

    @api.multi
    def action_open_twain_scanner(self):
        """ This opens TWAIN Scanner module
        """
        action_context = {'applicant_id': self.id, 'res_id': self.id, 'res_model': 'hr.applicant'}
        res = {
            'type': 'ir.actions.client',
            'name':'Scan Document',
            'tag':'twain_scanner',
            'context': action_context,
            # 'applicant_id': self.id,#self._context['res_id']
        }
        return res

class SalaryPackage(models.Model):
    _name = 'salary.package'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char("Salary Code", required=True,track_visibility='always')
    type_of_package = fields.Selection([
        ('daily','Daily'),
        ('monthly','Monthly'),
        ], "Salary Scheme", help='Type of appoinment i.e: Full-Time/Part-Time')
    payment_schedule = fields.Selection([
        ('daily','Daily'),
        ('monthly','Monthly'),
        ], "Salary Scheme", help='Type of appoinment i.e: Full-Time/Part-Time')
    time = fields.Selection([
        ('730am730pm','7.30 am – 7.30 pm'),
        ('800am800pm','8.00 am – 8.00 pm'),
        ('800am600pm','8.00 am – 6.00 pm'),
        ('730pm730am','7.30 pm – 7.30 am'),
        ('800pm800am','8.00 pm – 8.00 am'),
        ], "Shift")
    basic_salary = fields.Float("Basic Salary")
    ot = fields.Float("Overtime")
    mvc = fields.Float("Monthly Variable Component")
    pis = fields.Float("Productivity Incentive")
    awbr = fields.Float("Attendance & Bonus Reward")

    @api.multi
    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            if ((self.name == 'SCDSGSO18') or (self.name == 'SCDSGSO213') or (self.name == 'SCDSGSO323') or (self.name == 'SCDSGSS1') or (self.name == 'SCDSGSSO1')):
                self.type_of_package = 'daily'
            else:
                self.type_of_package = 'monthly'



class InterviewAssessment(models.Model):
    _name = 'iv.assessment'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Interview Assessment'

    personal_grooming = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Personal Grooming", store=True)
    personal_expression = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Personal Expression", store=True)
    confidence = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Confidence", store=True)
    maturity = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Maturity", store=True)
    commitment_n_drive = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Commitment and Drive", store=True)
    communication_skills = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Communication Skills", store=True)
    mental_alertness = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Mental Alertness", store=True)
    knowledge_and_skills = fields.Selection([
        ('below_average_1','1'),
        ('below_average_2','2'),
        ('below_average_3','3'),
        ('average_4','4'),
        ('average_5','5'),
        ('average_6','6'),
        ('excellent_7','7')
        ], "Knowledge and Skills", store=True)
    recommendation = fields.Selection([
        ('highly_recommended','Highly Recommended'),
        ('recommended','Recommended'),
        ('not_recommended','Not Recommended'),
        ('kiv','Keep in View')
        ], "Recommendation", store=True)
    recommendation_remarks = fields.Text('Remarks')
    strength_identified = fields.Text('Strength Identified')
    possible_weaknesses = fields.Text('Possible Weaknesses')
    other_comments = fields.Text('Other Comments/ Possible Deployment')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)
    name = fields.Char('Assessment Name')
    interviewer = fields.Many2one('res.users','Interviewer', default=lambda self: self.env.user)
    positive_char_ids = fields.Many2many('positive.character', string="Positive Character Traits")
    negative_char_ids = fields.Many2many('negative.character', string="Negative Character Traits")
    preferred_site_suitable_ids = fields.Many2many('preferredsuitable.site', string="Assessed Suitable For")
    recruiter = fields.Many2one('res.users','Recruiter', default=lambda self: self.env.user)
    recruiter_signature = fields.Binary(string="Signature", store=True)




