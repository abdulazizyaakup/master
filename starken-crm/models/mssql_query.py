from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging
import traceback
import hashlib
import pytz
# import pymssql

_logger = logging.getLogger(__name__)

try:
    import pyodbc
except:
    _logger.warning("Failed to load pyodbc")


class MSSQLQuery(models.Model):
    _name = 'starken_crm.mssql.query'
    _description = "MSSQL Query Class"

    def get_mssql_query(self, server, user, passwd, database, query):
      print("xx")
        # server = '172.16.90.10'
        # user = 'ppchonline'
        # passwd = 'wxdDx2T5wAAgP2YM'
        # database = 'PPCHLive102'

        # conn = pymssql.connect(server=server, user=user, password=passwd,
        #            database=database)

        # cursor = conn.cursor()
        # cursor.execute(query)
        # return cursor.fetchall()

    def notify_users_on_fail(self, subject, errorMessage, email_tmplt):
      context = {'trace_msg' : errorMessage}
      su_id = self.env['res.partner'].sudo().browse(SUPERUSER_ID)
      email_to_notify = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.fail.notifyemails')
      template_id = self.env['ir.model.data'].sudo().get_object_reference('starken-crm', email_tmplt)[1]
      template_browse = self.env['mail.template'].sudo().browse(template_id)
      if template_browse and email_to_notify:
         values = template_browse.with_context(context).generate_email(self.id, fields=None)
         values['subject'] = subject
         values['email_to'] = email_to_notify
         values['email_from'] = su_id.email
         if not values['email_to'] and not values['email_from']:
            _logger.warning('Error on sending email for failures to %s' % email_to_notify)
            return False
         msg = self.env['mail.mail'].sudo().create(values)
         msg.sudo().send()
         return True
      _logger.warning('Error on sending email for failures to due to missing template or user to notify')
      return False

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

    def sync_product_tracked_from_database(self, override_con_det=False,
                                           force_resync=False,
                                           max_count_resync=10000,
                                           resync_offset=0):
      try:
        date_format = "%m/%d/%Y, %H:%M:%S"
        sql_format = "%Y-%m-%d %H:%M:%S.000"
        exec_next_execution = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Products_next_execution')
        if exec_next_execution and not force_resync:
          if fields.datetime.now() < datetime.strptime(exec_next_execution.execution_details,date_format):
             return

        (hst, usr, pss, dab) = self.get_from_parameter_or_val(override_con_det)
        exec_track = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Products')
        ofst = "0"
        nextofst = "0"
        max_processes = 1000
        where_track = False

        if force_resync:
            max_processes = max_count_resync
            ofst = str(resync_offset)

        if exec_track and not force_resync:
            ofst = exec_track.execution_details

        if exec_next_execution and not force_resync:
            next_date = pytz.utc.localize(
                exec_next_execution.last_execution_time)
            next_date = next_date.astimezone(
                pytz.timezone('Asia/Kuala_Lumpur'))
            where_track = "a.changedon >= '" + \
                next_date.strftime(sql_format) + "'"

        offsetqry = "OFFSET " + ofst  + " ROWS FETCH NEXT " + str(max_processes)  + " ROWS ONLY"
        qry = self.env['product.template'].sudo().build_select_query(where_track,offsetqry)

        _logger.info('Product_Sync: Running query : %s' % qry)
        reslt = self.get_mssql_query(hst, usr, pss, dab, qry)
        resltcount = len(reslt)
        _logger.info('Product_Sync: Syncing %d products' % resltcount)
        self.env['product.template'].sudo().populate_by_ms(reslt)

        if resltcount == max_processes:
          incofst = int(ofst) + max_processes
          nextofst = str(incofst)
        else:
          nxt_hours = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.next_execution_hours')
          if not nxt_hours:
            nxt_hours = "4" # 4 is 12pm in GMT+8
          nxt_exec_date = datetime.now().replace(minute=0, hour=int(nxt_hours), second=0)
          nxt_exec_date += timedelta(days=1)
          self.env['starken_crm.mssql.track'].sudo().set_execution_track('Products_next_execution',nxt_exec_date.strftime(date_format))

        self.env['starken_crm.mssql.track'].sudo().set_execution_track('Products',nextofst)
      except Exception as e:
        error_msg = str(e)
        error_msg_md5 = hashlib.md5(error_msg.encode()).hexdigest()
        _logger.exception('Product_Sync: Syncing encountered an error :\n %s' % error_msg)
        error_equiv = self.env['starken_crm.mssql.track'].sudo().get_execution_track('error_%s'%error_msg_md5)
        report = True
        if error_equiv:
          difference_in_time = datetime.now() - datetime.strptime(error_equiv.execution_details,date_format)
          if difference_in_time.total_seconds() < 86400: # If less than 24 hours in seconds form
            self.env['starken_crm.mssql.track'].sudo().set_execution_track('error_%s'%error_msg_md5,datetime.now().strftime(date_format)) # Extend the error forever if keep appearing.Only need to send once
            report = False
        if report:
          self.env['starken_crm.mssql.track'].sudo().set_execution_track('error_%s'%error_msg_md5,datetime.now().strftime(date_format))
          self.notify_users_on_fail('Error on syncing products over VPN from Epicor Systems', error_msg, 'vpn_fail_email_template_products_notf_email')


    def sync_customer_tracked_from_database(self, override_con_det=False):
      try:
        date_format = "%m/%d/%Y, %H:%M:%S"
        sql_format = "%Y-%m-%d %H:%M:%S.000"
        exec_next_execution = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Customer_next_execution')
        if exec_next_execution:
          if fields.datetime.now() < datetime.strptime(exec_next_execution.execution_details,date_format):
             return

        (hst, usr, pss, dab) = self.get_from_parameter_or_val(override_con_det)
        exec_track = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Customer')
        ofst = "0"
        nextofst = "0"
        max_processes = 200
        where_track = False

        if exec_track:
          ofst = exec_track.execution_details

        if exec_next_execution:
            next_date = pytz.utc.localize(
                exec_next_execution.last_execution_time)
            next_date = next_date.astimezone(
                pytz.timezone('Asia/Kuala_Lumpur'))
            where_track = "Customer.ChangeDate >= '" + \
                next_date.strftime(sql_format) + "'"

        offsetqry = "OFFSET " + ofst  + " ROWS FETCH NEXT " + str(max_processes)  + " ROWS ONLY"
        qry = self.env['res.partner'].sudo().build_customers_sync_query(where_track,offsetqry)

        reslt = self.get_mssql_query(hst, usr, pss, dab, qry)
        resltcount = len(reslt)
        self.env['res.partner'].sudo().process_customers_data(reslt)

        if resltcount == max_processes:
          incofst = int(ofst) + max_processes
          nextofst = str(incofst)
        else:
          nxt_hours = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.next_execution_hours')
          if not nxt_hours:
            nxt_hours = "4" # 4 is 12pm in GMT+8
          nxt_exec_date = datetime.now().replace(minute=0, hour=int(nxt_hours), second=0)
          nxt_exec_date += timedelta(days=1)
          self.env['starken_crm.mssql.track'].sudo().set_execution_track('Customer_next_execution',nxt_exec_date.strftime(date_format))

        self.env['starken_crm.mssql.track'].sudo().set_execution_track('Customer',nextofst)
      except Exception as e:
        error_msg = str(e)
        error_msg_md5 = hashlib.md5(error_msg.encode()).hexdigest()
        _logger.exception('Error on syncing Epicor systems via VPN :\n %s' % error_msg)
        error_equiv = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Customer_error_%s'%error_msg_md5)
        report = True
        if error_equiv:
          difference_in_time = datetime.now() - datetime.strptime(error_equiv.execution_details,date_format)
          if difference_in_time.total_seconds() < 86400: # If less than 24 hours in seconds form
            self.env['starken_crm.mssql.track'].sudo().set_execution_track('Customer_error_%s'%error_msg_md5,datetime.now().strftime(date_format)) # Extend the error forever if keep appearing.Only need to send once
            report = False
        if report:
          self.env['starken_crm.mssql.track'].sudo().set_execution_track('Customer_error_%s'%error_msg_md5,datetime.now().strftime(date_format))
          self.notify_users_on_fail('Error on syncing Customer over VPN from Epicor Systems', error_msg, 'vpn_fail_email_template_products_notf_email')


    def sync_shipto_tracked_from_database(self, override_con_det=False):
      try:
        date_format = "%m/%d/%Y, %H:%M:%S"
        sql_format = "%Y-%m-%d %H:%M:%S.000"
        exec_next_execution = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Shipto_next_execution')
        if exec_next_execution:
          if fields.datetime.now() < datetime.strptime(exec_next_execution.execution_details,date_format):
             return

        (hst, usr, pss, dab) = self.get_from_parameter_or_val(override_con_det)
        exec_track = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Shipto')
        ofst = "0"
        nextofst = "0"
        max_processes = 200
        where_track = False

        if exec_track:
          ofst = exec_track.execution_details

        if exec_next_execution:
            next_date = pytz.utc.localize(
                exec_next_execution.last_execution_time)
            next_date = next_date.astimezone(
                pytz.timezone('Asia/Kuala_Lumpur'))
            where_track = "ChangeDate >= '" + \
                next_date.strftime(sql_format) + "'"

        offsetqry = "OFFSET " + ofst  + " ROWS FETCH NEXT " + str(max_processes)  + " ROWS ONLY"
        qry = self.env['res.partner'].sudo().build_shipto_sync_query(where_track,offsetqry)

        reslt = self.get_mssql_query(hst, usr, pss, dab, qry)
        resltcount = len(reslt)
        self.env['res.partner'].sudo().process_shipto_data(reslt)

        if resltcount == max_processes:
          incofst = int(ofst) + max_processes
          nextofst = str(incofst)
        else:
          nxt_hours = self.env['ir.config_parameter'].sudo().get_param('vpn.connect.next_execution_hours')
          if not nxt_hours:
            nxt_hours = "4" # 4 is 12pm in GMT+8
          nxt_exec_date = datetime.now().replace(minute=0, hour=int(nxt_hours), second=0)
          nxt_exec_date += timedelta(days=1)
          self.env['starken_crm.mssql.track'].sudo().set_execution_track('Shipto_next_execution',nxt_exec_date.strftime(date_format))

        self.env['starken_crm.mssql.track'].sudo().set_execution_track('Shipto',nextofst)
      except Exception as e:
        error_msg = str(e)
        error_msg_md5 = hashlib.md5(error_msg.encode()).hexdigest()
        _logger.exception('Error on syncing Epicor systems via VPN :\n %s' % error_msg)
        error_equiv = self.env['starken_crm.mssql.track'].sudo().get_execution_track('Shipto_error_%s'%error_msg_md5)
        report = True
        if error_equiv:
          difference_in_time = datetime.now() - datetime.strptime(error_equiv.execution_details,date_format)
          if difference_in_time.total_seconds() < 86400: # If less than 24 hours in seconds form
            self.env['starken_crm.mssql.track'].sudo().set_execution_track('Shipto_error_%s'%error_msg_md5,datetime.now().strftime(date_format)) # Extend the error forever if keep appearing.Only need to send once
            report = False
        if report:
          self.env['starken_crm.mssql.track'].sudo().set_execution_track('Shipto_error_%s'%error_msg_md5,datetime.now().strftime(date_format))
          self.notify_users_on_fail('Error on syncing Shipto over VPN from Epicor Systems', error_msg, 'vpn_fail_email_template_products_notf_email')

    def get_shipto_address_from_db(self, address_id, customer_n, company_code, override_con_det=False):
        rtn_val = []
        date_format = "%m/%d/%Y, %H:%M:%S"
        sql_format = "%Y-%m-%d %H:%M:%S.000"
        try:
            (hst, usr, pss, dab) = self.get_from_parameter_or_val(override_con_det)
            qry = self.env['res.partner'].sudo().build_get_shipto_address_query(address_id, customer_n, company_code)

            reslt = self.get_mssql_query(hst, usr, pss, dab, qry)
            rtn_val = self.env['res.partner'].sudo().get_shipto_address(reslt)

            return False, rtn_val
        except Exception as e:
            err_msg = 'getting existing ship to id %s' % address_id
            error_msg = str(e)

            err_msg_format = 'Error on %s from Epicor systems via VPN : \n %s ' % (err_msg, error_msg)
            error_msg_md5 = hashlib.md5(error_msg.encode()).hexdigest()
            _logger.exception('Shipto address from db sync: Syncing encountered an error :\n %s' % error_msg)
            error_equiv = self.env['starken_crm.mssql.track'].sudo().get_execution_track(
                'Shipto_address_from_db_error_%s' % error_msg_md5)
            report = True
            if error_equiv:
                difference_in_time = datetime.now() - datetime.strptime(error_equiv.execution_details, date_format)
                if difference_in_time.total_seconds() < 86400:  # If less than 24 hours in seconds form
                    self.env['starken_crm.mssql.track'].sudo().set_execution_track('Shipto_address_from_db_error_%s' % error_msg_md5,
                                                                                   datetime.now().strftime(
                                                                                       date_format))  # Extend the error forever if keep appearing.Only need to send once
                    report = False
            if report:
                self.env['starken_crm.mssql.track'].sudo().set_execution_track('Shipto_address_from_db_error_%s' % error_msg_md5,
                                                                               datetime.now().strftime(date_format))
                self.notify_users_on_fail('Error on syncing Shipto Address from db over VPN from Epicor Systems', error_msg,
                                          'vpn_fail_email_template_products_notf_email')
            return err_msg_format, []