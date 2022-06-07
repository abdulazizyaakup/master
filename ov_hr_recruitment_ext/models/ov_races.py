# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class OvRaces(models.Model):
    _name = 'ov.races'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Races'

    name = fields.Char("Race")

class OvSource(models.Model):
    _name = 'ov.source'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Source'

    name = fields.Char("Source")

class OvShiftPreference(models.Model):
    _name = 'ov.shiftpreference'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Shift Preference'

    name = fields.Char("Shift")


