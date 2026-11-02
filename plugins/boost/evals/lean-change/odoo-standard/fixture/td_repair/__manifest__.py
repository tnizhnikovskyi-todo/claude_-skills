{
    'name': 'TD Repair',
    'version': '19.0.1.0.0',
    'summary': 'Простые заказы на ремонт',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_order_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
}
