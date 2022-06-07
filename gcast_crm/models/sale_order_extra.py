from odoo import models, fields,api

class SaleOrderExtra_gcast(models.Model):
    _inherit = "sale.order"

    extra_product_lines_gcast = fields.One2many('extra.product.lines.gcast', 'quo_ref', string='Extra Product Lines')

class SaleOrderExtraLines_gcast(models.Model):
    _name = "extra.product.lines.gcast"
    _description = "Extra product gcast"

    product_id = fields.Many2one('product.product', string='Product')
    ros_item = fields.Boolean(string='Full Load', default=False)
    product_qty_1200 = fields.Integer(string='Quantity Nos')
    product_price_1200 = fields.Float(string='1200mm (RM)')
    product_qty_1350 = fields.Integer(string='Quantity Nos')
    product_price_1350= fields.Float(string='1350mm (RM)')
    product_qty_1500 = fields.Integer(string='Quantity Nos')
    product_price_1500 = fields.Float(string='1500mm (RM)')
    product_qty_1800 = fields.Integer(string='Quantity Nos')
    product_price_1800 = fields.Float(string='1800mm (RM)')
    quo_ref = fields.Many2one('sale.order', string='Quotation Ref')

class SaleOrderExtraDesc_gcast(models.Model):
    _inherit = "extra.product.lines.gcast"

    product_desc = fields.Char(string='Product Description')

    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.description_sale = rec.product_id.description_sale
            self.product_desc = rec.description_sale
            # super(SaleOrderExtraDesc_gcast, rec).product_id_change()
            # print(product_desc)





