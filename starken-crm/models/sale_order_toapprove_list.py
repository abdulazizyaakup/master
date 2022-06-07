from odoo import fields, models


class SaleOrderUsersToApprove(models.Model):
    _name = 'sale.order.user.toapprove'
    _description = "Approval Required Users"

    name = fields.Char('User Name', store=False)
    user_to_approve = fields.Many2one('res.users', 'User', required=True)

    def name_get(self):
        res = []
        for user in self:
            name = user.user_to_approve.name
            res.append((user.id, name))
        return res
