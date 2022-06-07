# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from datetime import datetime, timedelta
from odoo.exceptions import  ValidationError
import re

class OvProjectSiteTeam(models.Model):
    _name = 'ov.projectsiteteam'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Team for Each Project Site'

    name = fields.Char(string='Team')
    t_ic = fields.Many2one('hr.employee', string='Team IC')
    p_ic = fields.Many2one('hr.employee', string='Project IC')



class OvProjectSite(models.Model):
    _name = 'ov.projectsite'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'List of Project Site for Deployment'

    @api.constrains('phone_guard')
    def validate_phone_guard(self):
        for obj in self:
            try:
                obj = int(obj.phone_guard)
            except ValueError:
                raise ValidationError("%s contain non-number value!" % obj.phone_guard)

    @api.constrains('code')
    def validate_code(self):
        for obj in self:
            if len(obj.code) > 8:
                raise ValidationError("Project Code should be less or equal to 4 characters.!")

    name = fields.Char(string='Project Name',required=True)
    code = fields.Char(string='Project Code')
    address = fields.Text()
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', store=True)
    city_id = fields.Char(string='City', store=True)
    postcode = fields.Char(string='Postcode')
    sector = fields.Char(string='Sector')
    team = fields.Many2one('ov.projectsiteteam', string='Team')
    team_ic = fields.Many2one('hr.employee', string='Team IC')
    project_ic = fields.Many2one('hr.employee', string='Project IC')
    phone_guard = fields.Char(string='Phone(Guard House)')
    phone_client = fields.Char(string='Phone(Client Office)')
    start_date = fields.Date(string='Start Date', index=True, help='Start date for the project site')
    end_date = fields.Date(string='End Date', index=True, help='End date for the project site')
    active = fields.Boolean(default=True, help='The active field allows you to hide the category without removing it.')
    #latitude = fields.Integer(string='Latitude')
    #longitude = fields.Integer(string='Longitude')

class OvPrefLocation(models.Model):
    _name = 'ov.preflocation'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Preferred Location for Applicant'

    name = fields.Char(string='Location')

    