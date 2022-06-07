# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class OvAccountPayment(models.Model):
    _inherit = 'account.payment'

    cheque_no = fields.Char("Cheque No.")