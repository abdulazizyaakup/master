# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _
#import pyperclip
#import copy

class EmployeeStage(models.Model):
    _name = 'employee.stage'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Employee Stages'
    
    name = fields.Char('Stage')

AVAILABLE_QUALITY = [
    ('0', 'Poor'),
    ('1', 'Normal'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent')
]

class OvHrEmployeeExt(models.Model):
    _inherit = 'hr.employee'

    def _default_stage_id(self):
        val = self.env['employee.stage'].search([('name','=','Employee')])
        return val.id

    """ Basic Info """
    personnel_type = fields.Selection([('employee','Employee'),('contractor','Contractor')])
    code_type = fields.Selection([('ft','FT'),('pt','PT')])
    personnel_code = fields.Char("Personnel Code")
    preferred_name = fields.Char("Preferred Name")
    short_name = fields.Char("Short Name")
    deployment_name = fields.Char("Deployment Name")
    plrd_name = fields.Char("PLRD Name")
    nric = fields.Char("NRIC No. / FIN No")
    old_nric = fields.Char("Old NRIC No. / FIN No")
    """ End Basic Info """
    """ General Info """
    appointment_date = fields.Date("Appointment Date")
    commencement_date = fields.Date("Commencement Date")
    confirmation_date = fields.Date("Confirmation Date")
    promotion_date = fields.Date("Promotion Date")
    resignation_date = fields.Date("Resignation Date")
    termination_date = fields.Date("Termination Date")
    nationality = fields.Selection([
        ('singaporean', 'Singaporean'),
        ('pr', 'Singapore Permanent Resident'),
        ('malaysian', 'Malaysian'),
        ('philipines', 'Phillipines')
        ], "Nationality", store=True)
    races = fields.Many2one("applicant.races", "Races")
    age = fields.Integer('Age')
    gender = fields.Selection([('male','Male'),('female','Female')], "Gender")
    date_of_birth = fields.Date(string='Date of Birth')
    country_of_birth = fields.Many2one("res.country", "Country of Birth")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
        ], "Marital Status", store=True)
    postal_code = fields.Integer("Postal Code",default='')
    """ End General Info """
    """ Employment Info """
    probation_period = fields.Char("Probation Period")
    job_id = fields.Many2one('hr.job', "Job Title")
    individual_pwm_grade = fields.Selection([
        ('so', 'Security Officer'),
        ('sso', 'Senior Security Officer'),
        ('ss', 'Security Supervisor'),
        ('sss', 'Senior Security Supervisor'),
        ('cso', 'Chief Security Officer')
        ], "Individual PWM Grade", store=True)
    employment_grade = fields.Char('Employment Grade')
    driving_license = fields.Selection([
        ('class3','Class 3'),
        ('class2','Class 2 / 2A / 2B'),
        ('no','Nil'),
        ('others','Others')
        ], "License", store=True)
    d_license_number = fields.Char("License Number")
    vehicle = fields.Selection([('yes','Yes'),('no','No')])
    team = fields.Char("Team")
    shift_preferences = fields.Selection([
        ('day','Day'),
        ('night','Night'),
        ],"Shift Preference")
    primary_shift = fields.Char("Primary Shift")
    security_license = fields.Char("Security License")
    security_license_expiry = fields.Date("License Expiry Date")
    """ End Employment Info """
    stage_id = fields.Many2one('employee.stage','Stage',default=_default_stage_id)
    resigned = fields.Boolean("Resigned", default=False)
    terminated = fields.Boolean("Terminated", default=False)
    employee = fields.Boolean("Employee", default=True)
    related_applicant = fields.Many2one('hr.applicant', "Related Applicant")
    appointment_reference = fields.Char("Our Ref.")
    partner_id = fields.Many2one("res.partner", "Partner")
    approval = fields.Many2one("hr.employee", "Approval")
    letter_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    commencement_date = fields.Date(string='Commencement Date')
    description = fields.Text()
    partner_name = fields.Char("Name of Candidate")
    salutation = fields.Selection([('mr', 'Mr'),('ms', 'Ms'),('mrs', 'Mrs')], "Salutation", store=True)
    country_id = fields.Many2one("res.country", "Nationality")
    country_image = fields.Binary(readonly=True, related='country_id.image')
    project_site = fields.Many2one('project.site', "Project Site")
    preferred_location1 = fields.Many2one('ov.preflocation', "Preferred Location 1")
    preferred_location2 = fields.Many2one('ov.preflocation', "Preferred Location 2")
    preferred_location3 = fields.Many2one('ov.preflocation', "Preferred Location 3")
    quality_of_contact = fields.Selection(AVAILABLE_QUALITY, "Quality of Contact", default='0')
    blacklist = fields.Boolean("Blacklist", default=False)
    blacklist_note = fields.Text()
    mobile_no2 = fields.Char("Mobile No. 2", size=32)
    source_ids = fields.Many2one('ov.source','Source')
    day_of_source = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
        ], "Day of Source", store=True)
    status_of_candidate = fields.Selection([
        ('nuturing', 'Nuturing'),
        ('dead', 'Dead'),
        ('scheduled_for_interview', 'Scheduled For Interview'),
        ('offer_rejected', 'Offer - Rejected'),
        ('to_follow_up', 'To Follow Up'),
        ('recruited_start', 'Recruited - Start'),
        ('recruited_mia', 'Recruited - MIA'),
        ('recruited_pending', 'Recruited - Pending'),
        ('wss_reject', 'WSS Reject'),
        ('call_in_future', 'Call In Future'),
        ], "Status Of Candidate", store=True)
    date_of_source = fields.Date(string='Date of Source',default=lambda self : fields.Date.today())
    license = fields.Selection([('yes','Yes'),('no','No')], "License")
    gender = fields.Selection([('male','Male'),('female','Female')], "Gender")
    # age = fields.Selection([
    #     ('18-19','18-19'),
    #     ('20-29','20-29'),
    #     ('30-39','30-39'),
    #     ('40-49','40-49'),
    #     ('50-55','50-55'),
    #     ('56-60','56-60'),
    #     ('61-65','61-65'),
    #     ('66-69','66-69'),
    #     ('70-75','70-75'),
    #     ('others','Others'),
    #     ], "Age")
    employment_type = fields.Selection([
        ('permanent','Permanent'),
        ('non_permanent','Non Permanent'),
        ('outsourced','Outsourced'),
        ('package','Package'),
        ('others','Others'),
        ],"Deployment Type")
    no_days_avail = fields.Integer("No. of Days Available (Full Week)",default='')
    #days_avail = fields.Many2many('ov.daysavail', string="")
    no_weekends_avail = fields.Integer("No. of Weekends Available",default='')
    #preferred_site = fields.Many2many('ov.preferredsite', string="Preferred Sites")
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
    link_url = fields.Char(string='Link')
    emp_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('permanent_relief', 'Permanent Relief'),
        ('relief', 'Relief'),
        ('package', 'Package')
        ], "Employement Type", store=True)
    appointment_reference = fields.Char("Our Ref.")
    letter_date = fields.Date(string='Date of Issuance of Letter of Appointment')
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
    nationality = fields.Selection([
        ('singaporean', 'Singaporean'),
        ('pr', 'Singapore PR'),
        ('malaysian', 'Malaysian'),
        ('others', 'Others')
        ], "Nationality", store=True)

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.onchange('nric')
    def generate_our_reference(self):
        if self.nric:
            res = list(self.nric)
            if(res[0] == 'F'):
                res[0] = 'P'
                new_res = "".join(res)
                self.appointment_reference = new_res
            # elif(res[0] != 'S'):
            #     res1 = self.nric
            #     res2 = 'P'
            #     new_res = res2+res1
            #     self.appointment_reference = new_res 


    @api.multi
    def print_contract_document(self):
        for obj in self:
            if not obj.name:
                raise exceptions.ValidationError("Please set Full Name for this candidate.")
            # if not obj.project_site:
            #     raise exceptions.ValidationError("Please set Project Site for this candidate.")
            if not obj.shift:
                raise exceptions.ValidationError("Please set Shift for this candidate.")
            if not obj.shift_id:
                raise exceptions.ValidationError("Please set Salary Code for this employee.")
            elif ((obj.shift == '730am730pm')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily2').report_action(self)
            elif ((obj.shift == '800am800pm')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily2').report_action(self)
            elif ((obj.shift == '730pm730am')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily2').report_action(self)
            elif ((obj.shift == '800pm800am')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_ats.emp_contract_daily2').report_action(self)
            elif ((obj.shift == '730am730pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly2').report_action(self)
            elif ((obj.shift == '800am800pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly2').report_action(self)
            elif ((obj.shift == '730pm730am')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly2').report_action(self)
            elif ((obj.shift == '800pm800am')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly2').report_action(self)
            elif ((obj.shift == '800am600pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_ats.emp_contract_monthly2').report_action(self)
            else:
                #contract_report = self.env.ref('ov_ats.emp_contract_daily').report_action(self)
                return False
        return contract_report


    @api.multi
    def emp_terminate(self):
        self.write({'employee': False,'resigned': False,'terminated': True})
        source = self.env['wss.campaign'].search(['name','=','Ex-Employee'])
        applicant = self.related_applicant.id
        applicant.write({'call_campaign':source.id})

    @api.multi
    def emp_resign(self):
        self.write({'employee': False,'resigned': True,'terminated': False})
        source = self.env['wss.campaign'].search([])
        applicant = self.related_applicant
        for s in source:
            if(s.name == 'Ex-Employee'):
                applicant.write({'call_campaign':s.id})
        
        
        # print("ID \n", applicant.id)

    @api.multi
    def emp_reset(self):
        self.write({'employee': True,'resigned': False,'terminated': False})


class EmployeeResignDetails(models.Model):
    _name = 'employee.resignation.details'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Employee Resignation Details'
    
    # employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    name = fields.Char("Name")
    applicant_id = fields.Many2one('hr.applicant', string="Related Applicant")
    resignation_date = fields.Date("Resignation Date")
    resignation_reason = fields.Text("Reason")
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

