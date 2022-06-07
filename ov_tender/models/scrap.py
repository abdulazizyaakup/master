from urllib.request import urlopen, Request
import re
from bs4 import BeautifulSoup
import requests
import json
from threading import Thread
from xml.dom import minidom
from odoo import models, fields, api, exceptions, _


class Scrap(models.Model):
    _name = 'ov.scrap'
    # def header():
    #     xml = """    <website name="gebiz">
    #     <category name="Transportation">
    #         <description name="Moving Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Moving_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Bus Hire Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Bus_Hire-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Car Rental Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Car_Rental-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Other Vehicle Rental Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Other_Vehicle_Rental-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Ticketing, Travel Services, Tours &amp; Excursions Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Ticketing,_Travel_Services,_Tours__&amp;_Excursions-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Petroleum, Oil &amp; Lubricants Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Petroleum,_Oil_&amp;_Lubricants-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Vehicle Maintenance Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Vehicle_Maintenance-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="ShipBuilding, Marine Supplies c Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/ShipBuilding,_Marine_Supplies_&amp;_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/ShipBuilding,_Marine_Supplies_&amp;_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Others Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersTransportation-CREATE_BO_FEED.xml</url>
    #         </description>
    #     </category>
    #      <category name="Services">
    #         <description name="Advertising Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Advertising_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Childcare Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Childcare_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Data Entry, Supply of Manpower Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_BO_FEED.xml">    https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_AWD_FEED.xml">   https://www.gebiz.gov.sg/rss/Data_Entry,_Supply_of_Manpower_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Disposal and Management of Waste Chemicals Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_BO_FEED.xml"> https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_AWD_FEED.xml">    https://www.gebiz.gov.sg/rss/Disposal_and_Management_of_Waste_Chemicals-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Grooming Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Grooming_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Laundry Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Laundry_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Public Relations &amp; Counselling Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_AWD_FEED.xml">    https://www.gebiz.gov.sg/rss/Public_Relations_&amp;_Counselling-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Storage Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Tailoring Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Tailoring-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Tailoring-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Tailoring-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Tailoring-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Undertaker Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Undertaker_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Professional Services Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Professional_Services-CREATE_AWD_FEED.xml</url>
    #         </description>
    #     </category>
    #     <category name="Workshop Equipment and Services">
    #         <description name="Workshop Machinery, DIY Machinery &amp; Supplies Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Machinery,_DIY_Machinery_&amp;_Supplies-CREATE_AWD_FEED.xml</url>
    #         </description>
    #          <description name="Workshop Tools, DIY Tools &amp; Accessories Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools,_DIY_Tools_&amp;_Accessories-CREATE_AWD_FEED.xml</url>
    #         </description>
    #          <description name="Workshop Tools Maintenance Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Tools_Maintenance-CREATE_AWD_FEED.xml</url>
    #         </description>
    #          <description name="Workshop Furniture Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Workshop_Furniture-CREATE_AWD_FEED.xml</url>
    #         </description>
    #     </category>
    #     <category name="IT &amp; Telecommunication">
    #         <description name="Telecommunication Devices Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Telecommunication_Devices-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Desktop Computers Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Desktop_Computers-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Servers Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Servers-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Servers-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Servers-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Servers-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Notebooks Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Notebooks-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Notebooks-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Notebooks-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Notebooks-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Storage Devices &amp; Drives Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Storage_Devices_&amp;_Drives-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Computer Accessories Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Computer_Accessories-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Printers &amp; Scanners Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Printers_&amp;_Scanners-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Personal Digital Assistants Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Personal_Digital_Assistants-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Softwares &amp; Licences Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/Softwares_&amp;_Licences-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="IT Services &amp; Software Development Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/IT_Services_&amp;_Software_Development-CREATE_AWD_FEED.xml</url>
    #         </description>
    #           <description name="Others Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_BO_FEED.xml</url>
    #              <url name="https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/OthersIT&amp;Telecommunication-CREATE_AWD_FEED.xml</url>
    #         </description>
    #     </category>
    #     <category name="Others">
    #         <description name="Others Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_AWD_FEED.xml">https://www.gebiz.gov.sg/rss/OthersOthers-CREATE_AWD_FEED.xml</url>
    #         </description>
    #     </category>
    #     <category name="Construction">
    #         <description name="General Building &amp; Minor Construction Works Business Opportunity Award">
    #             <url name="https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_BO_FEED.xml">    https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_BO_FEED.xml</url>
    #             <url name="https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_AWD_FEED.xml">   https://www.gebiz.gov.sg/rss/General_Building_&amp;_Minor_Construction_Works-CREATE_AWD_FEED.xml</url>
    #         </description>
    #         <description name="Civil Engineering Business Opportunity">
    #             <url name="https://www.gebiz.gov.sg/rss/Civil_Engineering-CREATE_BO_FEED.xml">https://www.gebiz.gov.sg/rss/Civil_Engineering-CREATE_BO_FEED.xml</url>
    #         </description>
    #     </category>
    # </website>"""
    #     xmldoc = minidom.parse(xml)
    #     category = xmldoc.getElementsByTagName('category')
    #     for c in category:
    #         itemList = c.getElementsByTagName('url')
    #         for s in itemList:
    #             reg_url = s.attributes['name'].value
    #             category = c.attributes['name'].value
    #             headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    #             r = requests.get(reg_url, headers=headers)
    #             html = r.text

    #             # print(html)
    #             patFinderLink = re.compile('<link>(.*)</link>')
    #             findPatLink = re.findall(patFinderLink, html)

    #             listIterator = []
    #             listIterator[:] = range(1,len(findPatLink))

    #             # print(findPatLink)
    #             findPatLink.remove('https://www.gebiz.gov.sg')

    #             for item in findPatLink:
    #                 page_url = item
    #                 req = Request(url=page_url, headers=headers)
    #                 html = urlopen(req).read().decode('utf-8')
    #                 soup = BeautifulSoup(html, 'lxml')

    #                 # Name
    #                 nameTitle = soup.find('div', class_='formOutputText_HIDDEN-LABEL outputText_TITLE-BLACK')
    #                 nameTitle = nameTitle.text

    #                 # Start Date
    #                 start = soup.findAll('div', {'id':'contentForm:j_idt242'}, class_='form2_ROW')
    #                 for i in start:
    #                     startDate = i.find('div', class_='formOutputText_VALUE-DIV')
    #                     startDate = startDate.text

    #                 # End Date
    #                 end = soup.findAll('div', {'id':'contentForm:j_idt279'}, class_='form2_ROW form2_ROW-NO-PADDING-BOTTOM form2_ROW-NO-PADDING-TOP')
    #                 for i in end:
    #                     endDate =  i.find('div', class_='formOutputText_HIDDEN-LABEL outputText_NAME-BLACK')
    #                     endDate = endDate.text
    #                 for br in soup.findAll("br"):
    #                     br.replace_with(' ')

    #                 #Url
    #                 # print('Url:', page_url)

    #                 #Description
    #                 desc = soup.find('div', class_='formOutputText_HIDDEN-LABEL outputText_DESCRIPTION-GRAY')
    #                 desc = desc.text

    #                 jsonObj = { 'name': nameTitle, 'start_date': startDate, 'end_date': endDate, 'url': page_url, 'description': desc, 'category': category }
    #                 print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    #                 print (jsonObj)


    #print(header())
