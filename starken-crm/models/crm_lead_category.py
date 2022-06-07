from odoo import api, fields, models, tools, _

class CrmCategory(models.Model):
    _name = 'starken_crm.lead.category'
    _inherit = ['mail.thread.cc','mail.thread.cc','mail.thread', 'mail.activity.mixin']
    _description = 'CRM Lead Category'

    name = fields.Char("Name")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    parent_id = fields.Many2one('starken_crm.lead.category',string="Parent Category")
    category_notes = fields.Text("Category Notes")

    def name_get(self):
        result = []
        for val in self:
            if val.parent_id:
                result.append((val.id, _("%s >> %s ")%(val.parent_id.name, val.name)))
            if not val.parent_id:
                result.append((val.id, _("%s")%(val.name)))
        return result

