#!/usr/bin/env python3
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
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from functools import reduce
import os

# Add your fixtures at the end of the list so that model dependencies are respected.
DATA_FIXTURES = [
    'user.json',
    'person.json',
    'tutor.json',
    'student.json',
    'academic_year.json',
    'academic_calendar.json',
    'learning_unit.json',
    'learning_unit_year.json',
    'messages_templates.json',
    'offer.json',
    'organization.json',
    'structure.json',
    'attribution.json',
    'continent.json',
    'currency.json',
    'country.json',
    'decree.json',
    'domain.json',
    'education_institution.json',
    'language.json',
    'continent.json',
    'person_address.json',
    'organization_address.json',
    'offer_year.json',
    'offer_year_calendar.json',
    'session_exam.json',
    'program_manager.json',
    'offer_enrollment.json',
    'learning_unit_enrollment.json',
    'exam_enrollment.json'
    ]

ARGS = reduce(lambda s1,s2 : s1 + ' ' + s2,DATA_FIXTURES)
COMMAND = 'python manage.py loaddata '+ARGS
print(COMMAND)
os.system(COMMAND)
