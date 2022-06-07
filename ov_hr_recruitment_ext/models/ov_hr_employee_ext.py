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

    appointment_reference = fields.Char("Our Ref.")
    partner_id = fields.Many2one("res.partner", "Partner")
    approval = fields.Many2one("hr.employee", "Approval")
    letter_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    commencement_date = fields.Date(string='Commencement Date')
    description = fields.Text()
    partner_name = fields.Char("Name of Candidate")
    salutation = fields.Selection([('mr', 'Mr'),('ms', 'Ms'),('mrs', 'Mrs')], "Salutation", store=True)
    country_id = fields.Many2one("res.country", "Nationality")
    races = fields.Many2one("ov.races", "Races")
    postal_code = fields.Integer("Postal Code",default='')
    country_image = fields.Binary(readonly=True, related='country_id.image')
    project_site = fields.Many2one('ov.projectsite', "Project Site Name")
    preferred_location1 = fields.Many2one('ov.preflocation', "Preferred Location 1")
    preferred_location2 = fields.Many2one('ov.preflocation', "Preferred Location 2")
    preferred_location3 = fields.Many2one('ov.preflocation', "Preferred Location 3")
    quality_of_contact = fields.Selection(AVAILABLE_QUALITY, "Quality of Contact", default='0')
    blacklist = fields.Boolean("Blacklist", default=False)
    blacklist_note = fields.Text()
    nric = fields.Char("NRIC No.")
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
    age = fields.Selection([
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
        ], "Age")
    employment_type = fields.Selection([
        ('permanent','Permanent'),
        ('non_permanent','Non Permanent'),
        ('outsourced','Outsourced'),
        ('package','Package'),
        ('others','Others'),
        ],"Deployment Type")
    shift_preferences = fields.Selection([
        ('day','Day'),
        ('night','Night'),
        ],"Shift Preference")
    no_days_avail = fields.Integer("No. of Days Available (Full Week)",default='')
    days_avail = fields.Many2many('ov.daysavail', string="")
    no_weekends_avail = fields.Integer("No. of Weekends Available",default='')
    preferred_site = fields.Many2many('ov.preferredsite', string="Preferred Sites")
    remarks = fields.Text()
    previous_company = fields.Char("Where did you work before this? (Company)")
    previous_working_site = fields.Char("Where did you work before this? (Project Sites)")
    reason_leave = fields.Text()
    pay_like = fields.Char("What was the pay like?")
    remarks_on_prev_comp = fields.Text()
    shift_id = fields.Many2one('ov.salarypackage','Salary Code', domain="[('time', '=', shift)]")
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
    link_url = fields.Char(string='Link')

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.one
    def copy_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        copied_url = base_url+'/web#id=%s&action=173&model=%s&view_type=form&menu_id=132' % (self.id, self._name)
        test = pyperclip.copy(copied_url)
        pyperclip.copy(copied_url)
        pyperclip.paste(copied_url)
        print (test)


    @api.multi
    @api.onchange('shift_id')
    def onchange_shift_id(self):
        for shift in self.shift_id:
            if shift:
                self.shift_time = shift.time

    # @api.multi
    # @api.onchange('shift')
    # def onchange_shift(self):
    #     for t in self.shift:
    #         if t:
    #             self.shift_time = shift.time

    @api.multi
    def print_contract_document(self):
        for obj in self:
            if not obj.shift:
                raise exceptions.ValidationError("Please set Shift for this employee.")
            if not obj.shift_id:
                raise exceptions.ValidationError("Please set Salary Code for this employee.")
            elif ((obj.shift_time == '730am730pm')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
            elif ((obj.shift_time == '800am800pm')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
            elif ((obj.shift_time == '730pm730am')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
            elif ((obj.shift_time == '800pm800am')&(obj.shift_id.type_of_package=='daily')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
            elif ((obj.shift_time == '730am730pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
            elif ((obj.shift_time == '800am800pm')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
            elif ((obj.shift_time == '730pm730am')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
            elif ((obj.shift_time == '800pm800am')&(obj.shift_id.type_of_package=='monthly')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_monthly').report_action(self)
            else:
                #contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_daily').report_action(self)
                return False
        return contract_report