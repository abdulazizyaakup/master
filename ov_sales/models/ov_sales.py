# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class OvSales(models.Model):
    _inherit = 'sale.order'

    sale_order_no = fields.Char(string='Sale Order No.', copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('sale.order2'))
    quotation_no = fields.Char(string='Quotation No.', copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('sale.order1'))
    state_of_approval = fields.Selection([
        ('first_level_approved', 'Checked'),
        ('second_level_approved', 'Approved')
        ], "State of Approval", store=True)
    first_approver = fields.Many2one('res.users', "Checked By", track_visibility="onchange")#, default=lambda self: self.env.uid)
    second_approver = fields.Many2one('res.users', "Approved By", track_visibility="onchange")


    @api.multi
    def print_sales_proposal(self):
        sale_proposal = self.env.ref('ov_sales.ov_sales_proposal_form').report_action(self)
        return sale_proposal


    @api.multi
    def _action_confirm(self):
        """ Implementation of additionnal mecanism of Sales Order confirmation.
            This method should be extended when the confirmation should generated
            other documents. In this method, the SO are in 'sale' state (not yet 'done').
        """
        if self.env.context.get('send_email'):
            self.force_quotation_send()

        # create an analytic account if at least an expense product
        if any([expense_policy != 'no' for expense_policy in self.order_line.mapped('product_id.expense_policy')]):
            if not self.analytic_account_id:
                self._create_analytic_account()

        return True

    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'state_of_approval': 'second_level_approved',
            'confirmation_date': fields.Datetime.now(),
            'second_approver' : self.env.uid,
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def action_first_validate(self):
        self.write({
            'state_of_approval': 'first_level_approved',
            'first_approver' : self.env.uid,
            # 'confirmation_date': fields.Datetime.now()
        })
        return True


    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'state_of_approval': False,
            'first_approver': False,
            'second_approver': False,
        })

class OvSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_type = fields.Char("Type")
    shift = fields.Selection([
        ('day', 'Day Shift'),
        ('night', 'Night Shift')
        ], "Shift", store=True)
    shift_time = fields.Selection([
       ('0730h1930h','0730H – 1930H'),
       ('0800h2000h','0800H – 2000H'),
       ('1930h1930h','1930H – 0730H'),
       ('2000h0800h','2000H – 0800H'),
       ], "Time")
    public_holiday = fields.Boolean("Public Holiday", default=True)

    def _warning(self, title, message):
        return {
          'warning': {
            'title': title,
            'message': message,
          },
        }

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = self.get_sale_order_line_multiline_description_sale(product)

        if self.product_custom_attribute_value_ids or self.product_no_variant_attribute_value_ids:
            name += '\n'

        if self.product_custom_attribute_value_ids:
            for product_custom_attribute_value in self.product_custom_attribute_value_ids:
                if product_custom_attribute_value.custom_value and product_custom_attribute_value.custom_value.strip():
                    name += '\n' + product_custom_attribute_value.attribute_value_id.name + ': ' + product_custom_attribute_value.custom_value.strip()

        if self.product_no_variant_attribute_value_ids:
            for no_variant_attribute_value in self.product_no_variant_attribute_value_ids.filtered(
                lambda product_attribute_value: not product_attribute_value.is_custom
            ):
                name += '\n' + no_variant_attribute_value.attribute_id.name + ': ' + no_variant_attribute_value.name

        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        self.product_type = self.product_id.type

        return result

    @api.multi
    @api.onchange('price_unit')
    def _onchange_price_verify_limits(self):
        for line in self:
            if (line.price_unit < line.product_id.minimum_price):
                return self._warning(_("Minimum price for %s is $%s!" % (line.product_id.name,line.product_id.minimum_price)),_("Unit price cannot less than minimum price."))
            elif(line.price_unit > line.product_id.maximum_price):
                return self._warning(_("Maximum price for %s is $%s!" % (line.product_id.name,line.product_id.maximum_price)),_("Unit price cannot be greater than maximum price."))    # @api.multi
