# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError

class OvProduct(models.Model):
    _inherit = 'product.product'

    product_no = fields.Char('Product Code', default=lambda self: self.env['ir.sequence'].next_by_code('product.product'),
        copy=False)
    maximum_price = fields.Float("Maximum Price")
    minimum_price = fields.Float("Minimum Price")

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.multi
    @api.onchange('lst_price')
    def _check_sale_price(self):
        if self.id:
            val = self.lst_price
            min_price = format(self.minimum_price,'.2f')
            max_price = format(self.maximum_price,'.2f')
            if((val > self.maximum_price) or (val < self.minimum_price)):
                return self._warning(_("Sale price should be between $%s - $%s!" % (min_price,max_price)), _("Please insert new Sale Price."))


class OvProductTemplate(models.Model):
    _inherit = 'product.template'

    product_no = fields.Char('Product Code', default=lambda self: self.env['ir.sequence'].next_by_code('product.product'),
        copy=False)
    maximum_price = fields.Float("Maximum Price")
    minimum_price = fields.Float("Minimum Price")

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.multi
    @api.onchange('list_price')
    def _check_sale_price(self):
        if self.id:
            val = self.list_price
            min_price = format(self.minimum_price,'.2f')
            max_price = format(self.maximum_price,'.2f')
            if((val > self.maximum_price) or (val < self.minimum_price)):
                return self._warning(_("Sale price should be between $%s - $%s!" % (min_price,max_price)), _("Please insert new Sale Price."))

    @api.constrains('list_price')
    def _check_save_price(self):
        if self.id:
            val = self.list_price
            min_price = format(self.minimum_price,'.2f')
            max_price = format(self.maximum_price,'.2f')
            if((val > self.maximum_price) or (val < self.minimum_price)):
                raise UserError(_("The price should be between $%s - $%s" % (min_price,max_price)))