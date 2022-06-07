from odoo import api, fields, models, tools 

class VolumeUOM(models.Model):
    _name = 'starken_crm.volume.uom'
    _description = "Net Volume UOM"

    name = fields.Char('Short Name', required=True, readonly=False, store=True,copy=True)
    default_description = fields.Char('Name', readonly=False, store=True,copy=True)