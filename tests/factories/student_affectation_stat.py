##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import random
import factory.django

from base.tests.factories.student import StudentFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.tests.factories.period import PeriodFactory


class StudentAffectationStatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipStudentAffectationStat'

    cost = random.choice(list({1: 0, 2: 1, 3: 2, 4: 3, 'E': 0, 'I': 10, 'X': 1000}.values()))
    student = factory.SubFactory(StudentFactory)
    organization = factory.SubFactory(OrganizationFactory)
    speciality = factory.SubFactory(SpecialtyFactory)
    period = factory.SubFactory(PeriodFactory)