from odoo import api, fields, models, tools
import logging

_logger = logging.getLogger(__name__)
PRODUCT_GROUP_ACCESSORIES= 'TOOLS & ACCESSORIES'

class CrmLeadProducts(models.Model):
    _name = 'starken_crm.lead.products'
    _description = 'CRM Lead Products'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company.id, index=1)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    crm_id = fields.Many2one('crm.lead', string='Linked Lead')
    crm_partcode = fields.Char('Part Number')
    crm_prdct = fields.Many2one('product.product', string='Products', required=True)
    crm_prdct_size = fields.Char('Product Size', store=True, readonly=True, compute='compute_product_size')
    crm_prdct_qty = fields.Float('Quantity', store=True)
    crm_prdct_vol = fields.Float('Volume', store=True, readonly=True, compute='compute_product_vol')
    crm_prdct_price = fields.Monetary('Sales Price', store=True, currency_field='company_currency')
    crm_cmpt_price = fields.Monetary('Total Price', compute='compute_total_price', currency_field='company_currency', store=True, readonly=True)
    compressive_strength = fields.Char('Compressive Strength')
    mtr_sq_per_plt = fields.Float(string='Metre sq./pallet')
    no_pcs_per_plt = fields.Integer(string='No. of pcs/pallet')
    plt_per_dlv = fields.Integer(string='Pallets/delivery')
    quoted_price = fields.Float('Quoted Price', digits='Product Price')
    disc_amount = fields.Float('Discount Amount', digits='Product Price',
                               default=0.0)
    fp_unit_price = fields.Float('Final Unit Price', digits='Product Price',
                                 default=0.0)
    pro_group = fields.Many2one('product.group',"Product Group")

    @api.onchange('price_unit')
    def change_final_uni_price_on_up_changed(self):
        for line in self:
            line.fp_unit_price = line.price_unit

    @api.onchange('disc_amount')
    def get_disc_amount_changes(self):
        for line in self:
            line.discount = line.safe_div(line.disc_amount,
                                          line.price_unit) * 100
            line.fp_unit_price = line.price_unit - line.disc_amount

    @api.onchange('fp_unit_price')
    def get_disc_fin_amount_changes(self):
        for line in self:
            line.disc_amount = line.price_unit - line.fp_unit_price
            line.discount = line.safe_div(line.disc_amount,
                                          line.price_unit) * 100

    @api.onchange('discount')
    def get_disc_changes(self):
        for line in self:
            line.disc_amount = (line.price_unit * line.discount) / 100
            line.fp_unit_price = line.price_unit - line.disc_amount

    @api.depends('crm_prdct_price','crm_prdct_qty')
    def compute_total_price(self):
        for line in self:
            line.update({
                'crm_cmpt_price': line.crm_prdct_price * line.crm_prdct_qty
            })

    @api.depends('crm_prdct')
    def compute_product_vol(self):
        for line in self:
            line.update({
                'crm_prdct_vol': line.crm_prdct.net_vol,
                'crm_partcode': line.crm_prdct.part_number
            })

    @api.depends('crm_prdct')
    def compute_product_size(self):
        for line in self:
            vals = {'crm_prdct_size' : False}
            if line.crm_prdct.pro_length and line.crm_prdct.pro_width and line.crm_prdct.pro_height:
                vals['crm_prdct_size'] = str(int(line.crm_prdct.pro_length)) + ' x ' + str(int(line.crm_prdct.pro_height)) + ' x ' + str(int(line.crm_prdct.pro_width)) + 'mm'
            line.update(vals)

    @api.onchange('crm_prdct')
    def product_on_change(self):
        self.ensure_one()
        if not self.crm_prdct:
            return
        self.update({
            'crm_prdct_price': self.crm_prdct.list_price
        })
        self.get_pricing_policy()

    def get_pricing_policy(self):
        self._calculate_price_block()

    def _calculate_price_block(self):
        # CRM 173 -- Calculate Price of Blocks "600 x 200 x ..." range
        delivery_zone = self.crm_id.delivery_zone
        customer_type = self.crm_id.customer_type
        if delivery_zone and customer_type:
            if self.crm_prdct:
                part_number = self.crm_prdct.part_number.lower() if self.crm_prdct.part_number else ''
                if '-600x200x' in part_number:
                    price_policy = self.env['block.pricing.policy'].search([
                        ('customer_type', '=', customer_type),
                        ('delivery_zone', '=', delivery_zone.id),
                        ('block_type', '=', self.crm_prdct.block_type)
                    ], limit=1)
                    if price_policy:
                        self.update({'crm_prdct_price': price_policy.price})