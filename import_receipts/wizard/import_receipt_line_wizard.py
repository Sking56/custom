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
        
        current_receipt = self.env['stock.picking'].browse(self.env.context.get('receipt_id'))

        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        sheet = wb.sheet_by_index(0)
        df = self.sheet_to_df(sheet)
        
        company_id = self.env.context.get('company_id')

        #Create receipt lines
        for index, row in df.iterrows():
            line_counter += 1

            move_model = self.env['stock.move']
            move_line_model = self.env['stock.move.line']

            location_id = current_receipt.location_id
            location_dest_id = current_receipt.location_dest_id
            picking_type_id = current_receipt.picking_type_id
            date = self.date

            product_id = self.env['product.product'].search([('default_code', '=', row['Product_Reference'])], limit=1)
            if(not product_id):
                raise UserError("Product " + row['Product_ID'] + " not found on line " + str(line_counter))
            product_id = product_id[0]

            product_uom= self.env['uom.uom'].search([('name', '=', row['Uom'])], limit=1)[0]        
            if(self.create_lots):
                lot_id = self.env['stock.production.lot'].search([('name', '=', row['Lot_Number']),('product_id','=',product_id.id)], limit=1)
                if(not lot_id):
                    lot_id = self.env['stock.production.lot'].sudo().create([{'name':row['Lot_Number'], 'product_id':product_id[0].id,'company_id':company_id}])

            if(self.create_packages):
                source_package_id = self.env['stock.quant.package'].search([('name', '=', df['Origin'].iloc[0])], limit=1)
                package_id = self.env['stock.quant.package'].search([('name', '=', row['Package_Name'])], limit=1)
                if(not package_id):
                    package_id = self.env['stock.quant.package'].create([{'name':row['Package_Name'], 'company_id':company_id}])
                elif(not isinstance(package_id, int)):
                    package_id = package_id[0]
                if(not source_package_id):
                    source_package_id = self.env['stock.quant.package'].create([{'name':df['Origin'].iloc[0], 'company_id':company_id}])
                elif(not isinstance(source_package_id, int)):
                    source_package_id = source_package_id[0]

            move_vals = {
                'name': row['Product_Reference'],
                'product_id': product_id.id,
                'product_uom_qty': row['Quantity'],
                'product_uom': product_uom[0].id,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'picking_id': current_receipt.id,
                'picking_type_id': picking_type_id.id,
                'company_id': company_id,
                'date':date,
                'create_date':date,
                'write_date':date,
            }

            move_id = move_model.create(move_vals)

            move_line_vals = {
                'picking_id': current_receipt.id,
                'move_id': move_id.id,
                'company_id': company_id,
                'product_id': product_id.id,
                'product_uom_id': product_uom.id,
                'qty_done': row['Quantity'],
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'lot_id': lot_id.id,
                # 'lot_name': row['Lot_Number'],
                'package_id': source_package_id.id,
                'result_package_id': package_id.id,
                'date': date,
                'create_date': date,
                'write_date': date,
            }

            move_line_model.create(move_line_vals)