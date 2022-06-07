# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ApplicantBannedWizard(models.TransientModel):
    _name = 'applicant.banned'
    _description = 'Banned Wizard'

    def _default_ats(self):
        val = self.env['hr.applicant'].browse(self._context.get('active_ids'))
        return val.id

    applicant_ids = fields.Many2one('hr.applicant', string="Application", default=_default_ats)
    banned_date = fields.Date(string='Date',default=lambda self : fields.Date.today())
    # banned_from_site = fields.Boolean('Banned from Project Site?')
    # banned_project_site = fields.Many2many()
    banned_reason = fields.Text("Reason")

    @api.multi
    def banned_record(self):
        res = self.applicant_ids
        default_stage_id_banned = self.env['hr.recruitment.stage'].search([('name', '=', 'Banned')]).id
        res.write({'banned_date': self.banned_date, 'banned_note': self.banned_reason,'banned':True,'blacklist': False,'application': False,'enquiry': False,'iv': False ,'application': False, 'stage_id': default_stage_id_banned})

        return {'type': 'ir.actions.act_window_close'}

