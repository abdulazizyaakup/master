from odoo import models, fields,api

class TermsAndCondition_gcast(models.Model):
    _inherit = "sale.order"

    # quot_regarding_gcast = fields.Selection([('supply', 'Quotation For Supply'),
    #                                          ('concrete', 'Deliver Reinforced Concrete Products')],
    #                                         string = "Regarding(RE)")   
    # quot_regarding_gcast = fields.Many2many('regarding.items.gcast', string="Regarding(RE)")      
    quot_regarding_gcast = fields.Text(default="RE: Quotation For")                          
    disable_notes_gcast = fields.Boolean(string='Disable note', default=True)
    # T&Cs

    quot_pricing_gcast = fields.Char(default="Prices quoted are inclusive of transport charge to your site with the assumption of proper accessibility to your site but exclude unloading charge. Price quoted on full load/above quantities given.")
    quot_standard_gcast = fields.Char(default="The items quoted above conforms to the applicable Malaysian Standard as manufactured by G-Cast. In the event where the products do not conform to the stipulated requirements and standard. G-Cast liability will be limited to replacing the goods at our own costs. Please state our Reference No. on your purchase order.")
    quot_product_liability_gcast = fields.Char(default="In the event where the products do not conform to the stipulated requirements and standard. G-Cast liability will be limited to replacing the goods at our own costs. Please state our Reference No. on your purchase order.")
    quot_payment_gcast = fields.Char(default="Payment seven(7) days after invoice date.")
    quot_delivery_gcast= fields.Char(default="To be discussed & agreed upon prior to accepting order.")
    quot_validity_gcast = fields.Char(default="7 days.")
    quot_non_standard_products_gcast= fields.Char(default="Please take note that for all non-standard products ordered, customers are obliged to take delivery for product manufactured. If you fail to do so, G-Cast reserves the right to back-charge for non-delivery.")
    quot_note_gcast= fields.Char(default="Price quoted excludes of SST.")

    quot_tnc_type = fields.Selection([('local', 'Local T&Cs'),
                                    ('oversea', 'Overseas T&Cs')],
                                    default='local',
                                    string = "Terms & Condition Types") 
    quot_remarks_gcast= fields.Html(default="")
    quot_remarks_oversea_gcast= fields.Html(default="<p> 1) - All pipes are based on Ordinary Portland Cement to grade 50/60. </p>")
    quot_monetary_oversea_gcast = fields.Char(String="Monetary")

    @api.onchange('quot_tnc_type')
    def product_quot_tnc_type_change(self):
        for rec in self:
            rec.type = self.quot_tnc_type
            print(rec.type)

class SaleOrderLine_gcast(models.Model):
    _inherit = "sale.order.line"

    product_class = fields.Many2one('starken_crm.product.class', string="Product Class")
    # uom = fields.Char(string='Product Uom')
    ros_item_order = fields.Boolean(string='Full Load', default=False)
    item_order_type =  fields.Selection([('ro', 'R.O.'),
                                        ('full', 'Full Load')],
                                        default='',
                                        string = "Quantity Type") 

    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.name = rec.product_id.name
            rec.product_class = rec.product_id.pro_class.id
            rec.description_sale = rec.product_id.description_sale
            rec.companyID = self.env.company.id

            super(SaleOrderLine_gcast, rec).product_id_change()

    @api.onchange('item_order_type')
    def item_order_type_change(self):
        for rec in self:
            rec.item_order_type = self.item_order_type

class resPartner_gcast(models.Model):
    _inherit = "res.partner"

    signature = fields.Binary(string='Signature')
    


