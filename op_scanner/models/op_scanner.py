# -*- coding: utf-8 -*-
from odoo import api, fields, models

class op_scanner(models.Model):
    _name = "twain.scanner"

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for attachment in self:
            if attachment.res_model and attachment.res_id:
                record = self.env[attachment.res_model].browse(attachment.res_id)
                attachment.res_name = record.display_name

    @api.depends('res_model')
    def _compute_res_model_name(self):
        for record in self:
            if record.res_model:
                model = self.env['ir.model'].search([('model', '=', record.res_model)], limit=1)
                if model:
                    record.res_model_name = model[0].name


    name = fields.Char("Name")
    description = fields.Char(size=20)
    res_name = fields.Char('Resource Name', compute='_compute_res_name', store=True)
    res_model = fields.Char('Resource Model', readonly=True, help="The database object this attachment will be attached to.")
    res_model_name = fields.Char(compute='_compute_res_model_name', store=True, index=True)
    res_field = fields.Char('Resource Field', readonly=True)
    res_id = fields.Integer('Resource ID', readonly=True, help="The record id this is attached to.")

# class product(models.Model):
#     _inherit = "product.product"

#     max_quantity = fields.Float(string="Maximum Quantity")
class op_scanner2(models.Model):
    _name = "op.scanner"