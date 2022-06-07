# -*- coding: utf-8 -*-
# from odoo import http


# class Drymix-crm(http.Controller):
#     @http.route('/drymix-crm/drymix-crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/drymix-crm/drymix-crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('drymix-crm.listing', {
#             'root': '/drymix-crm/drymix-crm',
#             'objects': http.request.env['drymix-crm.drymix-crm'].search([]),
#         })

#     @http.route('/drymix-crm/drymix-crm/objects/<model("drymix-crm.drymix-crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('drymix-crm.object', {
#             'object': obj
#         })
