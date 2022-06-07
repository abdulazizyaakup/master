# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContactSubStage(models.TransientModel):
    _name = 'applicant.wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Wizard'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    applicant_id = fields.Many2one('hr.applicant', string="Applicant", default=_default_applicant)
    contact_stage = fields.Many2one('contact.substage','Contact Stage')
    contact_comment = fields.Text('Comment')

    @api.multi
    @api.onchange('contact_stage')
    def status(self):
        for a in self.applicant_id:
            stat = self.contact_stage.id
            comment = self.contact_comment
            a.write({'contact_stage': stat, 'contact_comment': comment})
        return {'type': 'ir.actions.act_window_close'}
