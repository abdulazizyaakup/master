from odoo import models, fields, api

class RegardingItems_gcast(models.Model):
    _name="regarding.items.gcast"
    _description = "Regarding (RE) Items"

    name = fields.Text(string="Regarding(RE) Item")