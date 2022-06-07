# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

ad
class HrApplicant(http.Controller):

    @http.route(['/hello', '/world_1'], auth='user')
    def test_controller_1(self):
        return "Hello World"

    @http.route('/hello/world_3', auth='public', website=True)
    def test_controller_3(self):
        return "<b>Hello, %s</b>" % (request.env.user.name)

    # @http.route('/name/', auth='public', website=True)
    # def test_name(self):
    #     return http.request.render('ov_hr_recruitment.my_template', {
    #        'user': request.env.user
    #     })

    # @http.route('/simple_page', auth='user', website=True)
    # def simple_page(self):
    #     return request.website.render("openacademy.simple_page", {})

    # @http.route('/dynamic_page', auth='user', website=True)
    # def dynamic_page(self):
    #     return request.website.render("openacademy.dynamic_page", {'user':request.env.user})

    @http.route('/hr/applicant', auth='user', website=True)
    def applicants(self):
        applicants = request.env['hr.applicant'].search([])
        return http.request.render("ov_hr_recruiment_ext.hr_applicant", {'applicants':applicants})

    @http.route("/hr/applicant/<model('hr.applicant'):applicant>", auth='user', website=True)
    def applicant_detail(self, applicant):
        return http.request.render("ov_hr_recruiment_ext.hr_applicant_courses_detail", {'applicant':applicant})