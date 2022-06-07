from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    lorry_no = fields.Char('Lorry No.')
    customer_ship_id = fields.Many2one('res.partner', 'Shipping Address')
    origin_so = fields.Many2one('sale.order', 'Sales Order')
    origin_so_po = fields.Char('PO Number', related="origin_so.po_number")
    seq_num = fields.Char('No', store=False, compute="_get_seq_num")
    shipping_date = fields.Date('Shipping Date')

    def _get_seq_num(self):
        for rec in self:
            if rec.name:
                if rec.name != '/':
                    rec.seq_num = rec.name.split('/')[2]
                else:
                    rec.seq_num = '/'

    @api.onchange('origin_so')
    def get_products_from_so(self):
        for rec in self:
            if not rec.backorder_id and rec.origin_so:
                rtn_list = []
                for line in rec.origin_so.order_line:
                    rtn_list.append((0, 0, {
                        'name': (line.product_id.name
                                 + line.product_id.description_sale),
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom,
                    }))
                rec.move_ids_without_package = [(6, 0, [])]
                if rtn_list:
                    rec.move_ids_without_package = rtn_list

    def name_get(self):
        res = []
        for spick in self:
            if spick.seq_num != '/':
                name = spick.seq_num
            else:
                name = spick.name
            res.append((spick.id, name))
        return res

    def action_generate_backorder_wizard(self):
        wiz = self.env['stock.backorder.confirmation'].\
            create({'pick_ids': [(4, p.id) for p in self]})
        wiz.process()
        return True
