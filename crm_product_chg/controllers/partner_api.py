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


class PartnerAPI(http.Controller):
    @validate_token
    @http.route("/odoo/partner", methods=["POST"], type="http",
                auth="none", csrf=False)
    def create_partner(self, **post):
        # get values from parameters
        # post = request.jsonrequest
        if not post.get('name'):
            return invalid_response({'message': "Compulsory field - Name not found as an identifier",
                                     'status': 401})

        partner_vals = {
            'name': post.get('name'),
            'registration_id': post.get('registration_id', False),
            'bu': post.get('company_name', False),
            'website': post.get('website_link', False),
            'street': post.get('street', False),
            'street2': post.get('street2', False),
            'street3': post.get('street3', False),
            'city': post.get('city', False),
            'zip': post.get('zip', False),
            'phone': post.get('phone', False),
            'mobile': post.get('mobile', False),
            'fax': post.get('fax', False),
            'email': post.get('email', False),
            'epicor_customer_id': post.get('customer_id', False),
            'epicor_customer_num': post.get('customer_code', False),
        }

        if post.get('state'):
            state_id = request.env['res.partner'].get_nearest_state_many2one(
                'res.country.state',
                post.get('state'))
            if state_id:
                partner_vals.update({'state_id': state_id})
            else:
                return invalid_response({'message': "No existing state found!",
                                         'status': 401})

        if post.get('parent_id'):
            parent_id = request.env['res.partner'].search(
                [('customer_code', '=', post.get('parent_id'))])

            if parent_id:
                partner_vals.update({'parent_id': parent_id.id,
                                     'type': 'delivery'})
            else:
                return invalid_response({'message': "Parent partner not found in system!",
                                         'status': 401})

        if post.get('customer_id'):
            partner = request.env['res.partner'].search(
                [('epicor_customer_id', '=', post.get('customer_id'))])
            if partner:
                for p in partner:
                    if(p.epicor_customer_id == post.get('customer_id')):
                        # print("XXXXXX ", post.get('name'))
                        # print("YYYYYY ", p.name)

                        try:
                            p.sudo().write(partner_vals)
                        except Exception as exception:
                            return invalid_response({'message': "Res Partner update failed!",
                                             'details': str(exception),
                                             'status': 401})

                        return valid_response({'message': "Res Partner Successfully Updated",
                                       'status': 200,
                                       'odoo_partner': p.name,
                                       'odoo_id': p.id})
            if not partner:
                try:
                    new_partner = request.env['res.partner'].sudo().create(partner_vals)
                except Exception as exception:
                    return invalid_response({'message': "Res Partner creation failed!",
                                     'details': str(exception),
                                     'status': 401})

                return valid_response({'message': "Res Partner Successfully Created",
                               'status': 200,
                               'odoo_partner': new_partner.name,
                               'odoo_id': new_partner.id})


    @validate_token
    @http.route("/odoo/partner", methods=["PUT"], type="http",
                auth="none", csrf=False)
    def edit_partner(self, **post):
        ResPartner = request.env['res.partner']

        partner_vals = {
            'name': post.get('name', False),
            'street': post.get('street', False),
            'street2': post.get('street2', False),
            'street3': post.get('street3', False),
            'city': post.get('city', False),
            'zip': post.get('zip', False),
            'phone': post.get('phone', False),
            'mobile': post.get('mobile', False),
            'fax': post.get('fax', False),
            'email': post.get('email', False),
            'epicor_customer_id': post.get('customer_id', False),
            #'epicor_customer_num': post.get('customer_code', False),
        }

        if post.get('state'):
            state_id = ResPartner.get_nearest_state_many2one(
                'res.country.state',
                post.get('state'))
            if state_id:
                partner_vals.update({'state_id': state_id})
            else:
                return invalid_response({'message': "No existing state found!",
                                         'status': 401})


        if post.get('parent_id'):
            parent_id = ResPartner.search(
                [('customer_id', '=', post.get('parent_id'))])

            partner_vals.update({'parent_id': parent_id.id,
                                 'type': 'delivery'})

        filtered_partner_vals = dict(filter(lambda elem: elem[1] is not False or elem[0] == 'active', partner_vals.items()))

        if post.get('customer_id'):
            partner = ResPartner.search(
                [('epicor_customer_id', '=', post.get('customer_id'))])
            if partner:
                try:
                    partner.sudo().write(partner_vals)
                except Exception as exception:
                    return invalid_response({'message': "Res Partner update failed!",
                                     'details': str(exception),
                                     'status': 401})

                return valid_response({'message': "Res Partner Successfully Updated",
                               'status': 200,
                               'odoo_partner': partner.name,
                               'odoo_id': partner.id})
