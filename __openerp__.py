# -*- coding: utf-8 -*-
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    A copy of this license - GNU Affero General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
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
        'demo.xml',
        'templates.xml',
        'views/menu.xml',
        "views/institution.xml",
        'views/person.xml',
        'views/student.xml',
        'views/tutor.xml',
        'views/offer.xml',
        'views/attribution.xml',
        'views/academic_year.xml',
        'views/learning_unit.xml',
        'views/exam.xml',
        # 'views/structure.xml',
        'views/offer_year.xml',
        'views/offer_enrollment.xml',
        'views/learning_unit_year.xml',
        'views/learning_unit_enrollment.xml',
        'views/exam_enrollment.xml',
        'reports/student.xml',
        'views/learning_unit_status.xml',
        'reports/learning_unit_enrollment.xml',
    ],

    'demo': [
        'demo.xml',
    ],
}
