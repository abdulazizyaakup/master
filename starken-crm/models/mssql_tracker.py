from odoo import api, fields, models, tools 
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)



class MSSQLQueryTracker(models.Model):
    _name = 'starken_crm.mssql.track'
    _description = "MSSQL Query Tracker"

    name = fields.Char('Execution Tags')
    last_execution_time = fields.Datetime('Last Execution Time')
    execution_details = fields.Text('Execution Description')

    def get_execution_track(self, exc_tag):
      return self.sudo().search([('name','=', exc_tag)], limit=1)

    def set_execution_track(self, exc_tag, exc_details = False):
      found_tags = self.sudo().search([('name','=', exc_tag)], limit=1)
      if not found_tags:
        self.sudo().create({'name' : exc_tag, 'last_execution_time' : fields.datetime.now(), 'execution_details' : exc_details})
      else:
        if found_tags.execution_details != exc_details:
          found_tags.write({'last_execution_time' : fields.Datetime.now(), 'execution_details' : exc_details})
        else:
          found_tags.write({'last_execution_time' : fields.Datetime.now()})
        