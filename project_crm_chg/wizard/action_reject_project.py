# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ActionRejectRequest(models.TransientModel):
    _name = 'action.reject.request'

    reject_reason = fields.Text("Reason")

    def pown_assignment_notification(self, vals, create_id = False):
        self_id = self.env.uid
        # lop_name = False
        lop_name = self.reject_reason
        if 'requestor' in self:
            if vals['user_id'] != self_id and vals['user_id'] != False:
                self.notify_project_requestor(lop_name, 'Requestor', vals['requestor'], self_id, create_id, True)

    def notify_project_requestor(self, lop_name, title, id_to_send, sender_id, create_id, is_user_id = False):
        email_obj = False
        email_template_name = 'emt_set_as_prown_email'
        if not is_user_id:
            recv_user = self.env['res.users'].sudo().search([('requestor','=',id_to_send)], limit=1)
            sndr_user = self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
            if recv_user and sndr_user:
                email_obj = { 'email_list' : [recv_user.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }
        else:
            recv_user = self.env['res.users'].sudo().search([('id','=',id_to_send)], limit=1)
            sndr_user = 'info@chinhingroup.com'#self.env['res.users'].sudo().search([('id','=',sender_id)], limit=1)
            if recv_user and sndr_user:
                 email_obj = { 'email_list' : [recv_user.email] , 'contexts' : { 'assigner_name' : sndr_user.name, 'receiver_name' : recv_user.name, 'title_set_as' : title } }

        message = "Project %s has been rejected by GSM team. %s" % (lop_name, title)

        if email_obj:
            self.send_email(email_obj['email_list'], message, email_template_name, email_obj['contexts'], create_id)


    def action_reject(self):
        val = self.env['master.project'].browse(self._context.get('active_ids'))
        reason = self.reject_reason
        #self.notify_project_requestor()
        return val.write({'stage_id':'cancelled','reject_reason':reason})
