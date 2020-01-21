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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test.testcases import TestCase

from internship.models import internship_speciality as mdl_internship_speciality
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.speciality import SpecialtyFactory


def create_speciality(name="chirurgie", cohort=None):
    if cohort is None:
        cohort = CohortFactory()
    return SpecialtyFactory(name=name, cohort=cohort)


class TestInternshipSpeciality(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.specialty_1 = create_speciality(name="spe1")
        cls.specialty_2 = create_speciality(name="spe2")

    def test_correct_id(self):
        self.assertEqual(self.specialty_1,
                         mdl_internship_speciality.get_by_id(self.specialty_1.id))
        self.assertEqual(self.specialty_2,
                         mdl_internship_speciality.get_by_id(self.specialty_2.id))

    def test_acronym_exists(self):
        cohort = CohortFactory()
        SpecialtyFactory(cohort=cohort, name="Test1", acronym="TE")
        self.assertTrue(mdl_internship_speciality.acronym_exists(cohort, "TE"))
        self.assertTrue(mdl_internship_speciality.acronym_exists(cohort, "Te"))
        self.assertTrue(mdl_internship_speciality.acronym_exists(cohort, "te"))
