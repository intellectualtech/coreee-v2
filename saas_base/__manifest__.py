{
    'name': 'SaaS Base',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Multi-tenant SaaS platform core',
    'author': 'SaaS Team',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_tenant_views.xml',
        'views/saas_plan_views.xml',
        'data/saas_plan_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
