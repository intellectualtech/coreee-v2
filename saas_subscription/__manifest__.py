{
    'name': 'SaaS Subscription & Billing',
    'version': '19.0.1.0.0',
    'category': 'Billing',
    'summary': 'Handle subscriptions, trials, and billing',
    'author': 'SaaS Team',
    'license': 'LGPL-3',
    'depends': ['saas_base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_subscription_views.xml',
        'views/saas_invoice_views.xml',
        'data/cron_jobs.xml',
    ],
    'installable': True,
}
