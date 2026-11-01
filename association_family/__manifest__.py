{
    'name': 'Association Family',
    'version': '19.0.1.0.0',
    'summary': 'Manage household members and member-level attribution for association operations',
    'category': 'Website',
    'license': 'AGPL-3',
    'author': 'Michael Champagne',
    'depends': [
        'base',
        'contacts',
        'portal',
        'website',
        'website_sale',
        'sale_management',
        'account',
        'event',
        'event_sale',
    ],
    'data': [
        'security/association_family_security.xml',
        'views/res_partner_views.xml',
        'views/sale_order_line_views.xml',
        'views/portal_templates.xml',
        'views/website_event_checkout_templates.xml',
        'views/website_event_confirmation_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'association_family/static/src/js/event_participants_checkout.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
