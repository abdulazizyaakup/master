# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class OvPartner(models.Model):
    _inherit = 'res.partner'

    partner_no = fields.Char("Customer No.")

