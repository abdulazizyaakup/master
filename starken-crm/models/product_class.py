from odoo import fields, models


class ProductClass(models.Model):
    _name = 'starken_crm.product.class'
    _description = "Product Class"

    name = fields.Char('Short Name', required=True, readonly=False, store=True,
                       copy=True)
    full_name = fields.Char('Name', readonly=False, store=True, copy=True)

    def get_nearest_many2one(self, class_to_use, newName):
        if newName:
            existing_val = self.env[class_to_use].search([('name','ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False
