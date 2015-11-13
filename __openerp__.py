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
        'views/person.xml',
        'views/student.xml',
        'views/tutor.xml',
        'views/offer.xml',
        'views/attribution.xml',
        'views/academic_year.xml',
        'views/learning_unit.xml',
        # 'reports/student.xml',
    ],

    'demo': [
        'demo.xml',
    ],
}
