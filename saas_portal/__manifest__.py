{
    'name': 'SaaS Portal',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Public signup and tenant management portal',
    'author': 'SaaS Team',
    'license': 'LGPL-3',
    'depends': ['saas_base', 'saas_subscription', 'web', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
        'views/signup_form.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'saas_portal/static/src/css/portal.css',
            'saas_portal/static/src/js/portal.js',
        ],
    },
    'installable': True,
}
