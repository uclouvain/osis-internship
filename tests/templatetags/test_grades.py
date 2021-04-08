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

from django.test import TestCase

from base.tests.factories.student import StudentFactory
from internship.templatetags.grades import is_valid, is_apd_validated
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.score import ScoreFactory


class TestGrades(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_grade = 'D'
        cls.not_valid_grade = 'A'
        cls.na_grade = 'E'
        cls.apd_index = 0
        cls.exception_apd_index = 7
        cls.exception_valid_grade = 'B'

        cls.cohort = CohortFactory()

        cls.good_student = StudentFactory()
        cls.score = ScoreFactory(
            student_affectation__period__cohort=cls.cohort,
            student_affectation__student=cls.good_student,
            APD_1='D'
        )

        cls.bad_student = StudentFactory()
        cls.score = ScoreFactory(
            student_affectation__period__cohort=cls.cohort,
            student_affectation__student=cls.bad_student,
            APD_1='A'
        )

    def test_is_grade_valid_na(self):
        self.assertTrue(is_valid(self.na_grade, self.apd_index))

    def test_is_grade_valid(self):
        self.assertTrue(is_valid(self.valid_grade, self.apd_index))

    def test_is_grade_valid_exception(self):
        self.assertTrue(is_valid(self.exception_valid_grade, self.exception_apd_index))

    def test_is_grade_not_valid(self):
        self.assertFalse(is_valid(self.not_valid_grade, 1))

    def test_is_apd_validated(self):
        self.assertTrue(is_apd_validated(self.cohort, self.good_student, self.apd_index+1))

    def test_is_apd_not_validated(self):
        self.assertFalse(is_apd_validated(self.cohort, self.bad_student, self.apd_index+1))
