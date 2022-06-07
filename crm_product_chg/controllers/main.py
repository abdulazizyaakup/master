# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import base64
import os, json
# import pandas as pd
import lxml
import requests
import time
from multiprocessing import Pool
import werkzeug.exceptions
import werkzeug.urls
import werkzeug.wrappers
import urllib
import logging

from datetime import datetime
from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.http_routing.models.ir_http import slug
from urllib.parse import quote
from urllib.request import urlopen, Request

class CrmMaster(http.Controller):

    def _prepare_master_values(self, master=None, **kwargs):
        values = {
            'user': request.env.user,
            'is_public_user': request.env.user.id == request.website.user_id.id,
            'header': kwargs.get('header', dict()),
            'searches': kwargs.get('searches', dict()),
        }
        if master:
            values['master'] = master
            values['name'] = master.name
            values['keywords'] = master.project_keywords
        elif kwargs.get('master'):
            values['master'] = request.env['master.project'].browse(kwargs.pop('master_id'))

        values.update(kwargs)
        return values

    @http.route('/crm/new', type='http', auth="public", website=True)
    def get_project_master_auth(self, master=None, **kwargs):

        template = "project_crm_chg.register_new_master_project"
        values = values = self._prepare_master_values(master=master)#{'name':kwargs.get('name')}
        master = request.env['master.project'].search([])
        countries = request.env['res.country'].search([])
        if kwargs.get('country_id'):
            country = country.browse(int(kwargs.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']
        

        values.update({
            'master': master,
            'countries':countries,
            # 'salary_expected': applicant.salary_expected,
            # 'pref_location':pref_location,
            # 'name': applicant.name,
            # 'job_id': applicant.job_id,
            # 'mobile_no1': applicant.mobile_no1,
            # 'races': applicant.races.id,
            # 'address': address,
            # 'emergency_address': emergency_address,
            # 'nationalservice': applicant.nationalservice,
            # 'ns_reason': ns_reason,
            # 'illness_yes': illness_yes
        })

        return request.render(template, values)
        # return http.request.render("project_crm_chg.crm_project_masters", {'masters':masters})

    @http.route("/crm/master/<model('master.project'):master>/project/new", auth='public', website=True)
    def master_project_detail(self, master):
        a = master.iv_assessment_ids
        for assess in a:
            if(master.title == assess.interviewer):
                assessment = assess
        return http.request.render("ov_ats.ov_ats_applicants_iv_detail", {'applicant':applicant,'assessment':assessment})


    # @http.route('/crm/master/list', auth='public', website=True)
    # def crm_master(self, **kwargs):
    #     # masters = self._prepare_master_values(master=master)
    #     masters = request.env['master.project'].search([])
    #     return http.request.render("project_crm_chg.crm_project_masters", {'masters':masters})

    # @http.route('/hello/world_3', auth='public', website=True)
    # def test_controller_3(self):
    #     return "<b>Hello, %s</b>" % (request.env.user.name)