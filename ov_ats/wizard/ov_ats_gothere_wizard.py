# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request
import logging
import requests
import json
from urllib.request import urlopen, Request

logger = logging.getLogger(__name__)

class GoThereWizard(models.TransientModel):
    _name = 'gothere.wizard'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    def _default_postalcode(self):
        return self.env['hr.applicant'].browse(self._context.get('postal_code'))

    call_project_site = fields.Many2one('project.site', "Project Site")
    call_postal_code = fields.Char("Postal Code")
    applicant_id = fields.Many2one('hr.applicant',"Applicant",default=_default_applicant)
    call_site_latitude = fields.Float(string='Site Latitude', digits=(16, 12), store=True)
    call_site_longitude = fields.Float(string='Site Longitude', digits=(16, 12), store=True)
    call_applicant_latitude = fields.Float(string='Applicant Latitude', digits=(16, 12), store=True)
    call_applicant_longitude = fields.Float(string='Applciant Longitude', digits=(16, 12), store=True)


    @api.onchange('call_postal_code')
    def get_applicant_lang_lat(self, return_geom=True, get_addr_details=True, page_num=1):
        #search_val = self.postal_code
        if self.call_postal_code:
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "N"
            val2 = json.loads(requests.get(url, params={'searchVal': self.call_postal_code,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)
            #val3 = val2['results']
            val4 = None
            val5 = None
            for i in val2['results']:
                val4_name = i['SEARCHVAL']
                val4 = i['LATITUDE']
                val5 = i['LONGITUDE']
                
            self.call_applicant_latitude = val4
            self.call_applicant_longitude = val5

    @api.onchange('applicant_id')
    def get_applicant_lang_lat(self):
        applicant = self.applicant_id
        self.call_postal_code = applicant.call_postal_code
        self.call_applicant_latitude = applicant.call_applicant_latitude
        self.call_applicant_longitude = applicant.call_applicant_longitude

    @api.onchange('call_project_site')
    def get_site_lang_lat(self):
        for val in self.call_project_site:
            if val:
                self.call_site_latitude = val.site_latitude
                self.call_site_longitude = val.site_longitude

    @api.multi
    def _address_as_string(self):
        self.ensure_one()
        #addr = self.project_site.postcode
        #return addr;
        addr = []
        if self.call_project_site.postcode:
            addr.append(self.call_project_site.postcode)
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
        if not self.call_postal_code:
            raise UserError(
                _('Missing start address for route map: '
                  'you should set it in your preferences.'))
        start_partner = self.call_postal_code
        if (map_website.route_lat_lon_url and
                hasattr(self, 'partner_latitude') and
                self.partner_latitude and self.partner_longitude and
                start_partner.call_partner_latitude and
                start_partner.call_partner_longitude):
            url = self._prepare_url(  # pragma: no cover
                map_website.route_lat_lon_url, {
                    '{START_LATITUDE}': start_partner.call_partner_latitude,
                    '{START_LONGITUDE}': start_partner.call_partner_longitude,
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
        
    @api.multi
    def set_project_site(self):
        applicant = self.applicant_id
        set_site = self.call_project_site.id
        applicant.write({'call_project_site': set_site})
        applicant.write({'project_site': set_site})
        return {'type': 'ir.actions.act_window_close'}
