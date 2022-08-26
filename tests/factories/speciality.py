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
import factory.django

from internship.tests.factories.cohort import CohortFactory


class SpecialtyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipSpeciality'

    name = factory.Sequence(lambda n: f"specialty-{n}")
    mandatory = False
    cohort = factory.SubFactory(CohortFactory)
    sequence = None

    @factory.lazy_attribute
    def acronym(self):
        return "".join(word[0] for word in self.name.split()).upper()
