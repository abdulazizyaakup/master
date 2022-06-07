from odoo import models, fields


class BlockPricingPolicy(models.Model):
    _name = 'block.pricing.policy'

    name = fields.Char('Block Pricing Policy')
    delivery_zone = fields.Many2one('delivery.zone')
    customer_type = fields.Selection([
        ('project', 'Project'),
        ('retail', 'Retail'),
    ], string='Customer Type')
    block_type = fields.Selection([
        ('S3', 'S3'),
        ('S5', 'S5'),
        ('S7', 'S7'),
    ])
    price = fields.Float()

    _sql_constraints = [
        ('delivery_customer_block_unique', 'unique (delivery_zone, '
         'customer_type, block_type)',
         'Combination delivery zone, customer type and '
         'block type must be unique!'),
    ]


class AccessoriesPricingPolicy(models.Model):
    _name = 'accessories.pricing.policy'

    name = fields.Char(string='Accessories Pricing Policy')
    delivery_zone = fields.Many2one('delivery.zone')
    product_id = fields.Many2one('product.template', string='Product Acc',
                                 domain="['|', ('pro_class', '='"
                                        ", 'TOOLS & ACCESSORIES'), "
                                        "('pro_group', '=', "
                                        "'TOOLS & ACCESSORIES')]")
    price = fields.Float()

    _sql_constraints = [
        ('delivery_product_unique', 'unique (delivery_zone, product_id)',
         'Combination delivery zone and product id must be unique!'),
    ]


class DeliveryZone(models.Model):
    _name = 'delivery.zone'

    name = fields.Char('Delivery Zone')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Delivery zone already exists!'),
    ]


class PanelPricingPolicy(models.Model):
    _name = 'panel.pricing.policy'

    name = fields.Char(string='Panel Pricing Policy')
    delivery_zone = fields.Many2one('delivery.zone')
    product_id = fields.Many2one('product.template', string='Product Acc',
                                 domain="['|', '|', '|', "
                                        "('pro_class', '=', 'FLOOR PANEL'), "
                                        "('pro_group', '=', 'FLOOR PANEL'), "
                                        "('pro_class', '=', 'WALL PANEL'), "
                                        "('pro_group', '=', 'WALL PANEL')]")
    price = fields.Float('Price')
    is_default = fields.Boolean('Is Default')

    _sql_constraints = [
        ('delivery_product_unique', 'unique (delivery_zone, product_id)',
         'Combination delivery zone and product id must be unique!'),
    ]
