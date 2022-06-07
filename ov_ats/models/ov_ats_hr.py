# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _
#import pyperclip
#import copy

AVAILABLE_QUALITY = [
    ('0', 'Poor'),
    ('1', 'Normal'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent')
]

class OvHrEmployeeExt(models.Model):
    _inherit = 'hr.employee'

    m_words = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Words", store=True)
    m_excel = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Excel", store=True)
    m_powerpoint = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Power Point", store=True)
    m_outlook = fields.Selection([('nil', 'Nil'),('basic', 'Basic'),('intermediate', 'Intermediate')], "Microsoft Outlook", store=True)
    #For Stage
    applicant_image = fields.Binary('Image', attachment=True)
    enquiry = fields.Boolean("Contact", default=True)
    application = fields.Boolean("Application", default=False)
    iv = fields.Boolean("Interview", default=False)
    contract_proposal = fields.Boolean("Contract Proposal", default=False)
    convert_to_emp = fields.Boolean("Converted to Employee", default=False)
    blacklist = fields.Boolean("Blacklist", default=False)
    blacklist_note = fields.Text()
    #SubStage for Contact
    # contact_stage = fields.Many2one('contact.substage','Contact Stage',default=_default_contact_stage_id)
    # application_stage = fields.Many2one('application.substage','Application Stage',default=_default_application_stage_id)
    # interview_stage = fields.Many2one('interview.substage','Interview Stage',default=_default_interview_stage_id)
    school_ids = fields.One2many('edu.back', 'applicant_id', string="School")
    alevel_ids = fields.One2many('alevel.result', 'applicant_id', string="GCE 'A' Level Result")
    nolevel_ids = fields.One2many('nolevel.result', 'applicant_id', string="GCE 'N'/'O' Level Result")
    lang_ids = fields.One2many('language.spokenwritten', 'applicant_id', string="Language(s)")
    dialect_ids = fields.One2many('language.dialect', 'applicant_id', string="Dialect")
    careerhistory_ids = fields.One2many('career.history', 'applicant_id', string="Career History")
    days_avail_ids = fields.Many2many('days.avail','days_avail_hr_applicant_rel', 'hr_applicant_id', 'days_avail_id', string="Working Days Preference")
    #nationalservice_ids = fields.One2many('national.service', 'applicant_id', string="National Service")
    nationalservice = fields.Selection([
        ('saf', 'SAF'),
        ('spf', 'SPF'),
        ('scdf', 'SCDF'),
        ('nil', 'Not Served')
        ], "National Service", store=True)
    reason = fields.Text('Reason Not Served')
    rank = fields.Char('Rank')
    pes_grading = fields.Char('PES Grading')
    enlistment_date = fields.Date(string='Enlistment Date')
    operation_ready_date = fields.Date(string='Operation Ready Date')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade', index=True, copy=False, readonly=True)
    #other information

    #Details Information Needed
    appointment_reference = fields.Char("Our Ref.")
    description = fields.Text()
    letter_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    commencement_date = fields.Date(string='Commencement Date')
    partner_name = fields.Char("Name of Candidate")
    salutation = fields.Selection([('mr', 'Mr'),('ms', 'Ms'),('mrs', 'Mrs')], "Salutation", store=True)
    address = fields.Text('Address')
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
    mobile_no1 = fields.Char("Mobile No.", size=32)
    mobile_no2 = fields.Char("Mobile No. 2", size=32)
    email = fields.Char("Email Address", size=128)
    # source_ids = fields.Many2one('job.source','Source')
    post_source = fields.Selection([
        ('newspaper_advertisement','Newspaper Advertisement'),
        ('word_of_mouth','Word of Mouth'),
        ('website','Website'),
        ('friends_relative','Website'),
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
    driving_license = fields.Selection([
        ('class3','Class 3'),
        ('class2','Class 2 / 2A / 2B'),
        ('no','Nil'),
        ('others','Others')
        ], "License", store=True)
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
    driving_license_other = fields.Char('Others')
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
    owner = fields.Many2one('res.users','Owner', default=lambda self: self.env.user)
    recruiter = fields.Many2one('res.users','Recruiter', default=lambda self: self.env.user)
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
    #no_days_avail = fields.Integer("No. of Days Available (Full Week)",default='')
    #days_avail = fields.Many2many('days.available', string="Do you have specific days you can work?")
    # days_avail = fields.Selection([
    #     ('monday', 'Monday'),
    #     ('tuesday', 'Tuesday'),
    #     ('wednesday', 'Wednesday'),
    #     ('thursday', 'Thursday'),
    #     ('friday', 'Friday'),
    #     ('saturday', 'Saturday'),
    #     ('sunday', 'Sunday'),
    #     ('no_pref', 'I do not have specific days I can work')
    #     ], "Do you have specific days you can work?", store=True)
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
    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    # @api.one
    # def copy_link(self):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     copied_url = base_url+'/web#id=%s&action=173&model=%s&view_type=form&menu_id=132' % (self.id, self._name)
    #     test = pyperclip.copy(copied_url)
    #     pyperclip.copy(copied_url)
    #     pyperclip.paste(copied_url)
    #     print (test)


    # @api.multi
    # @api.onchange('shift_id')
    # def onchange_shift_id(self):
    #     for shift in self.shift_id:
    #         if shift:
    #             self.shift_time = shift.time

    # @api.multi
    # @api.onchange('shift')
    # def onchange_shift(self):
    #     for t in self.shift:
    #         if t:
    #             self.shift_time = shift.time

    # @api.multi
    # def print_contract_document(self):
    #     for obj in self:
    #         if not obj.shift:
    #             raise exceptions.ValidationError("Please set Shift for this employee.")
    #         if not obj.shift_id:
    #             raise exceptions.ValidationError("Please set Salary Code for this employee.")
    #         elif ((obj.shift_time == '730am730pm')&(obj.shift_id.type_of_package=='daily')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
    #         elif ((obj.shift_time == '800am800pm')&(obj.shift_id.type_of_package=='daily')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
    #         elif ((obj.shift_time == '730pm730am')&(obj.shift_id.type_of_package=='daily')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
    #         elif ((obj.shift_time == '800pm800am')&(obj.shift_id.type_of_package=='daily')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
    #         elif ((obj.shift_time == '730am730pm')&(obj.shift_id.type_of_package=='monthly')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
    #         elif ((obj.shift_time == '800am800pm')&(obj.shift_id.type_of_package=='monthly')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
    #         elif ((obj.shift_time == '730pm730am')&(obj.shift_id.type_of_package=='monthly')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
    #         elif ((obj.shift_time == '800pm800am')&(obj.shift_id.type_of_package=='monthly')):
    #             contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
    #         else:
    #             #contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
    #             return False
    #     return contract_report