# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class OvPartner(models.Model):
    _inherit = 'stock.picking'

    reference = fields.Char(string='Reference',related='sale_id.client_order_ref')
    delivery_no = fields.Char(string='No.', copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('ov.stock.picking'))



