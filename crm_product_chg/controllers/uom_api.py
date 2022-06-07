import logging

from odoo import http
from odoo.http import request
from odoo.addons.restful.common import invalid_response, valid_response
from odoo.addons.restful.controllers.main import validate_token
from datetime import datetime
from ast import literal_eval
from odoo.exceptions import UserError
import json


logger = logging.getLogger(__name__)


class UomAPI(http.Controller):
    @validate_token
    @http.route("/odoo/uom", methods=["POST"], type="http",
                auth="none", csrf=False)
    def create_uom(self, **post):
        # get values from parameters
        # post = request.jsonrequest
        if not post.get('name'):
            return invalid_response({'message': "Compulsory field - Name not found as an identifier",
                                     'status': 401})

        # if not post.get('rounding'):
        #     return invalid_response({'message': "Compulsory field - Rounding not found as an identifier",
        #                              'status': 401})


        uom_vals = {
            'name': post.get('name', False),
            'category_id': 1,
            'uom_type': post.get('uom_type', False),
        }

        if post.get('active'):
            if post.get('active') == 'True':
                uom_vals.update({'active': True})
            if post.get('active') == 'False':
                uom_vals.update({'active': False})

        # if post.get('factor_inv'):
        #     uom_vals.update({'factor_inv': post.get('factor_inv')})
        # if post.get('rounding'):
        #     uom_vals.update({'rounding': post.get('rounding')})

        try:
            new_uom = request.env['uom.uom'].sudo().create(uom_vals)
        except Exception as exception:
            return invalid_response({'message': "Uom creation failed!",
                                     'details': str(exception),
                                     'status': 401})

        return valid_response({'message': "Uom Successfully Created",
                               'status': 200,
                               'odoo_partner': new_uom.name})

    @validate_token
    @http.route("/odoo/uom", methods=["PUT"], type="http",
                auth="none", csrf=False)
    def edit_uom(self, **post):
        Uom = request.env['uom.uom']
        existing_uom = Uom.search([('name', '=', post.get('name')), '|', ('active', '=', True), ('active', '=', False)])

        if not existing_uom:
            return invalid_response({
                'message': "Uom Record Not Found! Please check in Odoo System",
                'status': 401})

        uom_vals = {
            'name': post.get('name', False),
            'category_id': 1,
            'uom_type': post.get('uom_type', False),
            'rounding': post.get('rounding', False),
        }

        if post.get('active'):
            if post.get('active') == 'True':
                uom_vals.update({'active': True})
            if post.get('active') == 'False':
                uom_vals.update({'active': False})

        filtered_uom_vals = dict(filter(lambda elem: elem[1] is not False and elem[0] == 'active', uom_vals.items()))

        existing_uom.write(filtered_uom_vals)

        return valid_response({'message': "Uom Update Sucessfully",
                               'status': 200})
