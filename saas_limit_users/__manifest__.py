{
    'name': 'SaaS User Limits',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Enforce user limits per plan',
    'author': 'SaaS Team',
    'license': 'LGPL-3',
    'depends': ['saas_base', 'saas_subscription'],
    'data': [
        'data/cron_check_limits.xml',
    ],
    'installable': True,
}
