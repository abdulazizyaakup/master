# See LICENSE file for full copyright and licensing details.

from odoo import models, fields,api,_


class CHGBProduct(models.Model):
    _inherit = "product.product"

    company_code = fields.Char(string="Company Shortcode")

    @api.onchange('company_code')
    def get_company_id(self):
        company = self.env['res.company'].search([])
        if(self.company_code):
            for c in company:
                if(c.shortcode_name == self.company_code):
                    self.company_id.id = c.id

    def get_nearest_many2one(self, class_to_use, newName):
        if newName:
            existing_val = self.env[class_to_use].search([('name','ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False



class CHGBProductTemplate(models.Model):
    _inherit = "product.template"

    company_code = fields.Char(string="Company Shortcode")

    @api.onchange('company_code')
    @api.depends('company_code')
    def get_company_id(self):
        company = self.env['res.company'].search([])
        product = self.env['product.template'].search([])
        
        for p in product:
            if(p.company_code):
                for c in company:
                    if(c.shortcode_name == p.company_code):
                        p.write({'company_id':c.id})

    def get_nearest_many2one(self, class_to_use, newName):
        if newName:
            existing_val = self.env[class_to_use].search([('name','ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False

class CHGBPurchaseOrderSync(models.Model):
    _inherit = 'purchase.order'

    def get_nearest_many2one(self, class_to_use, newName):
        if newName:
            existing_val = self.env[class_to_use].search([('name','ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False


class ResPartnerSync(models.Model):
    _inherit = 'res.partner'

    def get_nearest_many2one(self, class_to_use, newName):
        if newName:
            existing_val = self.env[class_to_use].search([('name','ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False