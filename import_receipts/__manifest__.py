# -*- coding: utf-8 -*-
{
    'name': "Import Inventory Receipts",
    'summary': """
        Creates a new receipt from an xlsx file""",
    'description': """
        Imports a new receipt from an xlsx file that contains
        the following columns:
        Code,Receipt_Number,Location_ID, Destination_Location_ID, Vendor_ID, Receipt_Date, Origin, Quantity, Company_ID, Lot_Number, Product_Reference, Product_ID, Uom, Package_Name
    """,
    'author': "SJC",
    'website': "http://www.google.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','stock'],
    'application': True,
    # always loaded
    'data': [
        'security/import_receipts_security.xml',
        'security/ir.model.access.csv',
        'wizard/import_receipts_wizard.xml',    
        'views/stock_view.xml', 
    ],
    'external_dependencies': {
        'python': ['openpyxl', 'pandas', 'xlrd'],
    },
    'images': ['static/description/egg.jpeg'],
    'installable': True,
    'auto_install': False,
}
