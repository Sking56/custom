from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pandas as pd
import base64
import xlrd
from datetime import datetime

#Wizard to import sales orders from excel file into sales
class import_sale_order_wizard(models.TransientModel):
    _name = "import.sale.order.wizard"
    _description = "Import Sales Orders With Advanced Options"

    #Create fields
    date = fields.Datetime(string='Order Date', required=True, default=datetime.now())
    file = fields.Binary(string='Input File', required=True)
    create_packages = fields.Boolean(string='Create Packages', default=True)

    #Print error message
    def print_error_message(self, message):
        raise UserError(_(message))

    #Convert excel sheet to dataframe
    def sheet_to_df(self, sheet):
        data = []
        for row in range(sheet.nrows):
            data.append(sheet.row_values(row))
        df = pd.DataFrame(data[1:], columns=data[0])
        return df

    #Import sales orders from excel file button
    def import_sale_order(self):
        line_counter = 1
        error = ""

        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        sheet = wb.sheet_by_index(0)
        df = self.sheet_to_df(sheet)

        #Create sale order information
        partner_id = self.env['res.partner'].search([('name', '=', df['Customer_ID'].iloc[0])], limit=1)