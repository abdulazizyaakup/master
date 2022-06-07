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


class ProductAPI(http.Controller):
    @validate_token
    @http.route("/odoo/product", methods=["POST"], type="http",
                auth="none", csrf=False)
    def create_product(self, **post):
        # get values from parameters
        # post = request.jsonrequest
        if not post.get('name'):
            return invalid_response({'message': "Compulsory field - Name not found as an identifier",
                                     'status': 401})

        uom_id = request.env['purchase.order'].get_nearest_many2one(
            'uom.uom', post.get('uom'))
        po_uom_id = request.env['purchase.order'].get_nearest_many2one(
            'uom.uom', post.get('po_uom'))
        pro_group = request.env['purchase.order'].get_nearest_many2one(
            'starken_crm.product.group', post.get('pro_group'))
        if not uom_id:
            return invalid_response({'message': "UOM Record Not Found! Please check in Odoo System",
                                     'status': 401})
        if not po_uom_id:
            return invalid_response({'message': "PO UOM Record Not Found! Please check in Odoo System",
                                     'status': 401})
        if not pro_group:
            return invalid_response({'message': "Product Group Record Not Found! Please check in Odoo System",
                                     'status': 401})

        # dropship = False
        # if post.get('dropship_item'):
        #     if post.get('dropship_item') == 'True':
        #         dropship = True

        product_vals = {
            'name': post.get('part_number'),
            'default_code': post.get('default_code', False),
            'part_number': post.get('part_number', False),
            # 'dropship_item': dropship,
            'uom_id': uom_id,
            'list_price': post.get('list_price', False),
            'uom_po_id': po_uom_id,
            'description_sale': post.get('description_sale', False),
            'pro_group': pro_group,
            'type': 'product',
            'company_code': post.get('company_code',False)
        }

        if post.get('part_number'):
            product = request.env['product.template'].search(
                [('part_number', '=', post.get('part_number'))])
            if product:
                for p in product:
                    if(p.part_number == post.get('part_number')):
                        try:
                            p.sudo().write(product_vals)
                        except Exception as exception:
                            return invalid_response({'message': "Product update failed!",
                                             'details': str(exception),
                                             'status': 401})

                        return valid_response({'message': "Product Successfully Updated",
                                       'status': 200,
                                       'odoo_partner': p.name,
                                       'odoo_id': p.id})

            if not product:
                try:
                    new_product = request.env['product.template'].sudo().create(product_vals)
                except Exception as exception:
                    return invalid_response({'message': "Product creation failed!",
                                             'details': str(exception),
                                             'status': 401})

                return valid_response({'message': "Product Successfully Created",
                                       'status': 200,
                                       'odoo_partner': new_product.name})

    @validate_token
    @http.route("/odoo/product", methods=["PUT"], type="http",
                auth="none", csrf=False)
    def edit_product(self, **post):
        Product = request.env['product.template']
        existing_product = Product.search([('part_number', '=', post.get('part_number'))])

        if not existing_product:
            return invalid_response({
                'message': "Product Record Not Found! Please check in Odoo System",
                'status': 401})

        uom_id = False
        po_uom_id = False
        pro_group = False
        if post.get('uom'):
            uom_id = request.env['purchase.order'].get_nearest_many2one(
                'uom.uom', post.get('uom'))
            if not uom_id:
                return invalid_response({'message': "UOM Record Not Found! Please check in Odoo System",
                                         'status': 401})

        if post.get('po_uom'):
            po_uom_id = request.env['purchase.order'].get_nearest_many2one(
                'uom.uom', post.get('po_uom'))
            if not po_uom_id:
                return invalid_response({'message': "PO UOM Record Not Found! Please check in Odoo System",
                                         'status': 401})

        if post.get('pro_group'):
            pro_group = request.env['purchase.order'].get_nearest_many2one(
                'starken_crm.product.group', post.get('pro_group'))
            if not pro_group:
                return invalid_response({'message': "Product Group Record Not Found! Please check in Odoo System",
                                         'status': 401})

        product_vals = {
            'name': post.get('part_number', False),
            'default_code': post.get('default_code', False),
            'part_number': post.get('part_number', False),
            'list_price': post.get('list_price', False),
            # 'dropship_item': post.get('dropship_item', False),
            'uom_id': uom_id if uom_id else False,
            'uom_po_id': po_uom_id if po_uom_id else False,
            'description_sale': post.get('description_sale', False),
            'pro_group': pro_group if pro_group else False,
            'type': 'product',
        }

        # if post.get('dropship_item'):
        #     if post.get('dropship_item') == 'True':
        #         dropship = True
        #         product_vals.update({'dropship_item': dropship})
        #     if post.get('dropship_item') == 'False':
        #         dropship = False
        #         product_vals.update({'dropship_item': dropship})

        filtered_product_vals = dict(filter(lambda elem: elem[1] is not False, product_vals.items()))

        existing_product.write(filtered_product_vals)

        return valid_response({'message': "Product Update Sucessfully",
                               'status': 200})
