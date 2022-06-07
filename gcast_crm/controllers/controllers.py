# -*- coding: utf-8 -*-
# from odoo import http


# class GcastCrm(http.Controller):
#     @http.route('/gcast_crm/gcast_crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gcast_crm/gcast_crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gcast_crm.listing', {
#             'root': '/gcast_crm/gcast_crm',
#             'objects': http.request.env['gcast_crm.gcast_crm'].search([]),
#         })

#     @http.route('/gcast_crm/gcast_crm/objects/<model("gcast_crm.gcast_crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gcast_crm.object', {
#             'object': obj
#         })
