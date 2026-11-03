{
    'name': 'TD Rental',
    'version': '19.0.1.0.0',
    'summary': 'Equipment rental orders',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/rental_views.xml',
    ],
    'license': 'LGPL-3',
}
