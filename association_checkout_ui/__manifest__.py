{
    'name': 'Association Checkout UI',
    'version': '19.0.1.0.0',
    'summary': 'Customize website checkout labels and confirmation page for associations',
    'category': 'Website',
    'license': 'AGPL-3',
    'author': 'Michael Champagne',
    'depends': [
        'website',
        'website_sale',
        'payment',
        'sale_management',
        'account',
    ],
    'data': [
        'views/checkout_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
