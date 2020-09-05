# -*- coding: utf-8 -*-

{
    'name': 'ML Accounting Winbooks Export',
    'version': '12.0.0.1.0',
    'depends': [
        'account',
    ],
    'author': "Marc Lebrun",
    'category': 'Accounting',
    'description': """
    This module adds a wizard that allows you to export data to Winbooks.
    """,
    'licence': 'AGPL-3',
    'data': [
        'views/wizard.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'application': False,
    'installable': True,
}