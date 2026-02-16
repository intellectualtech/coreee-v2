{
    'name': 'SaaS Admin',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Master control panel for all tenants',
    'author': 'SaaS Team',
    'license': 'LGPL-3',
    'depends': ['saas_base', 'saas_subscription'],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_admin_views.xml',
        'views/saas_admin_menu.xml',
        'wizard/tenant_wizard_views.xml',
    ],
    'installable': True,
}
