{
    'name': 'TD Depot',
    'version': '19.0.1.0.0',
    'depends': ['td_base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/depot_views.xml',
        'data/cron.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'license': 'LGPL-3',
}
