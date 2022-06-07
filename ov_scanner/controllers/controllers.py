# -*- coding: utf-8 -*-
from odoo import http

class GoThere(http.Controller):

    @http.route('/ov_gothere/static/src/xml/ov_gothere.xml', cors='*', type='http', auth='none')
    def index(self, **kw):
        return "Hello, world"

# class MyController(odoo.http.Controller):
#     @route('/some_url', auth='public')
#     def handler(self):
#         return stuff()

# class OvTwainDocumentScanner(http.Controller):
#     @http.route('/ov_twain_document_scanner/ov_twain_document_scanner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ov_twain_document_scanner/ov_twain_document_scanner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ov_twain_document_scanner.listing', {
#             'root': '/ov_twain_document_scanner/ov_twain_document_scanner',
#             'objects': http.request.env['ov_twain_document_scanner.ov_twain_document_scanner'].search([]),
#         })

#     @http.route('/ov_twain_document_scanner/ov_twain_document_scanner/objects/<model("ov_twain_document_scanner.ov_twain_document_scanner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ov_twain_document_scanner.object', {
#             'object': obj
#         })