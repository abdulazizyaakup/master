# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ApplicantBlacklistWizard(models.TransientModel):
    _name = 'applicant.blacklist'
    _description = 'Blacklist Wizard'

    def _default_ats(self):
        val = self.env['hr.applicant'].browse(self._context.get('active_ids'))
        return val.id

    applicant_ids = fields.Many2one('hr.applicant', string="Application", default=_default_ats)
    blacklist_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    blacklist_reason = fields.Text("Reason")

    @api.multi
    def blacklist_record(self):
        res = self.applicant_ids
        default_stage_id_blacklist = self.env['hr.recruitment.stage'].search([('name', '=', 'Blacklisted')]).id
        res.write({'blacklist_date': self.blacklist_date, 'blacklist_note': self.blacklist_reason ,'blacklist': True,'application': False,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_blacklist})

        # self.env['employee.resignation.details'].create({
        #     'applicant_id': app_ids.id,
        #     'resignation_date': self.resignation_date,
        #     'resignation_reason': self.resignation_reason
        #     })

        return {'type': 'ir.actions.act_window_close'}

