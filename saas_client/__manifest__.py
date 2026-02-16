{
    'name': 'SaaS Client',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Client-facing features (custom domain, backup, etc)',
    'author': 'SaaS Team',
    'license': 'LGPL-3',
    'depends': ['saas_base', 'saas_subscription'],
    'data': [
        'views/client_panel_views.xml',
        'views/client_menu.xml',
    ],
    'installable': True,
}
