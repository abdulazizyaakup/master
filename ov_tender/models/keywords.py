# -*- coding: utf-8 -*-
from odoo import api, models, fields
from datetime import datetime, timedelta
from odoo.exceptions import  ValidationError
import re

class OvKeywords(models.Model):
    _name = 'ov.keyword'
    _description = 'Tender Keywords'
    name = fields.Char(string='Keywords', index=True, required=True)
    #color = fields.Integer('Color Index', default=10)
    #active = fields.Boolean(default=True, help="Set active to false to hide the Analytic Tag without removing it.")