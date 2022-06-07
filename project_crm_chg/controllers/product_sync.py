from requests import api
from requests.models import Response
from odoo import http
from odoo.http import request
from odoo.addons.restful.controllers.main import validate_token
from odoo.addons.restful.common import invalid_response, valid_response
import requests
from requests.auth import HTTPBasicAuth

class ProductSync(http.Controller):

  # @validate_token
  @http.route('/get_epicor/product/id', website=True, auth='public')
  def get_epicor(self, **kw):

    try:
      product = request.env['product.template'].sudo().search([])

      part_number = []

      epicor_api_product = []

      unsync_product = []

      link = requests.get("https://172.16.1.12/STRKLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27SAAC%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)
      link_metex = requests.get("https://172.16.1.10/MTEXLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27MSSB%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)
      link_chc = requests.get("https://172.16.1.11/CHCGLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27CHCKL%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)
      link_midah = requests.get("https://172.16.1.111/MISBLive102/api/v1/BaqSvc/Q_MB_OdooCRM_GetPart?Company=%27MISB%27", auth=HTTPBasicAuth("OdooCRM", "OdooCRM"), verify=False)


      for ep in product:
        if (ep.part_number):
          part_number.append(ep.part_number)

      hs = set(part_number)

      for eapn in link.json()["value"]:
        if (eapn["Part_PartNum"] in hs):
          epicor_api_product.append(eapn["Part_PartNum"])
        else:
          unsync_product.append(eapn)

      for eapn_chc in link_chc.json()["value"]:
        if (eapn_chc["Part_PartNum"] in hs):
          epicor_api_product.append(eapn_chc["Part_PartNum"])
        else:
          unsync_product.append(eapn_chc)

      for eapn_metex in link_metex.json()["value"]:
        if (eapn_metex["Part_PartNum"] in hs):
          epicor_api_product.append(eapn_metex["Part_PartNum"])
        else:
          unsync_product.append(eapn_metex)

      for eapn_midah in link_midah.json()["value"]:
        if (eapn_midah["Part_PartNum"] in hs):
          epicor_api_product.append(eapn_midah["Part_PartNum"])
        else:
          unsync_product.append(eapn_midah)

      for up in unsync_product:
        data = {
          "name": up["Part_PartNum"],
          "list_price": up["Part_UnitPrice"],
          "part_number": up["Part_PartNum"],
          # "company_id": up["Company"],
          "uom": up["Part_IUM"],
          "po_uom": up["Part_PUM"],
          "description_sale": up["Part_PartDescription"],
          "pro_group": up["Part_ProdCode"],
          "pro_class": up["Part_ClassID"],
          "company_code": up["Part_Company"]
          # "type": up["Part_TypeCode"],
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded', "access_token": "access_token_9008cd310f736ab92b19036bedf1e512ce95a5c4"}
        response = requests.post("https://groupcrm.chinhingroup.com/odoo/product", data=data, headers=headers)
    except Exception as exception:
      return invalid_response({'message':"Product is Sync Unuccessfully",
                               'details': str(exception),
                               'status': 401})
    return valid_response({'message': "Product is Sync Successfully",
                           'status': 200})
