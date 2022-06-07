# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request
import logging
#import pyperclip
#import copy

logger = logging.getLogger(__name__)

class OvShift(models.Model):
    _name = 'ov.shift'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Shift Category'

    name = fields.Char("Shift")

class OvDays(models.Model):
    _name = 'ov.daysavail'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Days'

    name = fields.Char("Days")

class OvPreferredSites(models.Model):
    _name = 'ov.preferredsite'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Preferred Location'

    name = fields.Char("Site Name")

class OvPrevCompany(models.Model):
    _name = 'ov.prevcompany'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Previous Company'

    name = fields.Char("Name")

AVAILABLE_QUALITY = [
    ('0', 'Poor'),
    ('1', 'Normal'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent')
]

class OvHrRecruitmentExt(models.Model):
    _inherit = 'hr.applicant'
    _order = "date_last_stage_update desc"

    def _get_default_copylink(self):
        return self.get_default_copylink()

    def _default_contact_stage_id(self):
        val = self.env['contact.substage'].search([('name','=','New')])
        return val.id

    appointment_reference = fields.Char("Our Ref.")
    description = fields.Text()
    letter_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    commencement_date = fields.Date(string='Commencement Date')
    partner_name = fields.Char("Name of Candidate")
    salutation = fields.Selection([('mr', 'Mr'),('ms', 'Ms'),('mrs', 'Mrs')], "Salutation", store=True)
    country_id = fields.Many2one("res.country", "Nationality")
    races = fields.Many2one("ov.races", "Races")
    postal_code = fields.Char("Postal Code",default='')
    country_image = fields.Binary(readonly=True, related='country_id.image')
    project_site = fields.Many2one('ov.projectsite', "Project Site Name")
    preferred_location1 = fields.Many2one('ov.preflocation', "Preferred Location 1")
    preferred_location2 = fields.Many2one('ov.preflocation', "Preferred Location 2")
    preferred_location3 = fields.Many2one('ov.preflocation', "Preferred Location 3")
    quality_of_contact = fields.Selection(AVAILABLE_QUALITY, "Quality of Contact", default='0')
    enquiry = fields.Boolean("Enquiry", default=True)
    application = fields.Boolean("Application", default=False)
    iv = fields.Boolean("Interview", default=False)
    contract_proposal = fields.Boolean("Contract Proposal", default=False)
    convert_to_emp = fields.Boolean("Converted to Employee", default=False)
    blacklist = fields.Boolean("Blacklist", default=False)
    blacklist_note = fields.Text()
    nric = fields.Char("NRIC No.")
    mobile_no1 = fields.Char("Mobile No.", size=32)
    mobile_no2 = fields.Char("Mobile No. 2", size=32)
    source_ids = fields.Many2one('ov.source','Source')
    created_by = fields.Many2one('res.users','Created By', default=lambda self: self.env.user)
    owner = fields.Many2one('res.users','Owner', default=lambda self: self.env.user)
    recruiter = fields.Many2one('res.users','Recruiter', default=lambda self: self.env.user)
    job_id = fields.Many2one('hr.job', "Applied Job",required=True)
    parent_id = fields.Many2one('hr.employee', 'Manager')
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
        ],"Deployment Type Preferred")
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
    #previous_working_site = fields.Many2one('ov.projectsite', "Where did you work before this? (Project Sites)")
    reason_leave = fields.Text()
    pay_like = fields.Char("What was the pay like?")
    remarks_on_prev_comp = fields.Text()
    contact_stage = fields.Many2one('contact.substage','Contact Stage',default=_default_contact_stage_id)
    state = fields.Selection([
                    ('enquiry', "Enquiry"),
                    ('application', "Application"),
                    ('interview', "Interview"),
                    ('contract_proposal', "Contract Proposal"),
                    ('converted_to_employee', "Converted to Employee"),
                    ('blacklisted', "Blacklisted"),
                    ], default='enquiry')
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
    contact_comment = fields.Text('Comment')
    interview_comment = fields.Text('Comment')
    #copylinkss = fields.Char(string='Link',default=lambda self: self._get_default_copylink())
    link_url = fields.Char(string='Link')

    _sql_constraints = [('mobile_no1', 'UNIQUE (mobile_no1)',  'Mobile number already registered!')]


    @api.multi
    @api.onchange('shift_id')
    def onchange_shift_id(self):
        for shift in self.shift_id:
            if shift:
                self.shift_time = shift.time

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
        res = super(OvHrRecruitmentExt, self.with_context(mail_create_nolog=True)).create(vals)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        copied_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (res.id, self._name)
        res['link_url'] = copied_url
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
                res = super(OvHrRecruitmentExt, self).write(vals)
        else:
            res = super(OvHrRecruitmentExt, self).write(vals)
        return res

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.onchange('mobile_no1')
    def check_mobile(self):
        id_needed = []
        wt = self.env['hr.applicant']
        id_needed = wt.search([('mobile_no1', '=', self.mobile_no1)])
        #new = wt.browse(id_needed)
        no = self.mobile_no1
        if no:
            if (no == id_needed.mobile_no1):
                return self._warning(_("Mobile number exist"), _("Mobile number already exist. Please use other number."))


    # @api.multi
    # def _default_enquiry(self):
    #     """ Reinsert the applicant into the recruitment pipe in the first stage"""
    #     default_stage_id_enquiry = self.env['hr.recruitment.stage'].search([('name', '=', 'Enquiry')]).id
    #     if (self.enquiry == True):
    #         return self.write({'stage_id': default_stage_id_enquiry})

    @api.multi
    def add_as_application(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage_id_application = self.env['hr.recruitment.stage'].search([('name', '=', 'Application')]).id
        self.write({'application': True,'enquiry': False,'stage_id': default_stage_id_application})

    @api.multi
    def interview_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage_id_interview = self.env['hr.recruitment.stage'].search([('name', '=', 'Interview')]).id
        self.write({'iv': True ,'application': False,'enquiry': False, 'stage_id': default_stage_id_interview})

    @api.multi
    def contract_proposal_stage(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage_id_contract = self.env['hr.recruitment.stage'].search([('name', '=', 'Contract Proposal')]).id
        self.write({'contract_proposal': True,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_contract})

    @api.multi
    def blacklist_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage_id_blacklist = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
        self.write({'blacklist': True,'application': False,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_blacklist})

    @api.multi
    def reset_blacklist_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage_id_blacklist = self.env['hr.recruitment.stage'].search([('name', '=', 'Application')]).id
        self.write({'blacklist': False,'application': True,'enquiry': False, 'stage_id': default_stage_id_blacklist})

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        default_stage_id_employee = self.env['hr.recruitment.stage'].search([('name', '=', 'Converted to Employee')]).id
        self.write({'blacklist': False,'application': False,'iv': False,'contract_proposal': False,'convert_to_emp': True,'stage_id': default_stage_id_employee})
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            else :
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.mobile_no1
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'id': applicant.id,
                    'name': applicant.partner_name or contact_name,
                    'salutation': applicant.salutation or False,
                    'mobile_phone': applicant.mobile_no1 or False,
                    'work_phone': applicant.partner_phone or False,
                    'postal_code': applicant.postal_code or False,
                    'races': applicant.races.id or False,
                    'project_site': applicant.project_site.id or False,
                    'country_id': applicant.country_id.id or False,
                    'nric': applicant.nric or False,
                    'mobile_no2': applicant.mobile_no2 or False,
                    'license': applicant.license or False,
                    'gender': applicant.gender or False,
                    'age': applicant.age or False,
                    'employment_type': applicant.employment_type or False,
                    'shift_preferences': applicant.shift_preferences or False,
                    'no_days_avail': applicant.no_days_avail or False,
                    'no_weekends_avail': applicant.no_weekends_avail or False,
                    'preferred_site': applicant.preferred_site or False,
                    'remarks': applicant.remarks or False,
                    'job_id': applicant.job_id.id,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                copied_url = base_url+'/web#id=%s&action=146&model=%s&view_type=form&menu_id=105' % (employee.id, self._name)
                applicant.write({'link_url': copied_url})
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
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

