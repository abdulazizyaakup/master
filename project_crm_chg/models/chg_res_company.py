# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class ChgResCompany(models.Model):
    _inherit = 'res.company'
    _description = "Inherit res company model"

    shortcode_name = fields.Char("Company Shortcode")

