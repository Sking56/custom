{
    'name': 'Extra Form Columns',
    'summary': 'Add Extra Columns to Forms',
    'description': """Adds extra columns to various different forms
    - Adds a new column to the product moves form that shows what destination column was used.""",
    'author': 'SJC',
    'website': 'http://www.google.com',
    'category': 'Technical',
    'version': '0.1',
    'depends': ['base','stock'],
    'data': [
        'views/stock_move_line_view.xml',
    ],
    'external_dependencies': {
        'python': ['openpyxl', 'pandas', 'xlrd'],
    },
    'images': ['static/description/icon.jpeg'],
    'installable': True,
    'auto_install': False,
}