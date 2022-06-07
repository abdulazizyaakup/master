# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat

class OvPartner(models.Model):
    _inherit = 'res.partner'

    customer_no = fields.Char(string='Customer No.', copy=False, readonly=True, index=True)
    vendor_no = fields.Char(string='Vendor No.', copy=False, readonly=True, index=True)
    customer_group = fields.Many2many('partner.group', string="Customer Group",domain="[('partner_type', '=', 'customer')]")
    supplier_group = fields.Many2many('partner.group', string="Supplier Group",domain="[('partner_type', '=', 'supplier')]")
    street3 = fields.Char('')
    fax = fields.Char(string="Fax")
    # @api.depends('customer','supplier')
    # @api.onchange('name')
    # @api.model
    # def write(self, vals):
    #     if(self.customer == True):
    #         vals['customer_no'] = self.env['ir.sequence'].next_by_code('res.partner1')
    #     if(self.supplier == True):
    #         vals['vendor_no'] = self.env['ir.sequence'].next_by_code('res.partner2')
    #     res = super(OvPartner, self).write(vals)
    #     return res

    # @api.depends('customer','supplier')
    # @api.onchange('name')
    # @api.model
    # def set_partner_no(self):
    #     if(self.customer == True):
    #         customer_no = self.env['ir.sequence'].next_by_code('res.partner1')
    #     if(self.supplier == True):
    #         vendor_no = self.env['ir.sequence'].next_by_code('res.partner2')
    #     res = super(OvPartner, self).write({'customer_no':customer_no, 'vendor_no':vendor_no})
    #     return res

    @api.multi
    def write(self, vals):
        if vals.get('active') is False:
            for partner in self:
                if partner.active and partner.user_ids:
                    raise ValidationError(_('You cannot archive a contact linked to an internal user.'))
        # res.partner must only allow to set the company_id of a partner if it
        # is the same as the company of all users that inherit from this partner
        # (this is to allow the code from res_users to write to the partner!) or
        # if setting the company_id to False (this is compatible with any user
        # company)
        if vals.get('website'):
            vals['website'] = self._clean_website(vals['website'])
        if vals.get('parent_id'):
            vals['company_name'] = False
        if vals.get('company_id'):
            company = self.env['res.company'].browse(vals['company_id'])
            for partner in self:
                if partner.user_ids:
                    companies = set(user.company_id for user in partner.user_ids)
                    if len(companies) > 1 or company not in companies:
                        raise UserError(
                            ("The selected company is not compatible with the companies of the related user(s)"))
        tools.image_resize_images(vals, sizes={'image': (1024, None)})

        result = True
        # To write in SUPERUSER on field is_company and avoid access rights problems.
        if 'is_company' in vals and self.user_has_groups('base.group_partner_manager') and not self.env.uid == SUPERUSER_ID:
            result = super(OvPartner, self.sudo()).write({'is_company': vals.get('is_company')})
            del vals['is_company']
        if(self.customer == True):
            vals['customer_no'] = self.env['ir.sequence'].next_by_code('res.partner1')
        if(self.supplier == True):
            vals['vendor_no'] = self.env['ir.sequence'].next_by_code('res.partner2')
        # res = super(OvPartner, self).write(vals)
        # return res
        result = result and super(OvPartner, self).write(vals)
        for partner in self:
            if any(u.has_group('base.group_user') for u in partner.user_ids if u != self.env.user):
                self.env['res.users'].check_access_rights('write')
            partner._fields_sync(vals)
        return result

class OvPartnerGroup(models.Model):
    _name = 'partner.group'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Group'

    name = fields.Char("Name")
    partner_type = fields.Selection([
        ('customer','Customer'),
        ('supplier','Vendor'),
        ], "Type")
    partner_ids = fields.Many2many('res.partner', string="Customer")



