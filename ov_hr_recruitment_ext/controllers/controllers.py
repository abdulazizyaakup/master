# -*- coding: utf-8 -*-
from odoo import http

# class OvHrRecruitmentExt(http.Controller):
#     @http.route('/ov_hr_recruitment_ext/ov_hr_recruitment_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ov_hr_recruitment_ext/ov_hr_recruitment_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ov_hr_recruitment_ext.listing', {
#             'root': '/ov_hr_recruitment_ext/ov_hr_recruitment_ext',
#             'objects': http.request.env['ov_hr_recruitment_ext.ov_hr_recruitment_ext'].search([]),
#         })

#     @http.route('/ov_hr_recruitment_ext/ov_hr_recruitment_ext/objects/<model("ov_hr_recruitment_ext.ov_hr_recruitment_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ov_hr_recruitment_ext.object', {
#             'object': obj
#         })