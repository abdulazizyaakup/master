from odoo import api, fields, models, tools 

class PartnerType(models.Model):
    _name = 'starken_crm.partner.type'
    _description = "Partner Type"

    name = fields.Char('Partner Type', readonly=False, store=True,copy=True)