from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.addons.sale_stock.models.sale_order import SaleOrder as OSaleOrder
from datetime import datetime, timezone, timedelta
import re
import json
import requests
import logging

_logger = logging.getLogger(__name__)
PRODUCT_GROUP_ACCESSORIES = 'TOOLS & ACCESSORIES'
PRODUCT_GROUP_PANEL = ['WALL PANEL', 'FLOOR PANEL']

SO_STATES = [
    ('draft', 'Draft'),
    ('tba', 'Pending Approval'),
    ('quotation', 'Quotation'),
    ('sent', 'Quotation Sent'),
    ('convert_so', 'Convert to Sales Order'),
    ('sim_draft', 'SIM Draft'),
    ('sim_pending', 'SIM Pending'),
    ('sim_pending_agm', 'SIM Pending Approval'),
    ('sim_pending_ceo', 'SIM Pending CEO Approval'),
    ('sale', 'Sales Order'),
    ('done', 'Locked'),
    ('cancel', 'Cancelled'),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    TRANSPORT_SEL = [('land', 'Land Transportation')]

    def _default_delivery_info(self):
        return 'To be discussed & agreed upon prior to accepting order'

    def _default_pricing_info(self):
        return 'Price quoted are based on full load (16-18 pallets/delivery) & inclusive of transport charge to your site with assumption of proper accessibility but exclude unloading charge. GST are not included.'

    def _default_quantity_info(self):
        return 'To be advised'

    def _default_odd_size_cutting_info(self):
        return 'Odd size cutting will be charged as 600mm standard size'

    def _default_validity_info(self):
        return '30 days'

    def _default_get_note(self):
        return 'Please take note that STARKEN ACC wall panel / block are sold in pallet form and delivery is based on full load. We hope the above quotation meets your requirement and look for ward for your confirmation.\n' \
               '\nPlease do not hesitate to contact us should you need further clarification.' \
               '\nThank you.'

    delivery_info = fields.Text('Delivery')
    pricing_info = fields.Text('Pricing')
    quantity_info = fields.Text('Quantity')
    odd_size_cutting_info = fields.Text('Odd Size Cutting')
    validity_info = fields.Text('Validity')

    def _get_default_state(self):
        state_ctx = self.env.context.get('set_state', False)
        if state_ctx:
            return state_ctx
        return 'draft'

    state = fields.Selection(SO_STATES, string='Status', readonly=True, copy=False, index=True, tracking=3,
        default=lambda self: self._get_default_state())
    state_quo = fields.Selection(SO_STATES, compute='_set_state')
    fl_name = fields.Char('Our ref', store=False, compute='get_revision_name')
    revision_num = fields.Integer('Revision Num', store=True, default=0)
    is_revised = fields.Boolean('Is revised', store=True, default=False)
    po_number = fields.Char('PO Number')
    ship_via = fields.Selection(TRANSPORT_SEL, 'Ship Via')
    po_attach = fields.Many2many('ir.attachment',
                                 'sale_order_po_attach_ir_attachments_rel',
                                 'so_id', 'attachment_id',
                                 string='PO Attachment')
    prj_sch_attach = fields.Many2many('ir.attachment',
                                      'sale_order_prj_sch_attach_rel',
                                      'so_id', 'attachment_id',
                                      string='Project Schedule')
    quote_to = fields.Many2one('res.partner', 'Quote To', domain="[('parent_id', '=', partner_id), ('type', '=', 'other')]")
    ship_to = fields.Many2one('res.partner', 'Ship To',
                              domain="[('parent_id','=', epicor_partner_id), "
                                     "('type','=','delivery')]")
    need_by_date = fields.Date('Need By Date')

    # Approver Field
    approver_lv1 = fields.Many2one('res.users',
                                   domain=lambda self:
                                   [("groups_id", "=",
                                    self.env.ref("starken-crm."
                                                 "sales_approver_group").id)],
                                   string="Approver")
    approved_by = fields.Many2one('res.users')
    so_approved_lv1_by = fields.Many2one('res.users')
    so_approved_lv2_by = fields.Many2one('res.users')
    so_approved_lv3_by = fields.Many2one('res.users')
    approval_level = fields.Selection([
        ('1', 'Level 1'),
        ('2', 'Level 2'),
        ('3', 'Level 3'),
    ], compute='_get_approval_level')
    approval_required = fields.Boolean('Required Approval', store=False,
                                       compute='_get_approval_requirement')
    attn_to = fields.Char(string='Attention to')
    customer_type = fields.Selection([
        ('project', 'Project'),
        ('retail', 'Retail'),
    ], string='Customer Type')
    delivery_zone = fields.Many2one('delivery.zone')
    sim_no = fields.Char(string='SIM No')
    approved_status = fields.Char('Approval Status', store=False,
                                  compute="_get_approval_status")
    # attn_to = fields.Char(string='Attention to')
    project_id = fields.Char(related='opportunity_id.crm_project_id', readonly=True, index=True)
    project_name = fields.Char(related='opportunity_id.name')
    quo_ref = fields.Many2one('sale.order', string='Quotation Ref')
    so_ref = fields.One2many('sale.order', 'quo_ref', string='Sale Order Ref') # it should be 1 to 1 relationship
    latest_so_ref = fields.Many2one('sale.order', compute='_has_so_ref')
    has_so_ref = fields.Boolean(compute='_has_so_ref')
    sim_status = fields.Selection(SO_STATES, compute='_get_sim_status', string='SIM Status')
    allow_so_approve_lv1 = fields.Boolean(compute='_allow_so_approve_lv1')
    project_quoted_name = fields.Char('Project Quoted Name')

    # Fields for address, due to separation from crm and res.partner
    quote_to_street = fields.Char()
    quote_to_street2 = fields.Char()
    quote_to_street3 = fields.Char()
    quote_to_zip = fields.Char('Zip', change_default=True)
    quote_to_city = fields.Char('City')
    quote_to_state_id = fields.Many2one("res.country.state", string='State')
    quote_to_country_id = fields.Many2one('res.country', string='Country')
    ship_to_street = fields.Char()
    ship_to_street2 = fields.Char()
    ship_to_street3 = fields.Char()
    ship_to_zip = fields.Char('Zip', change_default=True)
    ship_to_city = fields.Char('City')
    ship_to_state_id = fields.Many2one("res.country.state", string='State')
    ship_to_country_id = fields.Many2one('res.country', string='Country')
    epicor_partner_id = fields.Many2one('res.partner', string='Epicor Customer',
                                        domain="['|', '&', ('company_id', '=', False), ('company_id', '=', company_id), ('is_epicor_customer', '=', True), ('customer_rank', '>', 0), ('parent_id', '=', False)]")
    so_no = fields.Char('Epicor SO No', readonly=True)
    related_quo = fields.Many2many('sale.order', 'quo_so_rel', 'quo_id', 'so_id', domain="[('state', 'in', ['draft', 'tba', 'quotation', 'sent', 'convert_so'])]")
    related_so = fields.Many2many('sale.order', 'quo_so_rel', 'so_id', 'quo_id', domain="[('state', 'in', ['sim_draft', 'sim_pending', 'sim_pending_agm', 'sim_pending_ceo', 'sale'])]")

    @api.depends('state')
    def _set_state(self):
        for record in self:
            record.state_quo = record.state

    @api.onchange('quote_to')
    def onchange_quote_to_id(self):
        self.quote_to_street = self.quote_to.street if self.quote_to else ''
        self.quote_to_street2 = self.quote_to.street2 if self.quote_to else ''
        self.quote_to_street3 = self.quote_to.street3 if self.quote_to else ''
        self.quote_to_zip = self.quote_to.zip if self.quote_to else ''
        self.quote_to_city = self.quote_to.city if self.quote_to else ''
        self.quote_to_state_id = self.quote_to.state_id.id \
            if self.quote_to.state_id else False
        self.quote_to_country_id = self.quote_to.country_id.id \
            if self.quote_to.country_id else False

    @api.onchange('ship_to')
    def onchange_ship_to_id(self):
        self.ship_to_street = self.ship_to.street if self.ship_to else ''
        self.ship_to_street2 = self.ship_to.street2 if self.ship_to else ''
        self.ship_to_street3 = self.ship_to.street3 if self.ship_to else ''
        self.ship_to_zip = self.ship_to.zip if self.ship_to else ''
        self.ship_to_city = self.ship_to.city if self.ship_to else ''
        self.ship_to_state_id = self.ship_to.state_id.id \
            if self.ship_to.state_id else False
        self.ship_to_country_id = self.ship_to.country_id.id \
            if self.ship_to.country_id else False

    @api.depends('user_id')
    def _allow_so_approve_lv1(self):
        # only selected salesperson, AGM and CEO can approve
        for record in self:
            allow_approve_lv1 = False
            if record.state in ['sim_pending']:
                if record.user_id.id == self.env.uid:
                    allow_approve_lv1 = True
                if self.env.user.has_group('starken-crm.sales_ceo_approver_group'):
                    allow_approve_lv1 = True
                if self.env.user.has_group('starken-crm.sales_agm_approver_group'):
                    allow_approve_lv1 = True
            record.allow_so_approve_lv1 = allow_approve_lv1

    @api.depends('so_ref')
    def _has_so_ref(self):
        for record in self:
            latest_so_ref = False
            has_so_ref = any([so for so in record.so_ref])
            if has_so_ref:
                latest_so_ref = record.so_ref[0]
            record.latest_so_ref = latest_so_ref
            record.has_so_ref = has_so_ref

    @api.depends('so_ref.state')
    def _get_sim_status(self):
        for record in self:
            sim_status = False
            if record.so_ref:
                sim_status = record.so_ref[0].state
            record.sim_status = sim_status

    def _get_approval_status(self):
        for rec in self:
            if rec.state in ['draft', 'tba', 'cancel']:
                rec.approved_status = "Not Approved"
            elif rec.state in ['quotation', 'sent', 'convert_so']:
                rec.approved_status = "Quotation Approved"
            elif rec.state in ['sim_draft', 'sim_pending']:
                rec.approved_status = "Pending SO Approval"
            elif rec.state in ['sim_pending_agm']:
                rec.approved_status = "Pending AGM Approval"
            elif rec.state in ['sim_pending_ceo']:
                rec.approved_status = "Pending CEO Approval"
            else:
                rec.approved_status = "Approved"

    @api.depends('order_line.approval_lvl')
    def _get_approval_level(self):
        for order in self:
            approval_level = '1'
            for line in order.order_line:
                if int(line.approval_lvl) > int(approval_level):
                    approval_level = line.approval_lvl
            order.approval_level = approval_level

    @api.onchange('user_id')
    def _get_approval_requirement(self):
        for rec in self:
            approval_req = False
            if rec.user_id:
                sout = self.env['sale.order.user.toapprove'].search([
                        ('user_to_approve', '=', rec.user_id.id)], limit=1)
                if sout:
                    approval_req = True
            rec.approval_required = approval_req

    @api.onchange('customer_type', 'delivery_zone')
    def onchange_customer_and_delivery(self):
        self.ensure_one()
        for line in self.order_line:
            line.product_id_change()

    # Wrapper to use for sending notification per sale order object
    def send_notification(self, msg, receiver):
        self.sudo().message_post(subject=msg,
                                 body=msg,
                                 message_type="notification",
                                 subtype="mail.mt_subtype",
                                 partner_ids=[receiver.partner_id.id])

    # Override get name_get to display the revision as well
    def name_get(self):
        res = []
        for order in self:
            name = order.fl_name
            if order.partner_id.name and \
                    self._context.get('sale_show_partner_name'):
                name = '%s - %s' % (name, order.partner_id.name)
            res.append((order.id, name))
        return res

    # Get revision name from name + revision number
    def get_revision_name(self):
        for rec in self:
            if rec.state in ['draft', 'tba', 'quotation', 'sent', 'cancel']:
                if rec.revision_num > 0 and not rec.sim_no:
                    rec.fl_name = rec.name + '-R%d' % rec.revision_num
                else:
                    rec.fl_name = rec.name
            else:
                rec.fl_name = rec.name

    def action_view_so_ref(self):
        view_form = self.env.ref('starken-crm.sale_order_form_extend').id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_form],
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.so_ref.ids[0]
        }

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        res['note'] = self._default_get_note()
        if not self._context.get('so_page'):
            res['delivery_info'] = self._default_delivery_info()
            res['pricing_info'] = self._default_pricing_info()
            res['quantity_info'] = self._default_quantity_info()
            res['odd_size_cutting_info'] = self._default_odd_size_cutting_info()
            res['validity_info'] = self._default_validity_info()
        return res

    # Override create function to do the following
    # - To not give new running number on revision and add revision instead
    @api.model
    def create(self, vals):
        old_name = self.env.context.get('revision_past_name')
        if self.env.context.get('new_revision') and old_name:
            vals['name'] = old_name
            vals['revision_num'] = vals['revision_num'] + 1
            vals['state'] = 'draft'
            vals['is_revised'] = False
        state_ctx = self.env.context.get('set_state')
        if state_ctx:
            vals['state'] = state_ctx

        if self.env.context.get('set_quo_ref'):
            vals['quo_ref'] = self.env.context.get('quotation_ref')
            vals['state'] = 'quotation'
        elif not self.env.context.get('new_revision'):
            current_state = vals.get('state') if vals.get('state', False) else 'draft'
            vals['revision_num'] = 0
            vals['is_revised'] = False
            if current_state in ['draft', 'sent', 'tba', 'quotation']:
                quo_number = self.env['res.partner'].browse(vals['partner_id']).get_next_quo_number()
                vals['name'] = quo_number
            elif current_state in ['sale', 'sim_pending', 'sim_draft']:
                sim_seq = self.env['ir.sequence'].next_by_code('sale.enquiry.sim_draft') or _('New')
                vals['name'] = sim_seq
                vals['sim_no'] = sim_seq
            else:
                vals['name'] = _('New')

        result = super(SaleOrder, self).create(vals)
        if self.env.context.get('set_quo_ref'):
            result.action_confirm()
        return result

    def write(self, vals):
        state_chg_value = vals.get('state', False)
        if state_chg_value:
            if state_chg_value in ['draft']:
                quo_number = self.mapped('partner_id').get_next_quo_number()
                vals['name'] = quo_number
            if state_chg_value in ['sim_pending']:
                if self.sim_no:
                    sim_seq = self.sim_no
                else:
                    sim_seq = self.env['ir.sequence'].next_by_code('sale.enquiry.sim_draft') or _('New')
                    vals['sim_no'] = sim_seq
                vals['name'] = sim_seq

        return super(SaleOrder, self).write(vals)

    def copy(self, default=None):
        self.ensure_one()
        res = super(SaleOrder, self).copy(default)
        if not self._context.get('set_state') and not self._context.get('set_quo_ref'):
            res.sim_no = False
        if not self.env.context.get('set_quo_ref'):
            res.quo_ref = False
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        addr = self.partner_id.address_get(['other'])
        quote_to = addr and addr.get('other')
        if quote_to:
            if self.state in ['draft', 'tba', 'quotation', 'sent', 'convert_so']:
                self.quote_to = quote_to if self.env['res.partner'].browse(quote_to).type == 'other' else False
        self.user_id = self.env.user and self.env.user.id
        payment_term_2months = self.env.ref('account.account_payment_term_2months', False)
        if payment_term_2months:
            self.payment_term_id = payment_term_2months.id

    @api.onchange('epicor_partner_id')
    def onchange_epicor_partner_id(self):
        addr = self.epicor_partner_id.address_get(['delivery'])
        ship_to = addr and addr.get('delivery')
        if ship_to:
            if self.state in ['sim_draft', 'sim_pending', 'sim_pending_agm', 'sim_pending_ceo', 'sale']:
                self.ship_to = ship_to if self.env['res.partner'].browse(ship_to).type == 'delivery' else False

    def action_cancel(self):
        if self.so_ref:
            if self.so_ref[0].state == 'sale':
                raise ValidationError('Cannot cancel quotation which have running Sales Order!')

        return self.write({
            'state': 'cancel',
            'approver_lv1': False,
            'approved_by': False,
            'so_approved_lv1_by': False,
            'so_approved_lv2_by': False,
            'so_approved_lv3_by': False,
        })

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        if self.state in ['quotation', 'sent', 'convert_so']:
            if self._context.get('set_quo_ref') or self.quo_ref:
                self.write({
                    'state': 'sim_pending',
                    'date_order': fields.Datetime.now()
                })
                # self.order_line.set_quoted_price_and_reset_qty()
            else:
                if self.has_so_ref:
                    _logger.warning('Sales Order related to this quotation already exist!')
                else:
                    new_so = self.with_context(set_quo_ref=True, quotation_ref=self.id).copy()
                    self.write({
                        'state': 'convert_so',
                        'related_so': [(4, new_so.id)]
                    })
                    return new_so
        else:
            self.write({
                'state': 'sim_pending',
                'date_order': fields.Datetime.now()
            })

        self._action_confirm()
        return True

    # Action to duplicate by revising instead of duplicate clone
    def action_duplicate_under_new_revision(self):
        if not self.is_revised:
            self.sudo().write({'is_revised': True})
            self.with_context(new_revision=True, revision_past_name=self.name).\
                copy()
            return
        raise ValidationError('This sales order has been revised')

    # Quotation get approval state method
    def get_approval_quotation(self):
        if self.approver_lv1:
            # Set to be approved state and notify user assigned
            self.write({'state': 'tba'})
            message = "%s requires your approval" % self.name
            self.send_notification(message, self.approver_lv1)
        else:
            raise ValidationError('No approver set to approve this quotation')

    # Quotation set approved state method
    def set_approve_quotation(self):
        # Only allow those that were in To be approved state
        if self.state == 'tba':
            # Only approver assigned allowed to approve this quotation
            # check user has group
            if self.env.user.has_group('starken-crm.sales_ceo_approver_group'):
                self.write({'state': 'quotation', 'approved_by': self.env.uid})
                message = "%s has been approved" % self.name
                self.send_notification(message, self.create_uid)
            elif self.env.user.has_group('starken-crm.sales_agm_approver_group'):
                self.write({'state': 'quotation', 'approved_by': self.env.uid})
                message = "%s has been approved" % self.name
                self.send_notification(message, self.create_uid)
            elif self.env.uid == self.approver_lv1.id:
                # Set to approved state and notify user that created the
                # Quotation
                self.write({'state': 'quotation', 'approved_by': self.env.uid})
                message = "%s has been approved" % self.name
                self.send_notification(message, self.create_uid)
            else:
                raise ValidationError('You are not allowed to approve this '
                                      'quotation')
        else:
            raise ValidationError('Current quotation is not to be approved')

    def set_approve_sales_order(self):
        if self.state in ['sim_pending', 'sim_pending_agm', 'sim_pending_ceo']:
            so_approved_field = False
            if self.state == 'sim_pending':
                # Only so_approval assigned or higher approval allowed to approve this quotation
                if self.env.user.has_group('starken-crm.sales_ceo_approver_group'):
                    pass # allow approval
                elif self.env.user.has_group('starken-crm.sales_agm_approver_group'):
                    pass # allow approval
                elif self.env.uid == self.user_id.id:
                    pass # allow approval
                else:
                    raise ValidationError('You are not allowed to approve this '
                                          'sales')
                state = 'sale'
                so_approved_field = 'so_approved_lv1_by'
                message = "%s sale has been approved" % self.name
                # check again if approval lvl is 2 or 3
                if self.approval_level in ['2', '3']:
                    state = 'sim_pending_agm'
                    approval_level = self.env['ir.config_parameter'].sudo().get_param('sales.order.approval_level')
                    if approval_level == 'sales_ceo':
                        state = 'sim_pending_ceo'
            elif self.state == 'sim_pending_agm':
                # Only AGM or CEO allow to approved
                if self.env.user.has_group('starken-crm.sales_ceo_approver_group'):
                    pass # allow approval
                elif self.env.user.has_group('starken-crm.sales_agm_approver_group'):
                    pass # allow approval
                else:
                    raise ValidationError('You are not allowed to approve this '
                                          'sales')
                state = 'sale'
                so_approved_field = 'so_approved_lv2_by'
                message = "%s sale has been approved by AGM" % self.name
                if self.approval_level in ['3']:
                    state = 'sim_pending_ceo'
            elif self.state == 'sim_pending_ceo':
                # Only CEO allow to approved
                if self.env.user.has_group('starken-crm.sales_ceo_approver_group'):
                    pass  # allow approval
                else:
                    raise ValidationError('You are not allowed to approve this '
                                          'sales')
                state = 'sale'
                so_approved_field = 'so_approved_lv3_by'
                message = "%s sale has been approved by CEO" % self.name

            if so_approved_field:
                if state == 'sale':
                #     res = self.insert_so_epicor()
                #     if res['is_success'] == True:
                #         self.send_notification(message, self.create_uid)
                #         self.write({
                #             'state': state,
                #             so_approved_field: self.env.uid,
                #             'so_no': res['orderNum'],
                #         })
                #     else:
                #         raise UserError(_(res['error']))
                # else:
                    self.send_notification(message, self.create_uid)
                    self.write({
                        'state': state,
                        so_approved_field: self.env.uid
                    })
        else:
            raise ValidationError('Current sales is not to be approved')

    def bypass_approval_quotation(self):
        self.write({'state': 'quotation'})

    def action_quotation_sent(self):
        if self.filtered(lambda so: so.state != 'quotation'):
            raise UserError(_('Only orders which are in Quotation stage '
                              'can be marked as sent directly.'))
        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
        self.write({'state': 'sent'})

    # Email quotation send
    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template
            loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'sale.order',
                                             self.ids[0])
        email_from = False
        if self.user_id:
            if self.user_id.partner_id.name and self.user_id.partner_id.email:
                email_from = '"%s" <%s>' % (self.user_id.partner_id.name,
                                            self.user_id.partner_id.email)
        if not email_from:
            if self.env.user.partner_id.name and\
                        self.env.user.partner_id.email:
                email_from = '"%s" <%s>' % (self.env.user.partner_id.name,
                                            self.env.user.partner_id.email)
            else:
                raise ValidationError('No email was set for either user or '
                                      'salesperson')
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_email_from': email_from,
            'default_reply_to': email_from,
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'quotation').with_context(
                tracking_disable=True).write({'state': 'sent'})
            self.env.company.sudo().set_onboarding_step_done(
                'sale_onboarding_sample_quotation_state')
        return super(SaleOrder, self.with_context(
            mail_post_autofollow=True)).message_post(**kwargs)

    # START : Overriding stock module methods

    def stc_m_create(self, vals):
        if 'warehouse_id' not in vals and 'company_id' in vals and \
                vals.get('company_id') != self.env.company.id:
            vals['warehouse_id'] = self.env['stock.warehouse'].\
                search([
                        ('company_id', '=', vals.get('company_id'))
                       ], limit=1).id
        return super(OSaleOrder, self).create(vals)

    def stc_m_write(self, values):
        res = super(OSaleOrder, self).write(values)
        return res

    OSaleOrder.create = stc_m_create
    OSaleOrder.write = stc_m_write

    # ENDS :  Overriding stock module methods

    def generate_progroup(self):
        csid = False
        if self.ship_to:
            csid = self.ship_to.id
        else:
            csid = self.partner_id.id
        return {
            'name': self.fl_name,
            'move_type': self.picking_policy,
            'sale_id': self.id,
            'partner_id': csid,
        }

    def _compute_picking_ids(self):
        for order in self:
            delivery_count = self.env['stock.picking'].search_count([
                                                        ('origin_so',
                                                         '=',
                                                         order.id)])
            order.delivery_count = delivery_count

    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        picktype = self.env['stock.picking.type'].search(
            [('company_id', '=', self.company_id.id),
             ('name', 'ilike', 'Delivery Orders')], limit=1)
        pcgrp = False
        if not self.procurement_group_id:
            pcgrp = self.env['procurement.group'].sudo().create(
                                                    self.generate_progroup())
            self.sudo().write({'procurement_group_id': pcgrp})
        else:
            pcgrp = self.procurement_group_id.id
        csshp = False
        if self.ship_to:
            csshp = self.ship_to.id

        action['domain'] = [('origin_so', '=', self.id)]
        action['context'] = dict(self._context,
                                 default_partner_id=self.partner_id.id,
                                 default_origin_so=self.id,
                                 default_customer_ship_id=csshp,
                                 default_picking_type_id=picktype.id,
                                 default_origin=self.fl_name,
                                 default_shipping_date=self.need_by_date,
                                 )
        return action

    def format_date(self, dt):
        myt = dt
        if type(dt) is datetime:
            myt = dt.astimezone(timezone(timedelta(hours=8)))
        return myt.strftime("%Y-%m-%d")

    def is_valid_email(self, email):
        return bool(re.match(
          "^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$",
          email))

    def get_company_code(self):
        company_code = 'SAAC'
        if self.company_id.epicor_company_code:
            company_code = self.company_id.epicor_company_code
        return company_code

    def get_shipping_address_shiptonum(self):
        if self.ship_to:
            if self.ship_to.ship_to_id:
                return self.ship_to.ship_to_id
        return ""

    def get_project_id(self):
        if self.opportunity_id:
            if self.opportunity_id.crm_project_id:
                return self.opportunity_id.crm_project_id
        return None

    def get_need_by_date(self):
        if self.need_by_date:
            return self.format_date(self.need_by_date)
        if self.expected_date:
            return self.format_date(self.expected_date)
        return ""

    def get_shipping_address_state(self):
        company_code = self.company_id.epicor_company_code
        if self.ship_to and company_code:
            if self.ship_to.parent_id and self.ship_to.ship_to_id:
                if self.ship_to.parent_id.epicor_customer_num:
                    errMsg, rtn_qry = self.env['starken_crm.mssql.query'].sudo()\
                        .get_shipto_address_from_db(
                            self.ship_to.ship_to_id,
                            self.ship_to.parent_id.epicor_customer_num,
                            company_code
                        )
                    if errMsg:
                        raise ValidationError(errMsg)
                    self.write_synced_to_epicor(rtn_qry)
                    return self.ship_to.ship_to_id not in rtn_qry
        return False

    def write_synced_to_epicor(self, shiptonums):
        if self.ship_to.synced_to_epicor:
            # Assign sync to epicor flag on found on Epicor but not on Odoo
            if self.ship_to.ship_to_id in shiptonums:
                self.persistent_synced_to_epicor_write(True)
            # Assign sync to epicor flag on not found on Epicor but in Odoo
            if self.ship_to.ship_to_id not in shiptonums:
                self.persistent_synced_to_epicor_write(False)
        else:
            # Assign sync to epicor flag on found on Epicor but not on Odoo
            if self.ship_to.ship_to_id in shiptonums:
                self.persistent_synced_to_epicor_write(True)

    def persistent_synced_to_epicor_write(self, persist_val):
        self.ship_to.sudo().with_context(ship_sync=True).\
            write({'synced_to_epicor': persist_val})
        self.env.cr.commit()

    def get_shipping_address_dict(self):
        shipping_address_dict = {}
        if self.ship_to:
            ship_to = self.ship_to
            if ship_to.ship_to_id:
                shipping_address_dict['ShipToNum'] = ship_to.ship_to_id
                shipping_address_dict['Name'] = ship_to.name
                shipping_address_dict['Address1'] = ship_to.street or ''
                shipping_address_dict['Address2'] = ship_to.street2 or ''
                shipping_address_dict['Address3'] = ship_to.street3 or ''
                shipping_address_dict['City'] = ship_to.city or ''
                shipping_address_dict['State'] = ship_to.state_id.name or ''
                shipping_address_dict['Zip'] = ship_to.zip or ''
                shipping_address_dict['Contact'] = ship_to.attn or ''
                shipping_address_dict['Fax'] = ship_to.fax or ''
                shipping_address_dict['PhoneNumber'] = ship_to.phone or ''
        return shipping_address_dict

    def get_socreator(self):
        if self.create_uid:
            if self.create_uid.login:
                eml = self.create_uid.login
                if self.is_valid_email(eml):
                    return eml
            if self.create_uid.partner_id:
                if self.create_uid.partner_id.email:
                    eml = self.create_uid.partner_id.email
                    if self.is_valid_email(eml):
                        return eml
        return ""

    def sales_orderline_to_epicor_json(self):
        json_orderline_list = []
        for line in self. order_line.filtered(lambda l: not l.display_type):
            json_ol = {}
            json_ol['partNum'] = line.product_id.part_number
            json_ol['partDescription'] = line.product_id.description_sale
            json_ol['lineComment'] = ''
            json_ol['UOM'] = line.product_uom.name
            json_ol['quantity'] = line.product_uom_qty
            json_ol['unitPrice'] = line.price_unit
            json_ol['discountPercentage'] = line.discount
            json_ol['discountAmount'] = line.disc_amount
            json_orderline_list.append(json_ol)
        return json_orderline_list

    def get_customer_type(self):
        if self.customer_type:
            return self.customer_type
        return ''

    def get_delivery_zone(self):
        if self.delivery_zone:
            return self.delivery_zone.name
        return ''

    def get_delivery_info(self):
        if self.delivery_info:
            return self.delivery_info
        return ''

    def get_odd_size_cutting_info(self):
        if self.odd_size_cutting_info:
            return self.odd_size_cutting_info
        return ''

    def get_pricing_info(self):
        if self.pricing_info:
            return self.pricing_info
        return ''

    def get_quantity_info(self):
        if self.quantity_info:
            return self.quantity_info
        return ''

    def get_quotation_no(self):
        if self.quo_ref:
            return self.quo_ref.name
        return ''

    def insert_so_epicor(self):
        self.ensure_one()
        api_resp = self.EJSON_sales_order_insert(
            self.get_company_code(), #company
            'MfgSys', #Hardcoded Plant
            self.epicor_partner_id.epicor_customer_id if self.epicor_partner_id.epicor_customer_id  else '', #Epicor custID
            self.get_shipping_address_shiptonum(), #shipToNum
            self.get_shipping_address_state(), #OneTimeShipment
            self.get_project_id(), #projectID
            self.sim_no, #SIMSNo
            self.user_id.name, #enterBy
            self.po_number if self.po_number else "", #poNum
            self.format_date(self.date_order), #orderDate
            self.get_need_by_date(), #needByDate
            self.get_need_by_date(), #shipByDate
            self.currency_id.name, #currencyCode
            '', # TODO: orderComment
            None, # TODO: poComment
            self.note, #tNCDescription
            self.get_shipping_address_dict(), #shippingAddress
            self.get_socreator(), #UserCreatorEmail
            self.get_customer_type(), #CustomerType
            self.get_delivery_zone(), #DeliveryZone
            self.get_delivery_info(), #Delivery
            self.get_odd_size_cutting_info(), #OddSizeCutting
            self.get_pricing_info(), #Pricing
            self.get_quantity_info(), #Quantity
            self.get_quotation_no(), #QuotationNo
            self.sales_orderline_to_epicor_json(), #sODetails
        )
        # Rerun ship to address state to set the sync to epicor variable
        self.get_shipping_address_state()
        return api_resp

    def EJSON_sales_order_insert(self,
                                 p_company,
                                 p_plant,
                                 p_cust_id,
                                 p_ship_to_num,
                                 p_onetimeshipment,
                                 p_project_id,
                                 p_sim_no,
                                 p_enterby,
                                 p_po_num,
                                 p_order_date,
                                 p_needby_date,
                                 p_shipby_date,
                                 p_currency_code,
                                 p_order_comment,
                                 p_po_comment,
                                 p_terms_condition,
                                 p_shipping_address,
                                 p_creator_email,
                                 p_customer_type,
                                 p_delivery_zone,
                                 p_delivery_info,
                                 p_odd_size_cutting_info,
                                 p_pricing_info,
                                 p_quantity_info,
                                 p_quotation_no,
                                 p_order_list):
        params = {}
        soheader = {}
        result = {}
        params['company'] = p_company
        params['plant'] = p_plant
        soheader['custID'] = p_cust_id
        soheader['OneTimeShipment'] = p_onetimeshipment
        soheader['projectID'] = p_project_id
        soheader['SIMSNo'] = p_sim_no
        soheader['enterBy'] = p_enterby
        soheader['poNum'] = p_po_num
        soheader['orderDate'] = p_order_date
        soheader['needByDate'] = p_needby_date
        soheader['shipByDate'] = p_shipby_date
        soheader['currencyCode'] = p_currency_code
        soheader['orderComment'] = p_order_comment
        soheader['poComment'] = p_po_comment
        soheader['tNCDescription'] = p_terms_condition
        soheader['UserCreatorEmail'] = p_creator_email
        soheader['CustomerType'] = p_customer_type
        soheader['DeliveryZone'] = p_delivery_zone
        soheader['Delivery'] = p_delivery_info
        soheader['OddSizeCutting'] = p_odd_size_cutting_info
        soheader['Pricing'] = p_pricing_info
        soheader['Quantity'] = p_quantity_info
        soheader['QuotationNo'] = p_quotation_no
        if p_onetimeshipment:
            soheader['shippingAddress'] = p_shipping_address
        else:
            soheader['shipToNum'] = p_ship_to_num

        params['sOHeader'] = soheader
        params['sODetails'] = p_order_list

        url = self.env['ir.config_parameter'].sudo().get_param('api.create.so.url')
        if not url:
            raise ValidationError('Missing Create SO API URL')

        _logger.info('EJSON_sales_order_insert request: ' + json.dumps(params))
        r = requests.post(url, json=params)
        _logger.info('EJSON_sales_order_insert response: ' + r.text)
        if r.status_code != 200:
            result['is_success'] = False
            result['error'] = r.text
            return result
        json_resp = json.loads(r.text)
        if json_resp['isSuccess'] is False:
            result['is_success'] = False
            result['error'] = json_resp['errorMessage']
            return result
        for so_detail_resp in json_resp['sODetailRespond']:
            if so_detail_resp['isSuccess'] is False:
                result['is_success'] = False
                result['error'] = so_detail_resp['errorMessage']
                return result
        result['is_success'] = True
        result['orderNum'] = json_resp['orderNum']
        return result

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    approval_lvl = fields.Selection([
        ('1', 'Level 1'),
        ('2', 'Level 2'),
        ('3', 'Level 3'),
    ], compute='_get_approval_lvl')
    compressive_strength = fields.Char('Compressive Strength')
    part_number = fields.Char('Part Number')
    pro_group = fields.Many2one('starken_crm.product.group', 'Product Group', readonly=False, store=True, copy=True) #
    mtr_sq_per_plt = fields.Float(string='Metre sq./pallet')
    no_pcs_per_plt = fields.Integer(string='No. of pcs/pallet')
    plt_per_dlv = fields.Integer(string='Pallets/delivery')
    quoted_price = fields.Float('Quoted Price', digits='Product Price')
    disc_amount = fields.Float('Discount Amount', digits='Product Price',
                               default=0.0)
    fp_unit_price = fields.Float('Final Unit Price', digits='Product Price',
                                 default=0.0)

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

    def safe_div(self, div1_val, div2_val):
        if div1_val == 0 or div2_val == 0:
            return 0
        return div1_val / div2_val

    def set_quoted_price_and_reset_qty(self):
        for line in self:
            price_unit = line.price_unit
            line.quoted_price = price_unit
            line.price_unit = 0
            line.product_uom_qty = 0

    @api.depends('price_unit')
    def _get_approval_lvl(self):
        for line in self:
            approval_lvl = '1'
            original_price = line._get_original_price()
            sales_person_limit_diff_per = self.env['ir.config_parameter'].\
                sudo().get_param('sales.person.pricedifflimit')
            sales_agm_limit_diff_per = self.env['ir.config_parameter'].sudo().\
                get_param('sales.agm.pricedifflimit')
            sales_ceo_limit_diff_per = self.env['ir.config_parameter'].sudo().\
                get_param('sales.ceo.pricedifflimit')
            approval_level = self.env['ir.config_parameter'].sudo().\
                get_param('sales.order.approval_level') # sales_ceo or sales_agm_ceo
            if not original_price:
                line.approval_lvl = approval_lvl
                continue
            unit_price = line.price_unit
            diff_eff_price = (100 - ((unit_price / original_price) * 100))
            if diff_eff_price <= float(sales_person_limit_diff_per):
                approval_lvl = '1'
            elif diff_eff_price <= float(sales_agm_limit_diff_per):
                approval_lvl = '2'
                if approval_level == 'sales_ceo':
                    approval_lvl = '3'
            elif diff_eff_price <= float(sales_ceo_limit_diff_per):
                approval_lvl = '3'
            else:
                approval_lvl = '3'
            line.approval_lvl = approval_lvl

    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            super(SaleOrderLine, rec).product_id_change()
            rec.get_pricing_policy()

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        for rec in self:
            # CRM-208: Do not calculate the Unit Price from the PriceList
            # super(SaleOrderLine, rec).product_uom_change()
            rec.get_pricing_policy()

    @api.onchange('price_unit')
    def check_max_price(self):
        state = self.order_id.state
        if self.product_id and state not in ['draft', 'tba', 'quotation', 'sent', 'cancel']:
            if self.product_id.max_price_alert:
                max_price = self.product_id.max_price
                if self.price_unit > max_price:
                    warning = {
                        'title': _("Maximum Price Alert"),
                        'message': '%s price is higher than maximum price, please check before proceed' % self.product_id.name
                    }
                    return { 'warning': warning}

    def get_pricing_policy(self):
        product_class = self.product_id.pro_class.name if self.product_id.\
            pro_class else ''
        product_group = self.product_id.pro_group.name if self.product_id.\
            pro_group else ''
        if (product_class == PRODUCT_GROUP_ACCESSORIES or product_group
                == PRODUCT_GROUP_ACCESSORIES):
            self._calculate_price_accessories()
        elif (product_class in PRODUCT_GROUP_PANEL or product_group
              in PRODUCT_GROUP_PANEL):
            self._calculate_price_panel(True)
        else:
            self._calculate_price_block()

    def _calculate_price_block(self):
        # CRM 173 -- Calculate Price of Blocks "600 x 200 x ..." range
        # formula = Selling Price/ 100 X Thickness
        delivery_zone = self.order_id.delivery_zone
        customer_type = self.order_id.customer_type

        if delivery_zone and customer_type:
            if self.product_id and self.product_uom_qty:
                part_number = self.product_id.part_number.lower() if \
                    self.product_id.part_number else ''
                if '-600x200x' in part_number:
                    price_policy = self.env['block.pricing.policy'].search([
                        ('customer_type', '=', customer_type),
                        ('delivery_zone', '=', delivery_zone.id),
                        ('block_type', '=', self.product_id.block_type)
                    ], limit=1)
                    if price_policy:
                        last_x_position = part_number.rfind('x')
                        if last_x_position > 0:
                            thickness = int(part_number[last_x_position + 1:last_x_position + 4])
                            price_unit = price_policy.price / 100 * thickness
                        else:
                            price_unit = price_policy.price
                        self.update({'price_unit': price_unit})

    def _calculate_price_accessories(self):
        # CRM 175 -- Pricing of Accessories by State
        delivery_zone = self.order_id.delivery_zone
        product_id = self.product_id
        if delivery_zone and product_id:
            price_policy = self.env['accessories.pricing.policy'].search([
                ('product_id', '=', product_id.id),
                ('delivery_zone', '=', delivery_zone.id)
            ], limit=1)
            if price_policy:
                self.update({'price_unit': price_policy.price})

    def _calculate_price_panel(self, toupdate=False):
        delivery_zone = self.order_id.delivery_zone
        product_id = self.product_id
        # Setting default prices
        price_to_use = 0.0
        default_pricing = self.env['ir.config_parameter'].\
            sudo().get_param('panelm3price')
        default_global_pricing = self.env['panel.pricing.policy'].search([
            ('product_id', '=', False),
            ('delivery_zone', '=', False)
        ], limit=1)
        if default_global_pricing:
            price_to_use = float(default_global_pricing.price)
        elif default_pricing:
            price_to_use = float(default_pricing)
        else:
            price_to_use = 0.0
        if delivery_zone and product_id:
            price_policy = self.env['panel.pricing.policy'].search([
                ('product_id', '=', product_id.id),
                ('delivery_zone', '=', delivery_zone.id)
            ], limit=1)
            if price_policy:
                price_to_use = price_policy.price
        if price_to_use and product_id.net_vol:
            price_to_use = product_id.net_vol * price_to_use
        else:
            price_to_use = 0.0
        if toupdate:
            self.update({'price_unit': price_to_use})
            return False
        else:
            return price_to_use

    def _get_original_price(self):
        product_class = self.product_id.pro_class.name if self.product_id. \
            pro_class else ''
        product_group = self.product_id.pro_group.name if self.product_id. \
            pro_group else ''
        if (product_class == PRODUCT_GROUP_ACCESSORIES or product_group
                == PRODUCT_GROUP_ACCESSORIES):
            original_price = self._get_price_accessories()
        elif (product_class in PRODUCT_GROUP_PANEL or product_group
              in PRODUCT_GROUP_PANEL):
            original_price = self._calculate_price_panel()
        else:
            original_price = self._get_price_block()
        return original_price

    def _get_price_block(self):
        # CRM 173 -- Calculate Price of Blocks "600 x 200 x ..." range
        # formula = Selling Price/ 100 X Thickness
        delivery_zone = self.order_id.delivery_zone
        customer_type = self.order_id.customer_type
        price_unit = 0.0
        if delivery_zone and customer_type:
            if self.product_id:
                part_number = self.product_id.part_number.lower() if \
                    self.product_id.part_number else ''
                if '-600x200x' in part_number:
                    price_policy = self.env['block.pricing.policy'].search([
                        ('customer_type', '=', customer_type),
                        ('delivery_zone', '=', delivery_zone.id),
                        ('block_type', '=', self.product_id.block_type)
                    ], limit=1)
                    if price_policy:
                        last_x_position = part_number.rfind('x')
                        if last_x_position > 0:
                            thickness = int(part_number[last_x_position+1:last_x_position+4])
                            price_unit = price_policy.price / 100 * thickness
                        else:
                            price_unit = price_policy.price
        return price_unit

    def _get_price_accessories(self):
        price_unit = 0.0
        delivery_zone = self.order_id.delivery_zone
        product_id = self.product_id
        if delivery_zone and product_id:
            price_policy = self.env['accessories.pricing.policy'].search([
                ('product_id', '=', product_id.id),
                ('delivery_zone', '=', delivery_zone.id)
            ], limit=1)
            if price_policy:
                price_unit = price_policy.price
        return price_unit

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        return True

    def get_sale_order_line_multiline_description_sale(self, product):
        if product.description_sale:
            return product.description_sale
        else:
            return product.name