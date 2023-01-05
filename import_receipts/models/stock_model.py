from odoo import models

class StockPicking(models.Model):
    _inherit="stock.picking"

    def import_receipt_lines(self):
        if self:
            action = self.env.ref('import_receipts.action_import_receipt_line_wizard').read()[0]
            return action