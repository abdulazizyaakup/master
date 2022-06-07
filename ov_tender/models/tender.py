# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _
from urllib.request import urlopen, Request
import re
from bs4 import BeautifulSoup
import requests
import json
from threading import Thread
from xml.dom import minidom
import datetime
from datetime import datetime, timedelta
import pytz

date = datetime.strptime('26 Sep 2012', '%d %b %Y')
newdate = date.replace(hour=11, minute=59)

class MarketingParticipantExt(models.Model):
    _inherit = 'marketing.participant'

    def keep_running(self):
        existing_traces = self.env['marketing.trace'].search([
            ('participant_id', 'in', self.ids),
            ('state', '=', 'scheduled'),
        ])
        (self - existing_traces.mapped('participant_id')).write({'state': 'running'})


class Tender(models.Model):
    _name = 'ov.tender'
    _description = 'Tenders'
    _order = 'start_date desc'


    def _default_past_date(self):
        current_date = datetime.now()
        now_minus_12 = datetime.now() - timedelta(hours=24)
        new_now_minus_12 = now_minus_12.replace(hour=10, minute=00)
        return new_now_minus_12

    def _default_future_date(self):
        current_date = datetime.now()
        now_plus_12 = datetime.now() + timedelta(hours=24)
        new_now_plus_12 = now_plus_12.replace(hour=10, minute=00)
        return new_now_plus_12


    name = fields.Char(required=True)
    quotation_number = fields.Char('Quotation No.')
    start_date = fields.Datetime(string='Start Date')
    #start_date = fields.Datetime(string='Start Date'default=lambda self : fields.Date.today())
    end_date = fields.Datetime(string='End date') #, inverse='_set_end_date'
    active = fields.Boolean(default=True)
    category = fields.Char('Category')
    awarding_agency = fields.Char('Awarding Agency')
    url = fields.Char(string="Url")
    url2= fields.Char(string="Url2")
    tender_ids = fields.Many2many('res.partner', string="Attendees")
    description = fields.Text()
    tender_id = fields.Many2one('res.partner', ondelete='cascade', string="Partner")
    partner_ids = fields.Many2many('res.partner', string="Customer")
    status = fields.Char('Status')
    p_date = fields.Datetime(string="Previous Date", default=_default_past_date,required=True)
    f_date = fields.Datetime(string="Next Date", default=_default_future_date,required=True)
    is_included = fields.Integer("Includes in Next Email", compute="check_date_period", store=True)

    #Scrapping
    def header(self):
        xml = """    <website name="gebiz">
        <category name="Transportation">
            <description name="Moving Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Bus Hire Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Car Rental Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Other Vehicle Rental Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Ticketing, Travel Services, Tours &amp; Excursions Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Petroleum, Oil &amp; Lubricants Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Vehicle Maintenance Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="ShipBuilding, Marine Supplies c Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/ShipBuilding,_Marine_Supplies_&amp;_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/ShipBuilding,_Marine_Supplies_&amp;_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Others Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml</url>
            </description>
        </category>
         <category name="Services">
            <description name="Advertising Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Childcare Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Data Entry, Supply of Manpower Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_BO_FEED.xml">    https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_AWD_FEED.xml">   https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Disposal and Management of Waste Chemicals Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_BO_FEED.xml"> https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_AWD_FEED.xml">    https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Grooming Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Laundry Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Public Relations &amp; Counselling Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_AWD_FEED.xml">    https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Storage Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Tailoring Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Tailoring-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Tailoring-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Tailoring-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Tailoring-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Undertaker Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Professional Services Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_AWD_FEED.xml</url>
            </description>
        </category>
        <category name="Workshop Equipment and Services">
            <description name="Workshop Machinery, DIY Machinery &amp; Supplies Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_AWD_FEED.xml</url>
            </description>
             <description name="Workshop Tools, DIY Tools &amp; Accessories Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_AWD_FEED.xml</url>
            </description>
             <description name="Workshop Tools Maintenance Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_AWD_FEED.xml</url>
            </description>
             <description name="Workshop Furniture Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_AWD_FEED.xml</url>
            </description>
        </category>
        <category name="IT &amp; Telecommunication">
            <description name="Telecommunication Devices Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Desktop Computers Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Servers Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Servers-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Servers-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Servers-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Servers-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Notebooks Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Notebooks-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Notebooks-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Notebooks-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Notebooks-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Storage Devices &amp; Drives Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Computer Accessories Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Printers &amp; Scanners Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Personal Digital Assistants Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Softwares &amp; Licences Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="IT Services &amp; Software Development Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_AWD_FEED.xml</url>
            </description>
              <description name="Others Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_BO_FEED.xml</url>
                 <url name="https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_AWD_FEED.xml</url>
            </description>
        </category>
        <category name="Others">
            <description name="Others Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_AWD_FEED.xml</url>
            </description>
        </category>
        <category name="Construction">
            <description name="General Building &amp; Minor Construction Works Business Opportunity Award">
                <url name="https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_BO_FEED.xml">    https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_BO_FEED.xml</url>
                <url name="https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_AWD_FEED.xml">   https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_AWD_FEED.xml</url>
            </description>
            <description name="Civil Engineering Business Opportunity">
                <url name="https://www.gebiz.gov.sg/rss/Civil_Engineering-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Civil_Engineering-CREATE_BO_FEED.xml</url>
            </description>
        </category>
    </website>"""
        xmldoc = minidom.parseString(xml)
        category = xmldoc.getElementsByTagName('category')
        data = []
        jsonObj = {}
        for c in category:
            itemList = c.getElementsByTagName('url')
            for s in itemList:
                reg_url = s.attributes['name'].value
                category = c.attributes['name'].value
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
                r = requests.get(reg_url, headers=headers)
                html = r.text

                # print(html)
                patFinderLink = re.compile('<link>(.*)</link>')
                findPatLink = re.findall(patFinderLink, html)

                listIterator = []
                listIterator[:] = range(1,len(findPatLink))

                # print(findPatLink)
                link = 'https://www.gebiz.gov.sg'
                for path in findPatLink:
                    if(path == 'https://www.gebiz.gov.sg'):
                        findPatLink.remove(link)
                    else:
                        continue

                for item in findPatLink:
                    page_url = item
                    req = Request(url=page_url, headers=headers)
                    html = urlopen(req).read().decode('utf-8')
                    soup = BeautifulSoup(html, 'lxml')

                    # Name
                    nameTitle = soup.find('div', class_='formOutputText_HIDDEN-LABEL outputText_TITLE-BLACK')
                    nameTitle = nameTitle.text

                    # End Date
                    end = soup.findAll('div', class_='formOutputText_HIDDEN-LABEL outputText_NAME-BLACK')
                    for br in soup.findAll("br"):
                        br.replace_with(' ')
                    for i in end:
                        endDate = i.text
                        e_vals = ["AM","PM"]
                        eDt = endDate
                        for e in e_vals:
                            if (e in eDt):
                                new_eDt = new_dt = eDt.replace(e,"")
                                endDate = new_eDt
                            else:
                                endDate = eDt

                    # Start Date && Quotation No
                    div_class = soup.findAll('div', class_='formOutputText_VALUE-DIV')
                    for index, q in enumerate(div_class):
                        if index == 0:
                            quotationNum = q.text
                        if index == 13:
                            awarding_agency = q.text
                        if index == 3:
                            startDate = q.text
                            t_vals = ["AM","PM"]
                            sDt = startDate
                            for t in t_vals:
                                if (t in sDt):
                                    new_sDt = new_dt = sDt.replace(t,"")
                                    startDate = new_sDt
                                else:
                                    startDate = sDt

                    #Description
                    desc = soup.find('div', class_='formOutputText_HIDDEN-LABEL outputText_DESCRIPTION-GRAY')
                    desc = desc.text

                    #Status
                    status_string = soup.findAll('div', class_='formSectionHeader3_MAIN')
                    for i in status_string:
                        open_status = i.find('div', class_='label_MAIN label_WHITE-ON-GRAY')
                        awarded_status = i.find('div', class_='label_MAIN label_WHITE-ON-GREEN')
                        if (open_status != None):
                            status = open_status.text
                        elif (awarded_status != None):
                            status = awarded_status.text

                    tender = self.env['ov.tender'].search([])
                    quote_no = tender.mapped('quotation_number')
                    new_qv = []
                    for qv in quote_no:
                        if qv:
                            new_qv.append(qv)

                    jsonObj = {}
                    x = datetime.now()
                    date_vals = [startDate]
                    quotation_vals = [quotationNum]
                    for q_vals in quotation_vals:
                        for dt_vals in date_vals:
                            now_dt = x.strftime("%d %b %Y")
                            if (now_dt in dt_vals):
                                if new_qv:
                                    if (q_vals not in new_qv):
                                        jsonObj = { 'name': nameTitle, 'quotation_number': quotationNum ,'start_date': startDate, 'end_date': endDate, 'url': page_url, 'description': desc, 'category': category, 'awarding_agency': awarding_agency, 'status': status }
                                        self.env['ov.tender'].create(jsonObj)
                                    elif (q_vals in new_qv):
                                        pass
                                    else:
                                        continue
                                else:
                                    jsonObj = { 'name': nameTitle, 'quotation_number': quotationNum ,'start_date': startDate, 'end_date': endDate, 'url': page_url, 'description': desc, 'category': category, 'awarding_agency': awarding_agency, 'status': status }
                                    self.env['ov.tender'].create(jsonObj)

    def check_date_period(self):
    #if now-timedelta(hours=24) <= set_date <= now+timedelta(hours=24):
        current_date = datetime.now()
        tender_ids = self.env['ov.tender'].search([])
        for tend in tender_ids:
            s_date = tend.start_date
            difference = current_date - s_date
            # print(difference)
            if ((difference.days == 0) or (difference.days == -1)) :
                tend.is_included = 1
                #print("ID :", tend.id , "CURRENT :", current_date ," START DATE :",s_date, " IS WITHIN 24 HOURS ", difference)
            if difference.days >= 1:
                tend.is_included = 0
                #print("ID :", tend.id , "CURRENT :", current_date ," START DATE :",s_date, " IS NOT WITHIN 24 HOURS ", difference)

#    @api.depends('url')
#    def get_url(self):
#        tenders = self.env['ov.tender'].search([])
#        for t in tenders:
#            text = 'Link'
#            val = t.url
#            t.url2 = val
