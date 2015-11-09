# -*- coding: utf-8 -*-
{
    'name': "osis-louvain",

    'summary': """
        Extension of the module OSIS to accommodate specific needs of the Université catholique de Louvain.
    """,

    'description': """
        OSIS Louvain is an extension of OSIS customized for the needs of the Université catholique de Louvain.
    """,

    'author': "Université catholique de Louvain",
    'website': "http://www.uclouvain.be",

    'category': 'Education',
    'version': '15.11.1.0',

    'depends': ['base','osis-core'],

    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/menu.xml',
        "views/institution.xml",
        "views/student.xml",
        # "views/partner.xml",
    ],

    'demo': [
        'demo.xml',
    ],
}
