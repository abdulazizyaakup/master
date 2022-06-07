# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class OvPurchase(models.Model):
    _inherit = 'purchase.order'

    purchase_order_no = fields.Char(string='Purchase Order No.', copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('purchase.order2'))
    rfq_no = fields.Char(string='RFQ No.', copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('purchase.order1'))
    first_approver = fields.Many2one('res.users', "First Approver", track_visibility="onchange")#, default=lambda self: self.env.uid)
    second_approver = fields.Many2one('res.users', "Second Approver", track_visibility="onchange")

