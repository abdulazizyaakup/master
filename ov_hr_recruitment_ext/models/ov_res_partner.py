# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class OvResPartner(models.Model):
    _inherit = 'res.partner'

    is_project_site = fields.Boolean(string='Is Project Site?', default=False, help="Check if the contact is a project site")


