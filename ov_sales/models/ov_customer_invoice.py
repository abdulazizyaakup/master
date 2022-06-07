# -*- coding: utf-8 -*-

import json
import re
import uuid
from functools import partial

from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class OvInvoice(models.Model):
    _inherit = 'account.invoice'

    state_of_approval = fields.Selection([
        ('first_level_approved', 'Checked'),
        # ('second_level_approved', 'Approved')
        ], "State of Approval", store=True)
    # created_by = fields.Many2one('res.users', "Created By", track_visibility="onchange")
    first_approver = fields.Many2one('res.users', "Checked By", track_visibility="onchange")
    second_approver = fields.Many2one('res.users', "Approved By", track_visibility="onchange")

    @api.multi
    def action_first_validate_invoice(self):
        self.write({
            'state_of_approval': 'first_level_approved',
            'first_approver' : self.env.uid,
            # 'confirmation_date': fields.Datetime.now()
        })
        return True

    # @api.multi
    # def action_invoice_open(self): # for both vendor bills and customer invoice
    #     # lots of duplicate calls to action_invoice_open, so we remove those already open
    #     to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
    #     if to_open_invoices.filtered(lambda inv: not inv.partner_id):
    #         raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
    #     if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
    #         raise UserError(_("Invoice must be in draft state in order to validate it."))
    #     if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
    #         raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
    #     if to_open_invoices.filtered(lambda inv: not inv.account_id):
    #         raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
    #     self.write({
    #         'second_approver' : self.env.uid,
    #         'state_of_approval': 'second_level_approved',
    #     })
    #     to_open_invoices.action_date_assign()
    #     to_open_invoices.action_move_create()
    #     return to_open_invoices.invoice_validate()