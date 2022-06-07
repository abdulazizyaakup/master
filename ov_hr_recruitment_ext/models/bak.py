# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _

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
        ],"Employment Type Preferred")
    shift_preferences = fields.Many2many('ov.shift', string="Shift Preference")
    no_days_avail = fields.Integer("No. of Days Available (Full Week)",default='')
    no_weekends_avail = fields.Integer("No. of Weekends Available",default='')
    preferred_site = fields.Many2many('ov.preferredsite', string="Preferred Sites")
    remarks = fields.Text()
    previous_company = fields.Many2one('res.partner', "Where did you work before this? (Company)")
    previous_working_site = fields.Many2one('ov.projectsite', "Where did you work before this? (Project Sites)")
    reason_leave = fields.Text()
    pay_like = fields.Char("What was the pay like?")
    remarks_on_prev_comp = fields.Text()
    salary_code = fields.Selection([
        ('SCDSGSO18','SCDSGSO18'),
        ('SCDSGSO213','SCDSGSO213'),
        ('SCDSGSO323','SCDSGSO323'),
        ('SCDSGSS1','SCDSGSS1'),
        ('SCDSGSSO1','SCDSGSSO1'),
        ('SCMMYSO2145','SCMMYSO2145'),
        ('SCMMYSO2145P','SCMMYSO2145P'),
        ('SCMMYSS2365','SCMMYSS2365'),
        ('SCMMYSS2365P','SCMMYSS2365P'),
        ('SCMMYSSO2255','SCMMYSSO2255'),
        ('SCMMYSSO2255P','SCMMYSSO2255P'),
        ('SCMMYSO145','SCMMYSO145'),
        ('SCMMYSO145P','SCMMYSO145P'),
        ('SCMMYSS1265','SCMMYSS1265'),
        ('SCMMYSS1265P','SCMMYSS1265P'),
        ('SCMMYSSO1155','SCMMYSSO1155'),
        ('SCMMYSSO1155P','SCMMYSSO1155P'),
        ('SCMSGSO2100','SCMSGSO2100'),
        ('SCMSGSO2100P','SCMSGSO2100P'),
        ('SCMSGSS1','SCMSGSS1'),
        ('SCMSGSS1P','SCMSGSS1P'),
        ('SCMSGSSO1','SCMSGSSO1'),
        ('SCMSGSSO1P','SCMSGSSO1P'),
        ('SCMSGSSS1','SCMSGSSS1'),
        ('SCMSGSSS1P','SCMSGSSS1P'),
        ], "Salary Code")
    shift = fields.Many2one('Shift',required=True)
    #shift = fields.Selection([
    #    ('730am730pm','7.30 am – 7.30 pm'),
    #    ('800am800pm','8.00 am – 8.00 pm'),
    #    ('730pm730am','7.30 pm – 7.30 am'),
    #    ('800pm800am','8.00 pm – 8.00 am'),
    #    ], "Shift")

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.multi
    def print_contract_document(self):
        for obj in self:
            if not obj.salary_code:
                raise exceptions.ValidationError("Please set Salary Code for this employee.")
            if not obj.shift:
                raise exceptions.ValidationError("Please set Shift for this employee.")
            elif ((obj.salary_code == 'SCDSGSO18')&(obj.shift=='730am730pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso18_730am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO213')&(obj.shift=='730am730pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso213_730am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO323')&(obj.shift=='730am730pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso323_730am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSS1')&(obj.shift=='730am730pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgss1_730am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSSO1')&(obj.shift=='730am730pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgsso1_730am').report_action(self)
                #end if for day 730am
            elif ((obj.salary_code == 'SCDSGSO18')&(obj.shift=='730pm730am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso18_730pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO213')&(obj.shift=='730pm730am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso213_730pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO323')&(obj.shift=='730pm730am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso323_730pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSS1')&(obj.shift=='730pm730am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgss1_730pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSSO1')&(obj.shift=='730pm730am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgsso1_730pm').report_action(self)
                #end if for day 730pm
            elif ((obj.salary_code == 'SCDSGSO18')&(obj.shift=='800am800pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso18_800am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO213')&(obj.shift=='800am800pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso213_800am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO323')&(obj.shift=='800am800pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso323_800am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSS1')&(obj.shift=='800am800pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgss1_800am').report_action(self)
            elif ((obj.salary_code == 'SCDSGSSO1')&(obj.shift=='800am800pm')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgsso1_800am').report_action(self)
                #end if for day 800am
            elif ((obj.salary_code == 'SCDSGSO18')&(obj.shift=='800pm800am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso18_800pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO213')&(obj.shift=='800pm800am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso213_800pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSO323')&(obj.shift=='800pm800am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgso323_800pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSS1')&(obj.shift=='800pm800am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgss1_800pm').report_action(self)
            elif ((obj.salary_code == 'SCDSGSSO1')&(obj.shift=='800pm800am')):
                contract_report = self.env.ref('ov_hr_recruitment_ext.emp_contract_scdsgsso1_800pm').report_action(self)
                #end if for day 800am
            else:
                return False
        return contract_report