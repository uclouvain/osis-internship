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
from django.db.utils import IntegrityError
from django.test import TestCase

from base.tests.models import test_student
from internship.models import internship_choice as mdl_internship_choice
from internship.models.internship_choice import InternshipChoice
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.models import test_internship_student_information
from internship.tests.models import test_organization, test_internship_speciality


class TestSearchByStudentOrChoice(TestCase):
    def setUp(self):
        self.organization = test_organization.create_organization()
        self.student = test_student.create_student(first_name="first", last_name="last", registration_id="64641200")
        self.other_student = test_student.create_student(first_name="first", last_name="last", registration_id="606012")
        self.cohort = CohortFactory()
        self.speciality = test_internship_speciality.create_speciality(cohort=self.cohort)
        self.internship = InternshipFactory(cohort=self.cohort)
        self.other_internship = InternshipFactory(cohort=self.cohort)
        self.student_information = test_internship_student_information.create_student_information(
            person=self.student.person,
            cohort=self.cohort)
        self.other_student_information = test_internship_student_information.create_student_information(
            person=self.other_student.person,
            cohort=self.cohort)

        self.choice_1 = create_internship_choice(
            self.organization, self.student, self.speciality,
            internship=self.other_internship
        )
        self.choice_2 = create_internship_choice(
            self.organization, self.student, self.speciality,
            internship=self.internship
        )
        self.choice_3 = create_internship_choice(
            self.organization, self.other_student, self.speciality,
            internship=self.other_internship
        )

    def test_duplicates_are_forbidden(self):
        with self.assertRaises(IntegrityError):
            create_internship_choice(self.organization, self.student, self.speciality, internship=self.internship)

    def test_with_only_student(self):
        choices = list(mdl_internship_choice.search_by_student_or_choice(student=self.student))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_2, choices)

    def test_with_only_internship_choice(self):
        choices = list(mdl_internship_choice.search_by_student_or_choice(internship=self.other_internship))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_3, choices)

    def test_with_student_and_internship_choice(self):
        choices = list(mdl_internship_choice.search_by_student_or_choice(student=self.student,
                                                                         internship=self.internship))
        self.assertListEqual([self.choice_2], choices)

    def test_get_number_students(self):
        expected = 2
        actual = InternshipChoice.objects.filter(internship__cohort=self.cohort).distinct("student").count()
        self.assertEqual(expected, actual)
