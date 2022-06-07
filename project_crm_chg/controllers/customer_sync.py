from requests import api
from requests.models import Response
from odoo import http
from odoo.http import request
from odoo.addons.restful.controllers.main import validate_token
from odoo.addons.restful.common import invalid_response, valid_response
import requests
from requests.auth import HTTPBasicAuth

class CustomerSync(http.Controller):

  # @validate_token
  @http.route('/get_epicor/customer/id', website=True, auth='public')
  def get_epicor(self, **kw):

    try:
      epicor_customer = request.env['res.partner'].sudo().search([])
      # epicor customer id 
      epicor_customer_id = []

      epicor_api_customer = []

      new_customer_id = []

      # all the data from epicor api
      # open vpn before use 
      link = requests.get("https://172.16.1.12/STRKLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27SAAC%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)
      link_metex = requests.get("https://172.16.1.10/MTEXLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27MSSB%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)
      link_chc = requests.get("https://172.16.1.11/CHCGLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27CHCKL%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)
      link_midah = requests.get("https://172.16.1.111/MISBLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27MISB%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)


      for ec in epicor_customer:
        if (ec.epicor_customer_id):
          epicor_customer_id.append(ec.epicor_customer_id)

      hs = set(epicor_customer_id)

      for eaci in link.json()["value"]:
        if (eaci["Customer_CustID"] in hs):
          epicor_api_customer.append(eaci["Customer_CustID"])
        else:
          data = {
            "name": eaci["Customer_Name"],
            "company_code" : eaci["Company_Code"],
            "customer_code": eaci["Customer_CustNum"],
            "customer_id": eaci["Customer_CustID"],
            "street": eaci["Customer_Address1"],
            "street2": eaci["Customer_Address2"] + ' ' + eaci["Customer_Address3"],
            "street3": eaci["Customer_Address3"],
            "city": eaci["Customer_City"],
            "zip": eaci["Customer_Zip"],
            "fax": eaci["Customer_FaxNum"],
            "phone": eaci["Customer_PhoneNum"],
          }

      for eaci_chc in link_chc.json()["value"]:
        if (eaci_chc["Customer_CustID"] in hs):
          epicor_api_customer.append(eaci_chc["Customer_CustID"])
        else:
          data = {
            "name": eaci_chc["Customer_Name"],
            "company_code" : eaci_chc["Company_Code"],
            "customer_code": eaci_chc["Customer_CustNum"],
            "customer_id": eaci_chc["Customer_CustID"],
            "street": eaci_chc["Customer_Address1"],
            "street2": eaci_chc["Customer_Address2"] + ' ' + eaci_chc["Customer_Address3"],
            "street3": eaci["Customer_Address3"],
            "city": eaci_chc["Customer_City"],
            "zip": eaci_chc["Customer_Zip"],
            "fax": eaci_chc["Customer_FaxNum"],
            "phone": eaci_chc["Customer_PhoneNum"],
          }

      for eaci_metex in link_metex.json()["value"]:
        if (eaci_metex["Customer_CustID"] in hs):
          epicor_api_customer.append(eaci_metex["Customer_CustID"])
        else:
          data = {
            "name": eaci_metex["Customer_Name"],
            "company_code" : eaci_metex["Company_Code"],
            "customer_code": eaci_metex["Customer_CustNum"],
            "customer_id": eaci_metex["Customer_CustID"],
            "street": eaci_metex["Customer_Address1"],
            "street2": eaci_metex["Customer_Address2"] + ' ' + eaci_metex["Customer_Address3"],
            "street3": eaci["Customer_Address3"],
            "city": eaci_metex["Customer_City"],
            "zip": eaci_metex["Customer_Zip"],
            "fax": eaci_metex["Customer_FaxNum"],
            "phone": eaci_metex["Customer_PhoneNum"],
          }

      for eaci_midah in link_midah.json()["value"]:
        if (eaci_midah["Customer_CustID"] in hs):
          epicor_api_customer.append(eaci_midah["Customer_CustID"])
        else:
          data = {
            "name": eaci_midah["Customer_Name"],
            "company_code" : eaci_midah["Company_Code"],
            "customer_code": eaci_midah["Customer_CustNum"],
            "customer_id": eaci_midah["Customer_CustID"],
            "street": eaci_midah["Customer_Address1"],
            "street2": eaci_midah["Customer_Address2"] + ' ' + eaci_midah["Customer_Address3"],
            "street3": eaci["Customer_Address3"],
            "city": eaci_midah["Customer_City"],
            "zip": eaci_midah["Customer_Zip"],
            "fax": eaci_midah["Customer_FaxNum"],
            "phone": eaci_midah["Customer_PhoneNum"],
          }


          # get token from postman and replace the 'access_token'
          headers = {'Content-type': 'application/x-www-form-urlencoded', 'access_token': 'access_token_9008cd310f736ab92b19036bedf1e512ce95a5c4'}
          response = requests.post("https://groupcrm.chinhingroup.com/odoo/partner", data=data, headers=headers)
          new_customer_id.append(response.json()["data"]["odoo_id"])
    except Exception as exception:
      return invalid_response({'message':"Customer is Sync Unuccessfully",
                               'details': str(exception),
                               'status': 401})
    return valid_response({'message': "Customer is Sync Successfully",
                           'status': 200,
                           'odoo_id': new_customer_id})
