from odoo import models, fields


class on_hand_qty(models.Model):
    _inherit = 'stock.move'

    on_hand_qty = fields.Float(string='On Hand Qty', related='product_id.qty_available', readonly=True)

class on_hand_qty_move_line(models.Model):
    _inherit = 'stock.move.line'

    on_hand_qty = fields.Float(string='On Hand Qty', related='product_id.qty_available', readonly=True)