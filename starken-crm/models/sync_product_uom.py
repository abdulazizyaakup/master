from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging
import traceback
import hashlib

_logger = logging.getLogger(__name__)

try:
    import pyodbc
except:
    _logger.warning("Failed to load pyodbc")

class PaymentTermSync(models.Model):
    _name = 'starken_crm.uom.sync'
    _description = "Sync: Product UOM"

    def get_mssql_query(self, server, user, passwd, database, query):
        server = '172.16.90.10'
        user = 'ppchonline'
        passwd = 'wxdDx2T5wAAgP2YM'
        database = 'PPCHLive102'

        conn = pymssql.connect(server=server, user=user, password=passwd,
                   database=database)

        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_from_parameter_or_val(self, con_det=False):
        # Assign by connection dict or by parameter
        if not con_det:
            hst = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.hostname')
            usr = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.username')
            pss = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.pass')
            dab = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.database')
        else:
            hst = con_det.get('hostname')
            usr = con_det.get('username')
            pss = con_det.get('pass')
            dab = con_det.get('database')

      # Check if all value all not empty
        if not hst:
            raise ValidationError("Missing hostname for VPN connection")
        if not usr:
            raise ValidationError("Missing username for VPN connection")
        if not pss:
            raise ValidationError("Missing password for VPN connection")
        if not dab:
            raise ValidationError("Missing database for VPN connection")

        return hst,usr,pss,dab

    def build_select_query(self):
        sel_qry = "SELECT * FROM erp.uom (NOLOCK) WHERE company = 'SAAC'"

        return sel_qry

    def sync_product_uom(self, override_con_det=False):
        date_format = "%m/%d/%Y, %H:%M:%S"
        (hst, usr, pss, dab) = self.get_from_parameter_or_val(override_con_det)
        qry = self.build_select_query()
        reslt = self.get_mssql_query(hst, usr, pss, dab, qry)
        resltcount = len(reslt)
        # _logger.info(resltcount)
        # This code needs change. Using number as reference is error prone
        for x in reslt:
            uom = self.env['uom.uom'].search([('name', '=', x[1])], limit=1)
            if not uom:
                self.env['uom.uom'].create([{
                    'name': x[1],
                    'category_id' : 1,
                    'uom_type' : 'bigger',
                    'rounding' : 0.00100,
                    'factor_inv': 1.00000,
                    'active' : True
                }])

        self.env['starken_crm.mssql.track'].sudo().set_execution_track('UOM_Synced_Signal', datetime.now().strftime(date_format))
