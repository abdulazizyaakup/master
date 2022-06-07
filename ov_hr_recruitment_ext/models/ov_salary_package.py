# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, _

class OvSalaryPackage(models.Model):
    _name = 'ov.salarypackage'
    _inherit = ['mail.thread','mail.activity.mixin']

    #name = fields.Char("Name")
    name = fields.Selection([
        ('SCDSGSO18','SCDSGSO18'),
        ('SCDSGSO213','SCDSGSO213'),
        ('SCDSGSO323','SCDSGSO323'),
        ('SCDSGSS1','SCDSGSS1'),
        ('SCDSGSSO1','SCDSGSSO1'),
        ('SCMMYSO2145','SCMMYSO2145'),
        ('SCMMYSO2145P','SCMMYSO2145P'),
        ('SCMMYSS2365','SCMMYSS2365'),
        ('SCMMYSS2365P','SCMMYSS2365P'),
        ('SCMMYSSO2255','SCMMYSSO2255'),
        ('SCMMYSSO2255P','SCMMYSSO2255P'),
        ('SCMMYSO145','SCMMYSO145'),
        ('SCMMYSO145P','SCMMYSO145P'),
        ('SCMMYSS1265','SCMMYSS1265'),
        ('SCMMYSS1265P','SCMMYSS1265P'),
        ('SCMMYSSO1155','SCMMYSSO1155'),
        ('SCMMYSSO1155P','SCMMYSSO1155P'),
        ('SCMSGSO2100','SCMSGSO2100'),
        ('SCMSGSO2100P','SCMSGSO2100P'),
        ('SCMSGSS1','SCMSGSS1'),
        ('SCMSGSS1P','SCMSGSS1P'),
        ('SCMSGSSO1','SCMSGSSO1'),
        ('SCMSGSSO1P','SCMSGSSO1P'),
        ('SCMSGSSS1','SCMSGSSS1'),
        ('SCMSGSSS1P','SCMSGSSS1P'),
        ], "Salary Code", required=True,track_visibility='always')
    #job_title = fields.Many2one('hr.job','Job Title',)
    #country_id = fields.Many2one("res.country", "Country")
    type_of_package = fields.Selection([
        ('daily','Daily'),
        ('monthly','Monthly'),
        ], "Salary Scheme", help='Type of appoinment i.e: Full-Time/Part-Time')
    payment_schedule = fields.Selection([
        ('daily','Daily'),
        ('monthly','Monthly'),
        ], "Salary Scheme", help='Type of appoinment i.e: Full-Time/Part-Time')
    time = fields.Selection([
        ('730am730pm','7.30 am – 7.30 pm'),
        ('800am800pm','8.00 am – 8.00 pm'),
        ('730pm730am','7.30 pm – 7.30 am'),
        ('800pm800am','8.00 pm – 8.00 am'),
        ], "Shift")
    basic_salary = fields.Float("Basic Salary")
    ot = fields.Float("Overtime")
    mvc = fields.Float("Monthly Variable Component")
    pis = fields.Float("Productivity Incentive")
    awbr = fields.Float("Attendance & Bonus Reward")
    #gross_salary = fields.Float("Gross Salary",compute='_gross_amount',store=True)
    
    # @api.one
    # def _get_total_gross(self):
    #     total = self.gross_salary
    #     try:
    #         total = sum(self.basic_salary+self.ot+self.mvc+self.pis+self.awbr)
    #     except:
    #         raise "Calculation Error"
    #         #salary.gross_salary = sum(salary.basic_salary+salary.ot+salary.mvc+salary.pis+salary.awbr)
    #     return total

    # @api.one
    # def _gross_amount(self):  
    #     for gross in self:      
    #         comm_total = self.basic_salary+self.ot+self.mvc+self.pis+self.awbr
    #         gross.update({'gross_salary': comm_total })


    @api.multi
    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            if ((self.name == 'SCDSGSO18') or (self.name == 'SCDSGSO213') or (self.name == 'SCDSGSO323') or (self.name == 'SCDSGSS1') or (self.name == 'SCDSGSSO1')):
                self.type_of_package = 'daily'
            else:
                self.type_of_package = 'monthly'
