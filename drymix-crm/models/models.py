# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class drymix-crm(models.Model):
#     _name = 'drymix-crm.drymix-crm'
#     _description = 'drymix-crm.drymix-crm'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
