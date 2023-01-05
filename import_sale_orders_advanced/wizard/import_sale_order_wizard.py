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
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    template = fields.Many2one('sale.order.template', string='Template', required=True)
    date = fields.Datetime(string='Order Date', required=True, default=datetime.now())
    file = fields.Binary(string='Input File', required=True)
    create_packages = fields.Boolean(string='Create Packages', default=True)

    #Print error message
    def print_error_message(self, message):
        raise UserError(_(message))

    #Retrieve data from template line
    def get_template_line_data(self, template_line):
        product = template_line.product_id
        product_uom = template_line.product_uom_id.id
        product_uom_qty = template_line.product_uom_qty
        price_unit = template_line.product_id.lst_price
        name = template_line.name
        customer_lead = 0
        return {'product_id':product, 'product_uom':product_uom, 'product_uom_qty':product_uom_qty, 'price_unit':price_unit, 'name':name, 'customer_lead':customer_lead, 'discount':0,'order_id':self.id, 'invoice_lines':[]}

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
        partner_id = self.customer.id
        date = self.date
        create_packages = self.create_packages
        template = self.template
        order_lines = [(5,0,0)]

        for line in template.sale_order_template_line_ids:
            template_line_data = self.get_template_line_data(line)
            order_lines.append((0, 0, template_line_data))

        #Create sale order
        sale_order_model = self.env['sale.order']
        sale_order_vals = {
            'partner_id': partner_id,
            'date_order': date,
            'order_line': template.sale_order_template_line_ids,
            'sale_order_template_id': template.id,
        }

        sale_order_model.create(sale_order_vals)

        template.generate_sale_order()

        #Create sale order lines
        # for index, row in df.iterrows():
        #     line_counter += 1

        #     #Get product
        #     product_id = self.env['product.product'].search([('default_code', '=', row['Product_ID'])], limit=1)
        #     if(not product_id):
        #         error += "Product " + row['Product_ID'] + " not found on line " + str(line_counter)