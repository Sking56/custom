{
    'name': 'Operation On Hand Qty',
    'summary': 'Operation On Hand Qty',
    'description': """Adds a new column to the stock picking form that shows how much quantity on hand a product has.""",
    'author': 'SJC',
    'website': 'http://www.google.com',
    'category': 'Stock',
    'version': '0.1',
    'depends': ['base','stock'],
    'data': [
        'views/stock_view.xml',
    ],
    'external_dependencies': {
        'python': ['openpyxl', 'pandas', 'xlrd'],
    },
    'images': ['static/description/icon.jpeg'],
    'installable': True,
    'auto_install': False,
}