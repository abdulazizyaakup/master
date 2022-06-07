# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
import os, json
import requests
import base64
import binascii
import struct
import PyPDF2
import time
from odoo import _

class SaveAttachment(http.Controller):

    @http.route(['/web/test/'], csrf=False, type='http', auth="public",  website = True)
    def test(self, **kwargs):
        # try:
        #     strImageName
        #     HttpFileCollection files = HttpContext.Current.Request.Files
        #     HttpPostedFile uploadfile = files["RemoteFile"]
        #     strImageName = uploadfile.FileName

        #     uploadfile.SaveAs(Server.MapPath(".") + "\\UploadedImages\\" + strImageName);
        print("This is a test")

    @http.route(['/attachment/save'], csrf=False, type='json', methods=['GET','POST'], auth="user",  website = False)
    def create_docs(self, **kwargs):
        time.sleep(2)
        attachment = request.env['uploaded.file']
        title = kwargs.get('title')
        name = kwargs.get('name')
        description = kwargs.get('description')
        doc_name = kwargs.get('doc_name')
        file_type = kwargs.get('fileType')
        applicant_id = kwargs.get('applicant_id')
        new_applicant_id = int(applicant_id)
        res_model = kwargs.get('res_model')
        user = http.request.env.context.get('uid')
        applicant = request.env['hr.applicant'].sudo().search([])
        app_id = []
        # for app in applicant:
        #     if(app.id == new_applicant_id):
        #         print("APPLICANT NAME:", app)
        if(".pdf" in doc_name):
            filename = ("C:\\Users\\Public\\%s-%s.pdf" % (name,user))
            with open(filename, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                attachment.create({
                    'title': title,
                    'name': name,
                    'description': description,
                    'filetype': file_type,
                    'file': encoded_string,
                    'applicant_id': new_applicant_id,
                    })
        elif(".tiff" in doc_name):
            filename = ("C:\\Users\\Public\\%s-%s.tiff" % (name,user))
            with open(filename, "rb") as tiff_file:
                encoded_string = base64.b64encode(tiff_file.read())
                attachment.create({
                    'title': title,
                    'name': name,
                    'description': description,
                    'filetype': file_type,
                    'file': encoded_string,
                    'applicant_id': new_applicant_id,
                    })
        elif(".png" in doc_name):
            filename = ("C:\\Users\\Public\\%s-%s.png" % (name,user))
            with open(filename, "rb") as png_file:
                encoded_string = base64.b64encode(png_file.read())
                attachment.create({
                    'title': title,
                    'name': name,
                    'description': description,
                    'filetype': file_type,
                    'file': encoded_string,
                    'applicant_id': new_applicant_id,
                    })
        elif(".jpg" in doc_name):
            filename = ("C:\\Users\\Public\\%s-%s.jpg" % (name,user))
            with open(filename, "rb") as jpg_file:
                encoded_string = base64.b64encode(jpg_file.read())
                attachment.create({
                    'title': title,
                    'name': name,
                    'description': description,
                    'filetype': file_type,
                    'file': encoded_string,
                    'applicant_id': new_applicant_id,
                    })
        elif(".bmp" in doc_name):
            filename = ("C:\\Users\\Public\\%s-%s.bmp" % (name,user))
            with open(filename, "rb") as bmp_file:
                encoded_string = base64.b64encode(bmp_file.read())
                attachment.create({
                    'title': title,
                    'name': name,
                    'description': description,
                    'filetype': 'nric',
                    'file': encoded_string,
                    'applicant_id': new_applicant_id,
                    })
        else:
            print("Document Not Found!")




        # print("IDDD : ",user)
        # datas = kwargs.get('datas')
        # # print("XXXX\n", type(datas))
        # # print("YYYY\n", datas)
        # # test = base64.b64encode(datas)
        # test = base64.b64decode(datas)
        # test2 = base64.b64encode(test)
        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx\n",test2)
        # return attachment.create({
        #     'title': name,
        #     'name': name,
        #     'description': name,
        #     'filetype': 'nric',
        #     'file': test2,
        #     })

        """ JADI """

        # with open(filename, "rb") as pdf_file:
        #     encoded_string = base64.b64encode(pdf_file.read())
        #     # print("XXXXXXXXX\n", encoded_string)
        #     # print("YYYYYYYYY\n", type(encoded_string))
        #     return attachment.create({
        #         'title': name,
        #         'name': name,
        #         'description': name,
        #         'filetype': 'nric',
        #         'file': encoded_string,
        #         })