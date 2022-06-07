# -*- coding: utf-8 -*-

from odoo import api, fields, models

class OvScanner(models.Model):
    _name = "ov.scanner"

    @api.model
    def my_method(self):
        return {"hello": "scanner"}

    name = fields.Text()
    description = fields.Char(size=20)
# class ov_twain_document_scanner(models.Model):
#     _name = 'ov_twain_document_scanner.ov_twain_document_scanner'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100