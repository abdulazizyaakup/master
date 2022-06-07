# -*- coding: utf-8 -*-
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

class WebsiteForm(WebsiteForm):

    def _prepare_applicant_values(self, applicant=None, **kwargs):
        values = {
            'user': request.env.user,
            'is_public_user': request.env.user.id == request.website.user_id.id,
            'header': kwargs.get('header', dict()),
            'searches': kwargs.get('searches', dict()),
        }
        if applicant:
            values['applicant'] = applicant
            values['online_ref_no'] = applicant.online_ref_no
        elif kwargs.get('applicant'):
            values['applicant'] = request.env['hr.applicant'].browse(kwargs.pop('applicant_id'))
        elif kwargs.get('applicant'):
            values['school'] = request.env['edu.back'].browse(kwargs.pop('school_id'))
        elif kwargs.get('applicant'):
            values['language'] = request.env['language.spokenwritten'].browse(kwargs.pop('language_id'))
        elif kwargs.get('dialect'):
            values['dialect'] = request.env['language.dialect'].browse(kwargs.pop('dialect_id'))

        values.update(kwargs)
        return values


    @http.route('/maps', type='http', auth="public", methods=['GET'], website=True, sitemap=False)
    def maps_read(self, **post):
        sites = request.env['project.site'].search([])

        postal = []
        for site in sites:
            postal.append(site.postcode)

        for val in postal:
            url = ('https://developers.onemap.sg/commonapi/search?searchVal=%s&returnGeom=Y&getAddrDetails=Y&pageNum=1' % val)

            r = requests.get(url)
            val = r.json()
        return json.dumps(val)

    @http.route('/ats/applicant', auth='user', website=True)
    def applicant(self):
        applicants = request.env['hr.applicant'].search([])
        return http.request.render("ov_ats.ov_ats_applicants", {'applicants':applicants})

    @http.route('/ats/maps', auth='user', website=True)
    def site_maps(self):
        site_maps = request.env['project.site'].search([])
        for sm in site_maps:
            sm1 = sm.site_latitude
            sm2 = sm.site_longitude
        

        sm3 = "<iframe src='https://tools.onemap.sg/amm/amm.html?&amp;marker=latLng:%s,%s"%(sm1,sm2)
        sm4 = "!colour:red&amp;zoomLevl=7&amp;popupWidth=200&amp;popupHeight=500&amp;design=Default' height='450px' width='100%' scrolling='no' frameborder='0' allowfullscreen='allowfullscreen'></iframe>"
        sm5 = sm3+sm4
        return http.request.render("ov_ats.ov_ats_maps", {'sm1':sm1,'sm2':sm2})

    @http.route("/ats/applicant/<model('hr.applicant'):applicant>/application/details" ,auth='public', website=True)
    def applicant_application_detail(self, applicant):
        return http.request.render("ov_ats.ov_ats_applicants_detail", {'applicant':applicant,'job_id':applicant.job_id})

    @http.route("/ats/applicant/<model('hr.applicant'):applicant>/interview/details", auth='public', website=True)
    def applicant_iv_detail(self, applicant):
        a = applicant.iv_assessment_ids
        for assess in a:
            if(applicant.interviewer == assess.interviewer):
                assessment = assess
        return http.request.render("ov_ats.ov_ats_applicants_iv_detail", {'applicant':applicant,'assessment':assessment})

# Search page
    @http.route('/ats', auth='public', methods=['GET','POST'], website=True)
    def get_applicant_auth(self, **kwargs):

        template = "ov_ats.ov_ats_ref"
        values = {'online_ref_no':kwargs.get('ref')}
        applicant = request.env['hr.applicant'].search([])
        ref = values['online_ref_no']
        applicant_id = None
        for a in applicant:
            if(ref == a.online_ref_no):
                applicant_id = a.id

        if applicant_id:
            url = ('/ats/applicant/%s/application/edit' % applicant_id)
            return werkzeug.utils.redirect("/ats/applicant/%s/application/edit" % applicant_id)

        return request.render(template, values)


    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/application/edit', type='http', auth="public", website=True)
    def applicant_application_edit(self, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant)
        address = applicant.address
        ns_reason = applicant.ns_reason
        emergency_address = applicant.emergency_address
        illness_yes = applicant.illness_yes
        jobs = request.env['hr.job'].search([])
        pref_location = request.env['preferred.location'].search([])
        countries = request.env['res.country'].search([])
        if kwargs.get('country_id'):
            country = country.browse(int(kwargs.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']
        gender = applicant.gender
        val_gender = dict(applicant._fields['gender'].selection).get(gender)

        values.update({
            'applicant': applicant,
            'jobs':jobs,
            'countries':countries,
            'salary_expected': applicant.salary_expected,
            'pref_location':pref_location,
            'name': applicant.name,
            'job_id': applicant.job_id,
            'mobile_no1': applicant.mobile_no1,
            'races': applicant.races.id,
            'address': address,
            'emergency_address': emergency_address,
            'nationalservice': applicant.nationalservice,
            'ns_reason': ns_reason,
            'illness_yes': illness_yes
        })
        template = "ov_ats.edit_applicant_application_form"
        return request.render(template, values)


    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/iv/edit', type='http', auth="user", website=True)
    def applicant_interview_edit(self, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant)
        address = applicant.address

        values.update({
            'applicant': applicant,
            'name': applicant.name,
            'job_id': applicant.job_id,
            'mobile_no1': applicant.mobile_no1,
            'races': applicant.races.id,
            'address': address,
        })

        template = "ov_ats.edit_applicant_interview_form"
        return request.render(template, values)

    # def address_read(self, q='', l=25, **kwargs):
    #     # test = kwargs.get('call_postal_code')
    #     url = ('https://developers.onemap.sg/commonapi/search?')
    #     return_geom = "Y"
    #     get_addr_details = "Y"
    #     page_num = 1
    #     test = kwargs.get('call_postal_code')
    #     value = json.loads(requests.get(url, params={'searchVal': 588996,
    #                                                    'returnGeom': return_geom,
    #                                                    'getAddrDetails': get_addr_details,
    #                                                    'pageNum': page_num}).text)
    #     return json.dumps(value['results'])
    @http.route('/ats/address', type='http', auth="public", methods=['GET'], website=True, sitemap=False)
    def address_read(self, q='', l=25, **kwargs):
        if (len(q) == 6):
            url = ('https://developers.onemap.sg/commonapi/search?')
            return_geom = "Y"
            get_addr_details = "Y"
            page_num = 1
            test = kwargs.get('call_postal_code')
            value = json.loads(requests.get(url, params={'searchVal': q,
                                                           'returnGeom': return_geom,
                                                           'getAddrDetails': get_addr_details,
                                                           'pageNum': page_num}).text)
            return json.dumps(value['results'])

    # def address_read(self, q='', l=25, **kwargs):
    #     with open('/home/aziz/Desktop/PCODE/building.json') as json_file:
    #         data = json.load(json_file)
    #         for a in data:
    #             val = json.dumps(data['value'])
    #     return val


    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/school/<model("edu.back"):school>/save', type='http', auth="user", methods=['POST'], website=True)
    def applicant_school_save(self, applicant, school, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant,school=school)
        if 'name' in kwargs and not kwargs.get('name').strip():
            return request.render('website.http_error', {'status_code': _('Bad Request'), 'status_message': _('Name should not be empty.')})

        vals = {
            'applicant_id':applicant.id,
            'name': kwargs.get('s_name'),
            'hqa': kwargs.get('hqa'),
            'year': kwargs.get('year')
        }
        return vals

    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/school/<model("edu.back"):school>/delete', type='http', auth="user", methods=['POST'], website=True)
    def school_delete(self, school, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant, school=school)
        if (applicant.id == school.applicant_id.id):
            school.unlink()
        return werkzeug.utils.redirect("/ats/applicant/%s/edit" % (slug(applicant)))

    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/language/<model("language.spokenwritten"):language>/delete', type='http', auth="user", methods=['POST'], website=True)
    def language_delete(self, language, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant,language=language)

        if (applicant.id == language.applicant_id.id):
            language.unlink()
        return werkzeug.utils.redirect("/ats/applicant/%s/edit" % (slug(applicant)))

    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/dialect/<model("language.dialect"):dialect>/delete', type='http', auth="user", methods=['POST'], website=True)
    def dialect_delete(self, dialect, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant, dialect=dialect)
        if (applicant.id == dialect.applicant_id.id):
            dialect.unlink()
        return werkzeug.utils.redirect("/ats/applicant/%s/edit" % (slug(applicant)))

    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/careerhistory/<model("career.history"):careerhistory>/delete', type='http', auth="user", methods=['POST'], website=True)
    def career_delete(self, careerhistory, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant, careerhistory=careerhistory)
        if (applicant.id == careerhistory.applicant_id.id):
            careerhistory.unlink()
        return werkzeug.utils.redirect("/ats/applicant/%s/edit" % (slug(applicant)))

    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/relative/<model("friend.relative"):relative>/delete', type='http', auth="user", methods=['POST'], website=True)
    def relative_delete(self, relative, applicant, **kwargs):
        values = self._prepare_applicant_values(applicant=applicant, relative=relative)
        if (applicant.id == relative.applicant_id.id):
            relative.unlink()
        return werkzeug.utils.redirect("/ats/applicant/%s/edit" % (slug(applicant)))


    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/application/save', type='http', auth="public", methods=['POST'], website=True)
    # def ats_applicant_validate(self, **kwargs):
    #     # mode: tuple ('new|edit', 'billing|shipping')
    #     # all_form_values: all values before preprocess
    #     # data: values after preprocess
    #     error = dict()
    #     error_message = []

    #     # email validation
    #     if kwargs.get('email') and not tools.single_email_re.match(kwargs.get('email')):
    #         error["email"] = 'error'
    #         error_message.append(_('Invalid Email! Please enter a valid email address.'))

    #     return error, error_message

    def applicant_application_save(self, applicant, **kwargs):
        if 'name' in kwargs and not kwargs.get('name').strip():
            return request.render('website.http_error', {'status_code': _('Bad Request'), 'status_message': _('Name should not be empty.')})

        val = applicant.school_ids
        sc_id = []
        for v in val:
            sc_id.append(v.id)

        sc = {
            'applicant_id':applicant.id,
            'name': kwargs.get('s_name'),
            'hqa': kwargs.get('s_hqa'),
            'year': kwargs.get('s_year')
        }

        lang = {
            'applicant_id':applicant.id,
            'name': kwargs.get('l_name'),
            'proficiency_spoken': kwargs.get('l_proficiency_spoken'),
            'proficiency_written': kwargs.get('l_proficiency_written')
        }

        dial = {
            'applicant_id':applicant.id,
            'name': kwargs.get('d_name'),
            'proficiency_dialect': kwargs.get('d_proficiency_dialect'),
        }

        career_history = {
            'applicant_id':applicant.id,
            'date_from': kwargs.get('ch_date_from'),
            'date_to': kwargs.get('ch_date_to'),
            'name': kwargs.get('ch_name'),
            'position_held': kwargs.get('ch_position_held'),
            'gross_sal': kwargs.get('ch_gross_sal'),
            'reason_leave': kwargs.get('ch_reason_leave')
        }

        relative = {
            'applicant_id':applicant.id,
            'name': kwargs.get('r_name'),
            'relationship': kwargs.get('r_relationship'),
        }

        address_fw = kwargs.get('address')
        first, *middle, last = address_fw.split()

        vals = {
            'name': kwargs.get('name'),
            'street': kwargs.get('street'),
            'city': kwargs.get('city'),
            'postal_code': last,
            'call_postal_code': last,
            'state_id': kwargs.get('state_id'),
            'country_id': kwargs.get('country_id'),
            'email': kwargs.get('email'),
            'partner_name': kwargs.get('partner_name'),
            'pref_name': kwargs.get('pref_name'),
            'religion': kwargs.get('religion'),
            'address': kwargs.get('address'),
            'unit_no': kwargs.get('unit_no'),
            'level_no': kwargs.get('level_no'),
            'address_status': kwargs.get('address_status'),
            'job_id': kwargs.get('job_id'),
            'preferred_location1': kwargs.get('preferred_location1'),
            'salary_expected': kwargs.get('salary_expected'),
            'country_of_birth': kwargs.get('country_of_birth'),
            'nric': kwargs.get('nric'),
            'age': kwargs.get('age'),
            'date_of_birth': kwargs.get('date_of_birth'),
            'races': kwargs.get('races'),
            'partner_phone': kwargs.get('partner_phone'),
            'mobile_no1': kwargs.get('mobile_no1'),
            'address': kwargs.get('address'),
            'address_status': kwargs.get('address_status'),
            'nationality': kwargs.get('nationality'),
            'gender': kwargs.get('gender'),
            #'driving_license': kwargs.get('driving_license_ids'),
            #'driving_license_other': kwargs.get('driving_license_other'),
            'emergency_name': kwargs.get('emergency_name'),
            'emergency_relation': kwargs.get('emergency_relation'),
            'emergency_phone_no': kwargs.get('emergency_phone_no'),
            'emergency_mobile_no': kwargs.get('emergency_mobile_no'),
            'emergency_address': kwargs.get('emergency_address'),
            'nationalservice' : kwargs.get('nationalservice'),
            'ns_reason': kwargs.get('ns_reason'),
            'rank': kwargs.get('rank'),
            'pes_grading': kwargs.get('pes_grading'),
            'friend_relative': kwargs.get('friend_relative'),
            'update_from_website': True,
            'six_shift_no': kwargs.get('six_shift_no'),
            'illness': kwargs.get('illness'),
            'illness_yes': kwargs.get('illness_yes'),
            'criminal_record': kwargs.get('criminal_record'),
            'cr_yes': kwargs.get('cr_yes'),
            'charged_law': kwargs.get('charged_law'),
            'cl_yes': kwargs.get('cl_yes'),
            'investigation_awareness': kwargs.get('investigation_awareness'),
            'ia_yes': kwargs.get('ia_yes'),
            'financial_embarrassment': kwargs.get('financial_embarrassment'),
            'fe_yes': kwargs.get('fe_yes'),
            'broken_service_period': kwargs.get('broken_service_period'),
            'bsp_yes': kwargs.get('bsp_yes'),
            'currently_serving_bond': kwargs.get('currently_serving_bond'),
            'csb_yes': kwargs.get('csb_yes'),
            'dismissed_from_service': kwargs.get('dismissed_from_service'),
            'dfs_yes': kwargs.get('dfs_yes'),


        }

        dl_ids = request.httprequest.form.getlist('driving_license_ids')
        driving_license_val = {
            'applicant_id':applicant.id,
            'driving_license_ids': [(6, 0, dl_ids)]
        }


        vals_sc = {
            'school_ids': [(0,0, sc)]
        }
        vals_lang = {
            'lang_ids': [(0,0, lang)]
        }
        vals_dial = {
            'dialect_ids': [(0,0, dial)]
        }
        vals_career = {
            'careerhistory_ids': [(0,0, career_history)]
        }
        vals_relatives = {
            'relative_ids': [(0,0, relative)]
        }

        
        val_sc = sc['name']
        val_lang = lang['name']
        val_dial = dial['name']
        val_career_history = career_history['name']
        val_relative = relative['name']

        test_val = {
            'name': kwargs.get('s_name'),
            'hqa': kwargs.get('s_hqa'),
            'year': kwargs.get('s_year')
            }

        # for t in v:
        if(val_sc != None):
            applicant.write(vals_sc)
        if(val_lang != None):
            applicant.write(vals_lang)
        if(val_dial != None):
            applicant.write(vals_dial)
        if(val_career_history != None):
            applicant.write(vals_career)
        if(val_relative != None):
            applicant.write(vals_relatives)
        if dl_ids:
            applicant.write(driving_license_val)

        applicant.write(vals)
        #return request.render(template, vals,headers={'Cache-Control': 'no-cache'})
        return werkzeug.utils.redirect("/ats/applicant/%s/application/details" % (slug(applicant)))


    @http.route('/ats/applicant/<model("hr.applicant"):applicant>/interview/save', type='http', auth="user", methods=['POST'], website=True)
    def applicant_interview_save(self, applicant, **kwargs):
        if 'name' in kwargs and not kwargs.get('name').strip():
            return request.render('website.http_error', {'status_code': _('Bad Request'), 'status_message': _('Name should not be empty.')})

        vals = {
            'partner_name': kwargs.get('partner_name'),
            'nric': kwargs.get('nric'),
            'address': kwargs.get('address'),
            'nationality': kwargs.get('nationality'),
            'age': kwargs.get('age'),
            'area_of_resident': kwargs.get('area_of_resident'),
            'higher_educational_qualification': kwargs.get('higher_educational_qualification'),
            'preferred_shift': kwargs.get('preferred_shift'),
            'preferred_site': kwargs.get('preferred_site'),
            'preferred_site_other': kwargs.get('preferred_site_other'),
            'current_salary': kwargs.get('current_salary'),
            'salary_expected': kwargs.get('salary_expected'),
            'work_experience_year': kwargs.get('work_experience_year'),
            'work_experience_month': kwargs.get('work_experience_month'),
            'current_position_held': kwargs.get('current_position_held'),
            'last_employer': kwargs.get('last_employer'),
            'uniform_size_tshirt': kwargs.get('uniform_size_tshirt'),
            'uniform_size_shirt': kwargs.get('uniform_size_shirt'),
            'job_id': kwargs.get('job_id'),
        }

        n_ids = request.httprequest.form.getlist('negative_char_ids')
        p_ids = request.httprequest.form.getlist('positive_char_ids')
        asf_ids = request.httprequest.form.getlist('preferred_site_suitable_ids')
        psi_ids = request.httprequest.form.getlist('preferred_site_ids')

        negative_char = {
            'applicant_id':applicant.id,
            'negative_char_ids': [(6, 0, n_ids)]
        }

        positive_char = {
            'applicant_id':applicant.id,
            'positive_char_ids': [(6, 0, p_ids)]
        }

        assess_suitable_for = {
            'applicant_id':applicant.id,
            'preferred_site_suitable_ids': [(6, 0, asf_ids)]
        }

        psi = {
            'applicant_id':applicant.id,
            'preferred_site_ids': [(6, 0, psi_ids)]
        }

        iv_assessment_val = {
            'name': kwargs.get('partner_name'),
            'applicant_id': applicant,
            'recommendation': kwargs.get('recommendation'),
            'personal_grooming': kwargs.get('personal_grooming'),
            'personal_expression': kwargs.get('personal_expression'),
            'confidence': kwargs.get('confidence'),
            'maturity': kwargs.get('maturity'),
            'commitment_n_drive': kwargs.get('commitment_n_drive'),
            'communication_skills': kwargs.get('communication_skills'),
            'mental_alertness': kwargs.get('mental_alertness'),
            'knowledge_and_skills': kwargs.get('knowledge_and_skills'),
            'strength_identified': kwargs.get('strength_identified'),
            'possible_weaknesses': kwargs.get('possible_weaknesses'),
            'other_comments': kwargs.get('other_comments'),
            'recommendation_remarks': kwargs.get('recommendation_remarks'),
            'negative_char_ids': [(6, 0, n_ids)],
            'positive_char_ids': [(6, 0, p_ids)],
            'preferred_site_suitable_ids': [(6, 0, asf_ids)],
            'preferred_site_ids': [(6, 0, psi_ids)],
        }

        iv_a = {
            'iv_assessment_ids': [(0, 0, iv_assessment_val)]
        }

        if iv_assessment_val:
            applicant.write(iv_a)


        applicant.write(vals)
        template = "ov_ats.ov_ats_applicants_detail"
        return werkzeug.utils.redirect("/ats/applicant/%s/interview/details" % (slug(applicant)))
