from odoo import models, fields
from odoo.exceptions import UserError
import pandas as pd
import base64
import xlrd
from datetime import datetime

#Wizard to import receipt lines directly into current receipt
class import_receipt_line_wizard(models.TransientModel):
    _name="import.receipt.line.wizard"
    _description="Import Receipt Lines to Open Receipt"

    #Set default date to today
    date = fields.Datetime(string='Scheduled Date', required=True, default=datetime.now())
    file = fields.Binary(string='File', required=True)
    create_packages = fields.Boolean(string='Create Packages', default=True)
    create_lots = fields.Boolean(string='Create Lots', default=True)

    #Convert excel sheet to dataframe
    def sheet_to_df(self, sheet):
        data = []
        for row in range(sheet.nrows):
            data.append(sheet.row_values(row))
        df = pd.DataFrame(data[1:], columns=data[0])
        return df

    #Import receipt lines from excel file button
    def import_receipt_lines(self):
        line_counter = 1
        error = ""
        
        current_receipt = self.env['stock.picking'].browse(self._context.get('active_id'))

        #Create receipt lines
        for index, row in df.iterrows():
            product_id = self.env['product.product'].search([('default_code', '=', row['Product_ID'])], limit=1)