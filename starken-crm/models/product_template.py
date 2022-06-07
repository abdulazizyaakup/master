from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):

    _inherit = "product.template"

    part_number = fields.Char('Part Number', readonly=False, store=True, copy=True) #
    pro_class = fields.Many2one('starken_crm.product.class', 'Product Class', readonly=False, store=True, copy=True) #
    pro_group = fields.Many2one('starken_crm.product.group', 'Product Group', readonly=False, store=True, copy=True) #
    pro_length = fields.Float('Length (mm)', readonly=False, store=True, copy=True) #
    pro_width = fields.Float('Thickness (mm)', readonly=False, store=True, copy=True) #
    pro_height = fields.Float('Height (mm)', readonly=False, store=True, copy=True) #
    net_vol = fields.Float('Net Volume', readonly=False, store=True, copy=True, digits=(12, 5)) #
    net_vol_uom = fields.Many2one('starken_crm.volume.uom', 'Net Volume UOM', readonly=False, store=True, copy=True) #
    net_vol_uom_desc = fields.Char('Net Volume UOM Description', readonly=False, store=True, copy=True) # UNINF IN DATABASE. ASSUMPTION SAME AS UOM
    compression_strength = fields.Char('Compression Strength', readonly=False, store=True, copy=True) # UNINF IN DATABASE
    meter_sq_pallet = fields.Char('Metre sq/pallet', readonly=False, store=True, copy=True) # UNINF IN DATABASE
    num_pcs_pallet = fields.Char('No of pcs/pallet', readonly=False, store=True, copy=True) # UNINF IN DATABASE
    pallets_delivery = fields.Char('Pallets/Delivery', readonly=False, store=True, copy=True) # UNINF IN DATABASE
    pro_weight = fields.Float('Weight (kg)', readonly=False, store=True, copy=True)
    block_type = fields.Char(compute='_get_block_type', store=True)
    max_price_alert = fields.Boolean(default=False)
    max_price = fields.Float(digits=(10,2))

    # def name_get(self):
    # @api.multi
    # @api.depends('name', 'part_number')
    # def name_get(self):
    #     result = []
    #     for prod in self:
    #         part = prod.part_number
    #         name = prod.name
    #         if(part):
    #             result.append(part)
    #         if(part == False):
    #             result.append(name)
    #     return result


    @api.depends('part_number')
    def _get_block_type(self):
        for product in self:
            block_type = False
            if product.part_number:
                if 's3' in product.part_number.lower():
                    block_type = 'S3'
                elif 's5' in product.part_number.lower():
                    block_type = 'S5'
                elif 's7' in product.part_number.lower():
                    block_type = 'S7'

            product.block_type = block_type

    @api.onchange('net_vol_uom')
    def get_onchange_net_vol_desc(self):
       if self.net_vol_uom:
           self.net_vol_desc = self.net_vol_uom.default_description

    def get_nearest_many2one(self, class_to_use, newName,label='name'):
        if newName:
            existing_val = self.env[class_to_use].search([(label,'ilike',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                return False
        else:
            return False


    def populate_by_ms(self, datas):
        if datas:
            for data in datas:
                c_com = self.env['res.company'].get_company_by_ecc(
                    data.company)
                if not c_com:
                    _logger.warning(
                        'No valid company specified for this product')
                existed_model = self.env['product.template'].search([
                    ('company_id', '=', c_com),
                    ('name', '=', data.partnum),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False)], limit=1)
                self.create_or_update_on_with_data(existed_model, data, c_com)

    def create_or_update_on_with_data(self, existing_mdl, new_data, c_com):
        if existing_mdl:
            nwval = {}
            # UPDATE MODEL
            _logger.info('Product_Sync: Updating product with part number: %s' % new_data.partnum)
            if self.not_similar_name_comparator(existing_mdl.pro_class, new_data.PRODUCT_CLASS__C):
                nwval.update({'pro_class' : self.get_or_add_many2one('starken_crm.product.class', new_data.PRODUCT_CLASS__C)})

            if self.not_similar_name_comparator(existing_mdl.pro_group, new_data.PRODUCT_GROUP__C):
                nwval.update({'pro_group' : self.get_or_add_many2one('starken_crm.product.group', new_data.PRODUCT_GROUP__C)})

            if self.not_similar_name_comparator(existing_mdl.net_vol_uom, new_data.NET_VOLUME_UOM__C):
                nwval.update({'net_vol_uom' : self.get_or_add_many2one('starken_crm.volume.uom', new_data.NET_VOLUME_UOM__C, 'default_description')})

            if existing_mdl.net_vol_uom_desc != new_data.NET_VOLUME_UOM_DESCRIPTION__C:
                nwval.update({'net_vol_uom_desc' : new_data.NET_VOLUME_UOM_DESCRIPTION__C})

            v_to_use = new_data.UOM__C
            if not v_to_use:
                v_to_use = new_data.ium

            if self.not_similar_name_comparator(existing_mdl.uom_id, v_to_use):
                nwval.update({'uom_id' : self.get_or_add_uom(v_to_use)})

            if self.not_similar_name_comparator(existing_mdl.uom_po_id, new_data.pum):
                nwval.update({'uom_po_id' : self.get_or_add_uom(new_data.pum)})

            if existing_mdl.net_vol != float(new_data.NET_VOLUME__C):
                nwval.update({'net_vol' : float(new_data.NET_VOLUME__C)})

            if existing_mdl.pro_length != float(new_data.LENGTH_MM__C):
                nwval.update({'pro_length' : float(new_data.LENGTH_MM__C)})

            if existing_mdl.pro_height != float(new_data.HEIGHT_MM__C):
                nwval.update({'pro_height' : float(new_data.HEIGHT_MM__C)})

            if existing_mdl.pro_width != float(new_data.THICKNESS_MM__C):
                nwval.update({'pro_width' : float(new_data.THICKNESS_MM__C)})

            if existing_mdl.pro_weight != float(new_data.WEIGHT_KG__C):
                nwval.update({'pro_weight' : float(new_data.WEIGHT_KG__C)})

            if existing_mdl.description_sale != new_data.DESCRIPTION:
                nwval.update({'description_sale' : new_data.DESCRIPTION})

            if existing_mdl.pallets_delivery != new_data.PALLETS_DELIVERY__C:
                nwval.update({'pallets_delivery' : new_data.PALLETS_DELIVERY__C})

            if existing_mdl.default_code != new_data.searchword:
                nwval.update({'default_code' : new_data.searchword})

            if existing_mdl.active != self.get_bool_equivalent(new_data.ISACTIVE):
                nwval.update({'active' : self.get_bool_equivalent(new_data.ISACTIVE)})

            if nwval:
                existing_mdl.write(nwval)
        else:
            # NEW MODEL
            _logger.info('Product_Sync: Creating product with part number: %s' % new_data.partnum)
            self.env['product.template'].sudo().create({
                    'name' : new_data.partnum,
                    'part_number' : new_data.partnum,
                    'company_id': c_com,
                    'pro_class' : self.get_or_add_many2one('starken_crm.product.class', new_data.PRODUCT_CLASS__C),
                    'net_vol_uom' : self.get_or_add_many2one('starken_crm.volume.uom', new_data.NET_VOLUME_UOM__C, 'default_description'),
                    'net_vol_uom_desc' : new_data.NET_VOLUME_UOM_DESCRIPTION__C,
                    'pro_group' : self.get_or_add_many2one('starken_crm.product.group', new_data.PRODUCT_GROUP__C),
                    'uom_id' : self.get_or_add_uom(new_data.UOM__C if new_data.UOM__C else new_data.ium),
                    'uom_po_id' : self.get_or_add_uom(new_data.pum),
                    'pallets_delivery' : new_data.PALLETS_DELIVERY__C,
                    'pro_length' : float(new_data.LENGTH_MM__C),
                    'pro_height' : float(new_data.HEIGHT_MM__C),
                    'pro_width' : float(new_data.THICKNESS_MM__C),
                    'net_vol' : float(new_data.NET_VOLUME__C),
                    'pro_weight' : float(new_data.WEIGHT_KG__C),
                    'description_sale' : new_data.DESCRIPTION,
                    'responsible_id': 2, # Always admin as admin has more company
                    'default_code' : new_data.searchword,
                    'active' : self.get_bool_equivalent(new_data.ISACTIVE)
                })

    def get_bool_equivalent(self, bool_word):
        if bool_word.upper() == 'TRUE':
            return True
        else:
            return False

    def get_or_add_many2one(self, class_to_use, newName, var_full_name = 'full_name'):
        if newName:
            existing_val = self.env[class_to_use].search([('name','=',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                rslt = self.env[class_to_use].sudo().create({'name' : newName, var_full_name : newName})
                return rslt.id
        else:
            return False

    def get_or_add_uom(self, newName):
        if newName:
            existing_val = self.env['uom.uom'].search([('name','=',newName)],limit=1)
            if existing_val:
                return existing_val.id
            else:
                rslt = self.env['uom.uom'].sudo().create({'name' : newName, 'category_id' : 1, 'uom_type' : 'bigger', 'rounding' : 0.00100, 'factor_inv': 1.00000, 'active' : True})
                return rslt.id
        else:
            return 1

    def not_similar_name_comparator(self, model_to_compare, value_to_compare):
        if model_to_compare:
            if not value_to_compare:
                return True
            else:
                if model_to_compare.name != value_to_compare:
                    return True
                else:
                    return False
        else:
            if not value_to_compare:
                return False
            else:
                return True

    def build_select_query(self, extra_wheres=False, ofst=False):
        sel_qry = """SELECT parttype, grade, isstandardblock, size,
                      a.prodcode, CAST(CASE WHEN size != 'NA' THEN
                      dbo.Getcolumnvalue(size, 'X', 1) ELSE '0' END AS INT)
                      AS LENGTH_MM__C, CAST(CASE WHEN size != 'NA' THEN
                      dbo.Getcolumnvalue(size, 'X', 2) ELSE '0' END AS INT)
                      AS HEIGHT_MM__C, CAST(CASE WHEN size != 'NA' THEN
                      dbo.Getcolumnvalue(size, 'X', 3) ELSE '0' END AS INT)
                      AS THICKNESS_MM__C, CAST(CASE WHEN size != 'NA' THEN
                      dbo.Getcolumnvalue(size, 'X', 3) ELSE '0' END AS INT)
                      AS HEIGHT_MM__C0, a.company, a.partdescription NAME,
                      a.partdescription DESCRIPTION, 'TRUE' ISACTIVE,
                      'FALSE' ISDELETED, uom.uomdesc UOM_DESCRIPTION__C,
                      '16-18' PALLETS_DELIVERY__C,
                      prodgrup.description PRODUCT_GROUP__C, a.partnum,
                      a.netweight WEIGHT_KG__C, a.netvolume NET_VOLUME__C,
                      partclass.description PRODUCT_CLASS__C, a.salesum UOM__C,
                      '' PRODUCT_SIZE__C, '' PRODUCT_CATEGORY__C,
                      a.partnum PART_NUMBER__C,
                      a.netvolumeuom NET_VOLUME_UOM__C,
                      UOM2.uomdesc NET_VOLUME_UOM_DESCRIPTION__C, a.changedon,
                      a.pum, a.ium, a.searchword, a.inactive INACTIVE FROM
                      (SELECT 'NA' AS parttype, 'NA' AS grade, 'NA' AS size,
                      CASE WHEN
                      dbo.Getcolumnvalue(partnum, '-', 3) = '600x200x100' AND
                      classid = 'SB' THEN 1 ELSE 0 END AS isstandardblock,
                      * FROM dbo.part (nolock) WHERE company IN
                      ('SAAC', 'SESB') AND
                      prodcode IN ( 'CAKE', 'CONC', 'INTL', 'GRL', 'RM',
                      'SAMPLE', 'TOOL', 'TRENCHER', 'TRP', 'DROPSHIP', 'DS-P',
                      'DS-T&A', '', 'DS-B', 'DS-T' ) UNION ALL SELECT
                      dbo.Getcolumnvalue(partnum, '-', 1) AS parttype,
                      dbo.Getcolumnvalue(partnum, '-', 2) AS grade,
                      CASE WHEN prodcode IN ('RJB','RJW') THEN
                      dbo.Getcolumnvalue(partnum, '-', 4) ELSE
                      dbo.Getcolumnvalue(partnum, '-', 3) END AS size,
                      CASE WHEN dbo.Getcolumnvalue(partnum, '-', 3) =
                      '600x200x100' AND classid = 'SB' THEN 1 ELSE 0 END
                      AS isstandardblock, * FROM dbo.part (nolock) WHERE
                      company IN ('SAAC', 'SESB') AND prodcode NOT IN
                      ( 'CAKE', 'CONC', 'INTL', 'GRL', 'RM', 'SAMPLE', 'TOOL',
                      'TRENCHER', 'TRP', 'DROPSHIP', 'DS-P', 'DS-T&A', '',
                      'DS-B', 'DS-T' )) AS a LEFT OUTER JOIN
                      erp.prodgrup ProdGrup (nolock) ON
                      a.company = prodgrup.company AND
                      a.prodcode = prodgrup.prodcode LEFT OUTER JOIN
                      erp.partclass PartClass (nolock) ON
                      a.company = partclass.company AND
                      a.classid = partclass.classid LEFT OUTER JOIN
                      erp.uom UOM (nolock) ON a.company = uom.company AND
                      a.salesum = uom.uomcode LEFT OUTER JOIN erp.uom UOM2
                      (nolock) ON a.company = UOM2.company AND
                      a.netvolumeuom = UOM2.uomcode WHERE a.company IN
                      ('SAAC', 'SESB') AND a.inactive = 0 """
        if extra_wheres:
            sel_qry += "AND " + extra_wheres
        sel_qry += " ORDER BY NAME DESC"
        if ofst:
            sel_qry += " " + ofst

        return sel_qry
