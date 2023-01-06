from odoo import fields, models
from odoo.exceptions import UserError
import pandas as pd
import base64
import xlrd
from datetime import datetime

#Wizard to import receipts from excel file into inventory
class import_receipts_wizard(models.TransientModel):
    _name = "import.receipts.wizard"
    _description = "Import Receipts to Inventory"

    #Set default date to today
    date = fields.Datetime(string='Scheduled Date', required=True, default=datetime.now())
    file = fields.Binary(string='File', required=True)

    #Convert excel sheet to dataframe
    def sheet_to_df(self, sheet):
        data = []
        for row in range(sheet.nrows):
            data.append(sheet.row_values(row))
        df = pd.DataFrame(data[1:], columns=data[0])
        return df

    #Import receipts from excel file button
    def import_receipts(self):
        line_counter = 1
        error = ""
        
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        sheet = wb.sheet_by_index(0)
        df = self.sheet_to_df(sheet)

        #Create receipt information
        partner_id = self.env['res.partner'].search([('name', '=', df['Vendor_ID'].iloc[0])], limit=1)
        location_id = self.env['stock.location'].search([('complete_name', '=', df['Location_ID'].iloc[0])], limit=1)
        parent_location = self.env['stock.location'].search([('complete_name', '=', df['Parent_Location'].iloc[0])], limit=1)[0].id
        location_dest_id = self.env['stock.location'].search([('name', '=', df['Destination_Location_ID'].iloc[0])], limit=1)
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', df['Code'].iloc[0])], limit=1)
        date = self.date

        if(not location_dest_id):
            location_dest_id = self.env['stock.location'].sudo().create([{'name':df['Destination_Location_ID'].iloc[0]}])
            location_dest_id.write({'location_id':parent_location})

        if not picking_type_id:
            raise UserError("Picking type not found: " + df['Code'].iloc[0])
        elif not partner_id:
            raise UserError("Partner not found: " + df['Vendor_ID'].iloc[0])
        elif not location_id:
            raise UserError("Location not found: " + df['Location_ID'].iloc[0])
        elif not parent_location:
            raise UserError("Parent location not found: " + df['Parent_Location'].iloc[0])

        if(isinstance(location_dest_id, list)):
            location_dest_id = location_dest_id[0]

        receipt_model = self.env['stock.picking']
        receipt_vals = {
            'name': df['Receipt_Number'].iloc[0],
            'partner_id': partner_id[0].id,
            'location_id': location_id[0].id,
            'location_dest_id': location_dest_id.id,
            'date': date,
            "scheduled_date": date,
            'date_done': date,
            'origin': df['Origin'].iloc[0],
            'move_lines': [],
            'picking_type_id': picking_type_id[0].id,
            'immediate_transfer': True,
        }

        receipt_id = receipt_model.create([receipt_vals])

        company_id = self.env['res.company'].search([('name', '=', df['Company_ID'].iloc[0])], limit=1)

        #Create receipt lines from dataframe products
        for index, row in df.iterrows():
            stock_quant_model = self.env['stock.quant']

            #Create line information with product, lot, and package
            product_id = self.env['product.product'].search([('default_code', '=', row['Product_Reference'])], limit=1)
            if(not product_id):
                raise UserError("Product not found: " + row['Product_Reference'])

            product_id = product_id[0]
            product_uom= self.env['uom.uom'].search([('name', '=', row['Uom'])], limit=1)[0]
            if not product_uom:
                raise UserError("Uom not found: " + row['Uom'])

            
            package_id = self.env['stock.quant.package'].search([('name', '=', row['Package_Name'])], limit=1)
            source_package_id = self.env['stock.quant.package'].search([('name', '=', df['Origin'].iloc[0])], limit=1)
            if(not package_id):
                package_id = self.env['stock.quant.package'].create([{'name':row['Package_Name'],'company_id':company_id[0].id}])
            elif(not isinstance(package_id, int)):
                package_id = package_id[0]

            if(not source_package_id):
                source_package_id = self.env['stock.quant.package'].create([{'name':df['Origin'].iloc[0],'company_id':company_id[0].id}])
            elif(not isinstance(source_package_id, int)):
                source_package_id = source_package_id[0]

            lot_id = self.env['stock.production.lot'].search([('name', '=', row['Lot_Number']),('product_id','=',product_id.id)], limit=1)
            if(not lot_id):
                lot_id = self.env['stock.production.lot'].create([{'name':row['Lot_Number'],'product_id':product_id.id,'company_id':company_id[0].id}])

            if(not isinstance(lot_id, int)):
                lot_id = lot_id[0]

            move_model = self.env['stock.move']
            move_vals = {
                'name': row['Product_Reference'],
                'product_id': product_id.id,
                'product_uom_qty': row['Quantity'],
                'product_uom': product_uom[0].id,
                'location_id': location_id[0].id,
                'location_dest_id': location_dest_id.id,
                'picking_id': receipt_id.id,
                'picking_type_id': picking_type_id[0].id,
                'company_id': company_id[0].id,
                'date':date,
                'create_date':date,
                'write_date':date,
            }

            move_id = move_model.create([move_vals])

            move_line_model = self.env['stock.move.line']

            move_line_vals = {
                'picking_id': receipt_id.id,
                'move_id': move_id.id,
                'company_id': company_id[0].id,
                'product_id': product_id.id,
                'product_uom_id': product_uom[0].id,
                'qty_done': row['Quantity'],
                'location_id': location_id[0].id,
                'location_dest_id': location_dest_id.id,
                'lot_id': lot_id.id,
                # 'lot_name': row['Lot_Number'],
                'package_id': source_package_id.id,
                'result_package_id': package_id.id,
                'date': date,
                'create_date': date,
                'write_date': date,
            }

            move_line_id = move_line_model.create([move_line_vals])

            receipt_id.write({'date': date, "scheduled_date": date,'date_done':date})