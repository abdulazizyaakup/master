# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _name = 'tender.wizard'
    _description = 'Wizard'

    def _default_tender(self):
        return self.env['ov.tender'].browse(self._context.get('active_ids'))

    #session_ids = fields.Many2many('openacademy.session', string="Sessions", required=True, default=_default_sessions)
    #attendee_ids = fields.Many2many('res.partner', string="Attendees")
    tender_ids = fields.Many2many('ov.tender', string="Tenders", required=True, default=_default_tender)
    partner_ids = fields.Many2many('res.partner', string="Partner")

    # @api.multi
    # def subscribe(self):
        #for tender in self.tender_ids:
        #    att_ids = tender.partner_ids.ids + self.partner_ids.ids
        #    tender.write({'partner_ids': [(6, 0, att_ids)]})
        #return {'type': 'ir.actions.act_window_close'}
        #cr.execute("INSERT INTO res_partner (code,name,active) VALUES ('%s','%s','1')" %(code,name)) 
        # self.env.cr.execute("INSERT INTO ov_tender_res_partner_rel (ov_tender_id, res_partner_id) VALUES (1, 7)")
        # return True


    # @api.multi
    # def subscribe(self):
    #     id_needed = []
    #     #kw = self.partner_ids.ids
    #     #a_id = 5
    #     keyword = self.env['ov.tender'].search([('name','!=',False)])
    #     partner_ids = self.env['res.partner'].search([('keywords_ids', '!=', False)])
    #     #td = self.env['ov.tender'].browse(self._context.get('active_ids'))
    #     id_needed = partner_ids.search([('keywords_ids', 'like', keyword)])
    #     #new = wt.browse(id_needed)
    #     #keys = self.description
    #     if id_needed:
    #         print("XXXXX")
    #         print(id_needed)
    #     else:
    #         print("YYYYY")
    #         print("Failed")
        # if keys: