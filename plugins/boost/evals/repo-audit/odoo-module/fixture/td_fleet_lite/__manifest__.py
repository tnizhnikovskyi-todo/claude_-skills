{
    'name': 'TD Fleet Lite',
    'version': '19.0.1.2.0',
    'summary': 'Учёт машин и сервисных визитов для небольшого автопарка',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/vehicle_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
}
