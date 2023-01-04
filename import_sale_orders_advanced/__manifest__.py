{
    'name': 'Import Sale Orders Advanced',
    'summary': 'Import Sale Orders Advanced from an xls file',
    'description': """Allows you to import sale orders from an xls file. The file must contain information found within the sale order form. The file must contain the following columns:""",
    'author': 'SJC',
    'website': 'http://www.google.com',
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base','sale_management'],
    'data': [
        'security/import_sale_orders_security.xml',
        'security/ir.model.access.csv',
        'wizard/import_sale_order_wizard.xml',
        'views/sale_view.xml',
    ],
    'external_dependencies': {
        'python': ['openpyxl', 'pandas', 'xlrd'],
    },
    'images': ['static/description/icon.jpeg'],
    'installable': True,
    'auto_install': False,
}