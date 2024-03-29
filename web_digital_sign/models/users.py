# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Users(models.Model):
    _inherit = "res.users"

    digital_signature = fields.Binary(string="Signature")


class Partner(models.Model):
    _inherit = "res.partner"

    digital_signature = fields.Binary(string="Signature")
