# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from datetime import datetime, timedelta
from odoo.exceptions import  ValidationError
import re
import requests
import json
from urllib.request import urlopen, Request

class ProjectSiteTeam(models.Model):
    _name = 'projectsite.team'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Team for Each Project Site'

    name = fields.Char(string='Team')
    t_ic = fields.Many2one('hr.employee', string='Team IC')
    p_ic = fields.Many2one('hr.employee', string='Project IC')



class ProjectSite(models.Model):
    _name = 'project.site'
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

    def _default_longitude(self):
        return self.compute_site_longitude()

    def _default_latitude(self):
        return self.compute_site_latitude()

    name = fields.Char(string='Project Name',required=True)
    code = fields.Char(string='Project Code')
    address = fields.Text()
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', store=True)
    city_id = fields.Char(string='City', store=True)
    postcode = fields.Char(string='Postcode')
    sector = fields.Char(string='Sector')
    team = fields.Many2one('projectsite.team', string='Team')
    team_ic = fields.Many2one('hr.employee', string='Team IC')
    project_ic = fields.Many2one('hr.employee', string='Project IC')
    phone_guard = fields.Char(string='Phone(Guard House)')
    phone_client = fields.Char(string='Phone(Client Office)')
    start_date = fields.Date(string='Start Date', index=True, help='Start date for the project site')
    end_date = fields.Date(string='End Date', index=True, help='End date for the project site')
    active = fields.Boolean(default=True, help='The active field allows you to hide the category without removing it.')
    # site_latitude = fields.Float(string='Geo Latitude', digits=(16, 5), compute='_compute_site_latitude', store=True)
    # site_longitude = fields.Float(string='Geo Longitude', digits=(16, 5), compute='_compute_site_longitude', store=True)
    site_latitude = fields.Float(string='Geo Latitude', digits=(16, 12), store=True, default=_default_latitude)
    site_longitude = fields.Float(string='Geo Longitude', digits=(16, 12), store=True, default=_default_longitude)


    @api.depends('postcode')
    def compute_site_latitude(self, search_val=None, return_geom=True, get_addr_details=True, page_num=1):
        site_ids = self.env['project.site'].search([])
        for val1 in site_ids:
            search_val = val1.postcode
            search_name = val1.name
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "N"
            val2 = json.loads(requests.get(url,
                                                   params={'searchVal': search_val,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)
            val3 = val2['results']
            for i in val3:
                val4_name = i['SEARCHVAL']
                val4 = i['LATITUDE']
                if (search_name == val4_name):
                    val1.site_latitude = val4

    @api.depends('postcode')
    def compute_site_longitude(self, search_val=None, return_geom=True, get_addr_details=True, page_num=1):
        site_ids = self.env['project.site'].search([])
        for val1 in site_ids:
            search_val = val1.postcode
            search_name = val1.name
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "N"
            val2 = json.loads(requests.get(url,
                                                   params={'searchVal': search_val,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)
            val3 = val2['results']
            for i in val3:
                val4_name = i['SEARCHVAL']
                val4 = i['LONGITUDE']
                if (search_name == val4_name):
                    val1.site_longitude = val4

    @api.model
    def create(self, vals):
        res = super(ProjectSite, self.with_context(mail_create_nolog=True)).create(vals)
        name = vals.get('name')
        self.env['res.applicant'].create({
            'is_projectsite' : True,
            'name':name,
            'postal_code': vals.get('postcode'),
            'lat': vals.get('site_latitude'),
            'lng': vals.get('site_longitude'),
            'site_ids': res.id,
            })
        return res

    @api.multi
    def create_all(self, vals):
        #res = super(ProjectSite, self.with_context(mail_create_nolog=True)).create(vals)
        val = self.env['project.site'].search([])
        for v in val:
            #name = vals.get('name')
            self.env['res.applicant'].create({
                'is_projectsite' : True,
                'name':v.name,
                'postal_code': v.postcode,
                'lat': v.site_latitude,
                'lng': v.site_longitude,
                'site_ids': v.id,
                })
