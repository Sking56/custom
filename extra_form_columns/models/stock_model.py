from odoo import models, fields

class product_moves_destination(models.Model):
    _inherit = 'stock.move.line'

    move_destination_package = fields.Char(string='Destination Package', related='result_package_id.name', readonly=True)