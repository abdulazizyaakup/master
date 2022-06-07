from odoo import api, fields, models, tools 

class Users(models.Model):
    _inherit = 'res.users'

    action_id = fields.Many2one('ir.actions.actions', string='Home Action',
        help="If specified, this action will be opened at log on for this user, in addition to the standard menu.", default=lambda self: self.get_crm_action())
    # Force email from login if not set by importing
    @api.model
    def create(self, vals):
        if not vals.get('email',False):
            vals['email'] = vals['login']

        result = super(Users, self).create(vals)
        return result


    def get_crm_action(self):
        crm_act = self.env['ir.actions.actions'].sudo().search([('name','=','Crm: My Pipeline')],limit=1)
        if crm_act:
            return crm_act.id
        return False

    def set_all_user_new_default_page(self):
        usrs = self.sudo().search([('id','!=', 2), ('active','=','True'), ('share','=', False)])
        act_id = self.get_crm_action()
        if act_id:
            for usr in usrs:
                usr.write({'action_id' : act_id})