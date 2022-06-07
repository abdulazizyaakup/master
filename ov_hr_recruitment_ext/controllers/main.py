# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class HrApplicant(http.Controller):

    @http.route(['/hello', '/world_1'], auth='user')
    def test_controller_1(self):
        return "Hello World"

    @http.route('/hello/world_3', auth='public', website=True)
    def test_controller_3(self):
        return "<b>Hello, %s</b>" % (request.env.user.name)

    @http.route('/name/', auth='public', website=True)
    def test_name(self):
        return http.request.render('ov_hr_recruitment_ext.my_template', {
           'user': request.env.user
        })

    @http.route('/simple_page', auth='user', website=True)
    def simple_page(self):
        return request.website.render("ov_hr_recruitment_ext.simple_page", {})

    @http.route('/dynamic_page', auth='user', website=True)
    def dynamic_page(self):
        return request.website.render("ov_hr_recruitment_ext.dynamic_page", {'user':request.env.user})

    @http.route('/applicant', auth='public', website=True)
    def applicants(self):
        applicants = request.env['hr.applicant'].search([])
        return http.request.render("ov_hr_recruitment_ext.hr_applicant_website", {'applicants':applicants})

    @http.route("/applicant/<model('hr.applicant'):applicant>", methods=['GET', 'POST'], auth='public', website=True)
    def applicant_detail(self, applicant,**kw):
        hr_applicant = request.env['hr.applicant'].with_context().sudo()
        applicant_id = applicant.id
        mode = (False, False)

        #     return request.redirect('/edit_form')
        # print("xxxxxxxx ", applicant_id)
        render_values = {
            'applicant': applicant,
            'job_id': applicant.job_id.name,
        }
        return request.render("ov_hr_recruitment_ext.hr_applicant_detail", render_values)
        #return http.request.render("ov_hr_recruitment_ext.hr_applicant_detail", {'applicant':applicant})

    @http.route("/applicant/form/<model('hr.applicant'):applicant>", methods=['GET', 'POST'], auth='public', website=True)
    def applicant_form(self,applicant, **kw):
        hr_applicant = request.env['hr.applicant'].with_context().sudo()
        mode = (False, False)
        request.render("ov_hr_recruitment_ext.hr_applicant_form", render_values)
        if 'post_values' in kw:
            values = {}
            for field_name, field_value in kw.items():
                if field_name in request.env['hr.applicant']._fields and field_name.startswith('x_'):
                    values[field_name] = field_value
            if values:
                order.write(values)
        #return request.render("ov_hr_recruitment_ext.hr_applicant_form", render_values)