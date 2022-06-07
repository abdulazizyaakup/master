from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder_drymix(models.Model):
    _inherit = "sale.order"

    quot_drymix_notes = fields.Html(default="<p>(a) Unless otherwise stated as Ex-Factory, the prices quoted are inclusive of transport cost (minimum delivery loads: 10MT) to the specific location but exclude unloading charge.</p><p>(b) The prices quoted are excluded prevailing rate of Sales and Service Tax (SST), where applicable.</p><p>(c) Validity: 30 days from the date of the quotation and subject to change in the event of fluctuation in fuel/ transportation costs, raw materials etc.</p><p>(d) Terms of Payment: Cash Term/ Credit Term (30 days/ 60 days), as per approved Credit Facilities. We reserve the right to impose interest charge of 18% per annum on overdue payments.</p>")
    quot_title_drymix = fields.Text(string='Title', default='RE: QUOTATION FOR THE SUPPLY & DELIVER OF STARKEN DRYMIX PRODUCTS TO PROJECTS IN')
    quot_remarks_drymix = fields.Text(string='Remarks', default='We trust that the above offer meets your requirements and we look forward your kind confirmation on our proposed solutions and services. Please do not hesitate to contact the undersigned, should you need further clarifications.')
    quot_cust_addr_drymix = fields.Text(string='Customer Address')
    quot_street_drymix = fields.Char()
    quot_street2_drymix = fields.Char()
    quot_zip_drymix = fields.Char(change_default=True)
    quot_city_drymix = fields.Char()
    quot_state_id_drymix = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=', quot_country_id_drymix)]")
    quot_country_id_drymix = fields.Many2one('res.country', string='Country', ondelete='restrict')
    quot_epicor_street_drymix = fields.Char()
    quot_epicor_street2_drymix = fields.Char()
    quot_epicor_zip_drymix = fields.Char(change_default=True)
    quot_epicor_city_drymix = fields.Char()
    quot_epicor_state_id_drymix = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=', quot_epicor_country_id_drymix)]")
    quot_epicor_country_id_drymix = fields.Many2one('res.country', string='Country', ondelete='restrict')
    # Fikri Add
    attn_mobile = fields.Char(string='Mobile')
    attn_email = fields.Char(string='Email')



    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # self.quot_street_drymix = self.partner_id.street
        # self.quot_street2_drymix = self.partner_id.street2
        # self.quot_zip_drymix = self.partner_id.zip
        # self.quot_city_drymix = self.partner_id.city
        # self.quot_state_id_drymix = self.partner_id.state_id
        # self.quot_country_id_drymix = self.partner_id.country_id
        self.quot_street_drymix = self.partner_id.comp_address
        self.quot_street2_drymix = self.partner_id.town
        self.quot_zip_drymix = self.partner_id.postcode
        self.quot_city_drymix = self.partner_id.city
        self.quot_state_id_drymix = self.partner_id.state_id
        self.quot_country_id_drymix = self.partner_id.country_id
        # res = [self.partner_id.street,
        #        self.partner_id.street2,
        #        self.partner_id.zip,
        #        self.partner_id.state,
        #        self.partner_id.phone,
        #        self.partner_id.email,
        #        self.partner_id.mobile]
        # self.quot_cust_addr_drymix = ', '.join(x for x in res if x)

    @api.onchange('epicor_partner_id')
    def _onchange_epicor_partner_id(self):
        self.quot_epicor_street_drymix = self.epicor_partner_id.street
        self.quot_epicor_street2_drymix = self.epicor_partner_id.street2
        self.quot_epicor_zip_drymix = self.epicor_partner_id.zip
        self.quot_epicor_city_drymix = self.epicor_partner_id.city
        self.quot_epicor_state_id_drymix = self.epicor_partner_id.state_id
        self.quot_epicor_country_id_drymix = self.epicor_partner_id.country_id

    # def _default_delivery_info(self):
    #     _logger.info("outside")
    #     _logger.info(self._context)
    #     if self.company_id.id in [7]:
    #         _logger.info("inside")
    #         return 'hahahahaha'
    #     return super(SaleOrder_drymix, self)._default_delivery_info()
    # @api.model
    # def default_get(self, fields):
    #     res = super(SaleOrder_drymix, self).default_get(fields)
    #     _logger.info("this is note....................")
    #     if self.company_id.id == 7:
    #         res['note'] = 'hahha'
    #     _logger.info(res.get('note'))

    #     return res

# class SaleOrderLine_drymix(models.Model):
#     _inherit = "sale.order.line"
# 
#     product_class = fields.Many2one('starken_crm.product.class', string="Product Class")
