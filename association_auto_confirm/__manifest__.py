# pyright: reportUnusedExpression=false
{
    'name': 'Association Auto Confirm',
    'version': '19.0.1.0.0',
    'summary': 'Auto confirm web orders paid by bank transfer and issue the invoice',
    'category': 'Sales',
    'license': 'AGPL-3',
    'author': 'Michael Champagne',
    'depends': [
        'sale_management',
        'website_sale',
        'payment',
        'account',
    ],
    'data': [
        'views/payment_confirmation.xml',
    ],
    'installable': True,
    'auto_install': False,
}
