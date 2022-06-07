from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, Warning


class ResCompany(models.Model):
    _inherit = 'res.company'

    business_unit_code = fields.Char(string='Business Unit Code')
    epicor_company_code = fields.Char(string='Epicor Company Code')

    # Used to get the company id by the code
    def get_company_by_ecc(self, company_code):
        rec = self.search([('epicor_company_code', '=', company_code)],
                          limit=1)
        if rec:
            return rec.id
        else:
            return False


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Many2one('starken_crm.partner.type', 'Partner Type')
    fax = fields.Char('Fax', readonly=False, store=True,copy=True)
    selection_f = fields.Boolean(' ', default=False, store=False)
    quo_running_number = fields.Integer(default='1')
    street3 = fields.Char()
    epicor_customer_id = fields.Char('Epicor Customer ID', readonly=False)
    is_epicor_customer = fields.Boolean(compute='_is_epicor_customer', store=True)
    division = fields.Selection([('fd','FD'),('td','TD')])
    epicor_customer_num = fields.Char('Epicor Customer Num', readonly=False)
    ship_to_id = fields.Char('Ship To ID', readonly=False, store=True, copy=True)
    attn = fields.Char('Attn', readonly=False, store=True, copy=True)
    synced_to_epicor = fields.Boolean('Synced To Epicor')
    ship_seq = fields.Integer('Ship To Id Sequence', default=1)
    project_count = fields.Integer("Project", compute='_compute_dev_proj_count')
    project_count_ids = fields.Many2many('crm.lead', compute="_compute_dev_proj_count", string='Projects Count', help='Technical field used for stat button')
    lead_partner_id = fields.Many2one('crm.lead',string="Leads")

    def _compute_dev_proj_count(self):
        for p in self:
            # count_dev = self.env['crm.lead'].search([('crm_prj_dev', '=', p.id)])
            # count_arc = self.env['crm.lead'].search([('crm_prj_arc', '=', p.id)])
            # count_cseng = self.env['crm.lead'].search([('crm_prj_cseng', '=', p.id)])
            # count_qs = self.env['crm.lead'].search([('crm_prj_qs', '=', p.id)])
            p.project_count_ids = self.env['crm.lead'].search(['|','|','|','|',('crm_prj_dev', '=', p.id),('crm_prj_arc', '=', p.id),('crm_prj_cseng', '=', p.id),('crm_prj_qs', '=', p.id),('crm_prj_own_mark', '=', p.id)])
            p.project_count = len(p.project_count_ids)

    def action_view_sub_project(self):
        '''
        This function returns an action that displays the leads from project.
        '''
        action = self.env.ref('crm.crm_lead_all_leads').read()[0]
        action['domain'] = [('id', 'in', self.project_count_ids.ids)]
        return action

    def get_shipping_id_sequence(self, par_id):
        if par_id:
            par_obj = self.browse(par_id)
            if par_obj.name:
                ship_seq_unused = False
                ids_used = []
                for child in par_obj.child_ids:
                    if child.ship_to_id:
                        ids_used.append(child.ship_to_id)
                while not ship_seq_unused:
                    ship_seq_used = '%s-%02d' % (par_obj.name[0].capitalize(),
                                                 par_obj.ship_seq)
                    par_obj.sudo().write({'ship_seq': par_obj.ship_seq + 1})
                    if ship_seq_used not in ids_used:
                        ship_seq_unused = True
                return ship_seq_used
        return self.env['ir.sequence'].sudo().\
            next_by_code('res.partner.shiptoid') or ''

    @api.model
    def create(self, vals):
        if vals.get('parent_id'):
            vals['supplier_rank'] = 0
            vals['customer_rank'] = 0
        tp_contact = vals.get('type', False)
        if tp_contact == 'delivery' and not vals.get('ship_to_id', False)\
                and not vals.get('synced_to_epicor', False):
            vals['ship_to_id'] = self.get_shipping_id_sequence(
                vals.get('parent_id', False))
        res = super(ResPartner, self).create(vals)
        return res

    def write(self, values):
        for rec in self:
            rec.shipping_address_blocker_check()
            rec.check_if_user_can_adjust(values)
            tp_contact = values.get('type', False)
            if tp_contact == 'delivery' and not values.get('ship_to_id', False) and \
                    not rec.ship_to_id and not values.get('synced_to_epicor',
                                                          False):
                par_id = values.get('parent_id', False)
                if not par_id:
                    par_id = rec.parent_id.id
                values['ship_to_id'] = rec.get_shipping_id_sequence(par_id)


        return super(ResPartner, self).write(values)

    def check_if_user_can_adjust(self, values_to_adjust):
        ignored_values_to_flag = ['child_ids', 'ship_seq',
                                  'complete_cp_setup', 'is_cash_sales',
                                  'opportunity_ids', 'contract_ids',
                                  'synced_to_epicor', 'meeting_ids'
                                  ]
        modifying_unrelated = False
        for el_k in values_to_adjust.keys():
            if el_k not in ignored_values_to_flag:
                modifying_unrelated = True
        if self.type != 'contact':
            modifying_unrelated = False
        # if modifying_unrelated:
        #     self.check_object_permission_to_adjust()
        return

    def shipping_address_blocker_check(self):
        ship_sync = self._context.get('ship_sync', False)
        if self.synced_to_epicor and self.type == 'delivery' and \
                not(self.env.uid == 1 or self.env.user.
                    has_group('base.group_system') or ship_sync):
            raise Warning('You are not allowed to modify synced'
                          ' shipping address \n'
                          'Any edited values will not be saved')


    # def check_object_permission_to_adjust(self):
    #     # Ignore non-customer and non-supplier partners
    #     if self.customer_rank == 0 and self.supplier_rank == 0:
    #         return
    #     # Non-sync customer are allowed to be adjusted
    #     if not self.epicor_customer_num:
    #         return
    #     # Allow for master admin and odoobot (needed for sync write)
    #     if self.env.user.has_group('base.group_system') or \
    #             self.env.uid == 1:
    #         return
    #     # Allow owner of the partner_id to adjust
    #     if self.env.user.partner_id.id == self.id:
    #         return
    #     # Allow children of the partner_id to modify parent
    #     if self.env.user.partner_id.parent_id:
    #         if self.id == self.env.user.partner_id.parent_id.id:
    #             return
    #     raise ValidationError('You are not allowed to change any '
    #                           'information for this contact')

    @api.depends('epicor_customer_id')
    def _is_epicor_customer(self):
        for rec in self:
            is_epicor_customer = False
            if rec.epicor_customer_id:
                is_epicor_customer = True
            rec.is_epicor_customer = is_epicor_customer

    def get_next_quo_number(self):
        self.ensure_one()
        running_number = self.quo_running_number
        if self.company_id and self.company_id.business_unit_code:
            quotation_number = 'QUO%s-%s-%s' % (
                self.company_id.business_unit_code,
                str(self.id).zfill(4), str(running_number).zfill(7))
        else:
            quotation_number = 'QUO-%s-%s' % (str(self.id).zfill(4),
                                              str(running_number).zfill(7))
        self.update({
            'quo_running_number': running_number + 1
        })
        return quotation_number

    def _get_contact_name(self, partner, name):
        return "%s: %s" % (partner.commercial_company_name or partner.sudo().parent_id.name, name)


    def build_customers_sync_query(self, extra_wheres=False, ofst=False):
        sel_qry = ""
        sel_qry += "select[Customer].[Name] as [Customer_Name],[Customer].[CustNum] as [Customer_CustNum],[Customer].[CustID] as [Customer_CustID]"
        sel_qry += ",[Customer].[Address1] as [Customer_Address1],[Customer].[Address2] as [Customer_Address2],[Customer].[Address3] as [Customer_Address3]"
        sel_qry += ",[Customer].[City] as [Customer_City],[Customer].[State] as [Customer_State],[Customer].[Zip] as [Customer_PostCode]"
        sel_qry += ",[Customer].[Country] as [Customer_Country],[Customer].[FaxNum] as [Customer_FaxNum],[Customer].[PhoneNum] as [Customer_PhoneNum]"
        sel_qry += ",[Customer].BTName as [Customer_BillToName],[Customer].BTAddress1 as [Customer_BillToAddress1]"
        sel_qry += ",[Customer].BTAddress2 as [Customer_BillToAddress2],[Customer].BTAddress3 as [Customer_BillToAddress3]"
        sel_qry += ",[Customer].ChangeDate as [Customer_ChangeDate],[Terms].[TermsCode] as [Terms_TermsCode],[Terms].[Description] as [Terms_Description]"
        sel_qry += ",[SalesRep].[Name] as [SalesRep_Name],[SalesRep].SalesRepCode as [SalesRep_Code],[SalesRep].EMailAddress as [EMailAddress]"
        # sel_qry += ",[Plant].[Name] as [Plant_Name]"
        sel_qry += " from dbo.Customer as Customer"
        sel_qry += " left outer join Erp.Terms as Terms on Customer.Company = Terms.Company and Customer.TermsCode = Terms.TermsCode"
        sel_qry += " left outer join Erp.Company as Company on Customer.Company = Company.Company"
        sel_qry += " left outer join Erp.CustGrup as CustGrup on Customer.Company = CustGrup.Company and Customer.GroupCode = CustGrup.GroupCode "
        sel_qry += " left outer join Erp.SalesRep as SalesRep on Customer.Company = SalesRep.Company and Customer.SalesRepCode = SalesRep.SalesRepCode"
        # sel_qry += " left outer join Erp.Plant as Plant on Plant.Plant = Customer.ShortChar20 and Plant.Company = Customer.Company"
        sel_qry += " where Customer.company IN ('SAAC', 'SESB')"
        if extra_wheres:
            sel_qry += "AND " + extra_wheres
        sel_qry += " ORDER BY Customer.Name"
        if ofst:
            sel_qry += " " + ofst

        return sel_qry


    def process_customers_data(self, datas):
        if datas:
            for data in datas:
                existed_model = self.env['res.partner'].search([('epicor_customer_id', '=', data.Customer_CustID)], limit=1)
                self.create_or_update_on_with_customer_data(existed_model, data)

    def create_or_update_on_with_customer_data(self, existing_mdl, new_data):
        term_id = self.env['account.payment.term'].search([('name', '=', new_data.Terms_TermsCode)])
        #print(new_data.Terms_TermsCode+" "+str(term_id))
        if not term_id:
            term_id = self.env['account.payment.term'].sudo().create({
                'name': new_data.Terms_TermsCode
            })
            term_id = [term_id]

        if existing_mdl:
            existing_mdl.write({
                'name' : new_data.Customer_Name,
                'epicor_customer_num': new_data.Customer_CustNum,
                'epicor_customer_id': new_data.Customer_CustID,
                'street' : new_data.Customer_Address1,
                'street2' : new_data.Customer_Address2 + ' ' + new_data.Customer_Address3,
                'city' : new_data.Customer_City,
                'state_id' : self.get_nearest_many2one('res.country.state', new_data.Customer_State),
                'country_id' : self.get_nearest_many2one('res.country', new_data.Customer_Country),
                'zip' : new_data.Customer_PostCode,
                'phone': new_data.Customer_PhoneNum,
                'fax' : new_data.Customer_FaxNum,
                'property_payment_term_id' : term_id[0],
                'user_id' : self.get_sales_rep(new_data.EMailAddress),
                'customer_rank': 1
            })
        else:
            self.env['res.partner'].sudo().create({
                'name' : new_data.Customer_Name,
                'epicor_customer_num': new_data.Customer_CustNum,
                'epicor_customer_id': new_data.Customer_CustID,
                'street' : new_data.Customer_Address1,
                'street2' : new_data.Customer_Address2 + ' ' + new_data.Customer_Address3,
                'city' : new_data.Customer_City,
                'state_id' : self.get_nearest_many2one('res.country.state', new_data.Customer_State),
                'country_id' : self.get_nearest_many2one('res.country', new_data.Customer_Country),
                'zip' : new_data.Customer_PostCode,
                'phone': new_data.Customer_PhoneNum,
                'fax' : new_data.Customer_FaxNum,
                'property_payment_term_id' : term_id[0],
                'user_id' : self.get_sales_rep(new_data.EMailAddress),
                'customer_rank': 1
            })

    def get_nearest_many2one(self, class_to_use, newName):
        if newName:
            existing_val = self.env[class_to_use].search([('name','ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False

    def get_sales_rep(self, newName):
        if newName:
            existing_val = self.env['res.users'].search([('login','=',newName)],limit=1)
            if existing_val:
                # return existing_val.partner_id.id
                return existing_val.id
            else:
                return False
        else:
            return False

    def build_get_shipto_address_query(self, ship_to_id, customer_n, company_code):
        sel_qry = ""
        sel_qry += "SELECT ShipToNum"
        sel_qry += " FROM erp.ShipTo"
        sel_qry += " WHERE Company = '%s' AND ShipToNum = '%s' AND CustNum = '%s'" % (company_code,ship_to_id,customer_n)

        return sel_qry

    def get_shipto_address(self, datas):
        rtn_rslt = []
        for data in datas:
            rtn_rslt.append(data.ShipToNum)
        return rtn_rslt

    def build_shipto_sync_query(self, extra_wheres=False, ofst=False):
        customer = self.env['res.partner'].search([('customer_rank', '>', 0),('type', '=', 'contact')])
        epicor_customer_num = []
        for x in customer:
            if x.epicor_customer_num:
                epicor_customer_num.append(x.epicor_customer_num)
        custnum = ",".join(epicor_customer_num)

        sel_qry = ""
        sel_qry += "SELECT * FROM erp.shipto (NOLOCK) WHERE company IN ('SAAC', 'SESB') AND ShipToNum!='' AND custnum IN ("+custnum+")"

        if extra_wheres:
            sel_qry += " AND " + extra_wheres
        sel_qry += " ORDER BY Name"
        if ofst:
            sel_qry += " " + ofst

        # _logger.warning(sel_qry)

        return sel_qry

    def process_shipto_data(self, datas):
        if datas:
            for data in datas:
                existed_parent = self.env['res.partner'].search([('epicor_customer_num', '=', data.CustNum)], limit=1)
                if existed_parent:
                    existed_model = self.env['res.partner'].search([('ship_to_id', '=', data.ShipToNum),('parent_id', '=', existed_parent.id)], limit=1)
                else:
                    existed_model = False
                self.create_or_update_on_with_shipto_data(existed_model, data)

    def create_or_update_on_with_shipto_data(self, existing_mdl, new_data):
        if existing_mdl:
            existing_mdl.write({
                'type': 'delivery',
                'name': new_data.Name,
                'ship_to_id': new_data.ShipToNum,
                'street': new_data.Address1,
                'street2': new_data.Address2 + ' ' + new_data.Address3,
                'city': new_data.City,
                'state_id': self.get_nearest_many2one('res.country.state', new_data.State),
                'zip': new_data.ZIP,
                'country_id': self.get_nearest_many2one('res.country', new_data.Country),
                'fax': new_data.FaxNum,
                'phone': new_data.PhoneNum,
                'synced_to_epicor': True
            })
        else:
            customer = self.env['res.partner'].search([('epicor_customer_num', '=', new_data.CustNum)], limit=1)
            if customer:
                self.env['res.partner'].sudo().create({
                    'type': 'delivery',
                    'name': new_data.Name,
                    'ship_to_id': new_data.ShipToNum,
                    'street': new_data.Address1,
                    'street2': new_data.Address2+' '+new_data.Address3,
                    'city': new_data.City,
                    'state_id': self.get_nearest_many2one('res.country.state', new_data.State),
                    'zip': new_data.ZIP,
                    'country_id': self.get_nearest_many2one('res.country', new_data.Country),
                    'fax': new_data.FaxNum,
                    'phone': new_data.PhoneNum,
                    'parent_id': customer.id,
                    'synced_to_epicor': True
                })
