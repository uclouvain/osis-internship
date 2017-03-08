##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from internship.tests.models import test_organization, test_internship_speciality, test_internship_choice, \
    test_internship_student_information
from base.tests.models import test_student
from internship.views import student_resume


class TestStudentResume(TestCase):
    def setUp(self):
        organization = test_organization.create_organization()
        self.student_1 = test_student.create_student(first_name="first", last_name="last", registration_id="64641200")
        self.student_2 = test_student.create_student(first_name="first", last_name="last", registration_id="606012")
        speciality = test_internship_speciality.create_speciality()

        self.choice_1 = test_internship_choice.create_internship_choice(organization, self.student_1, speciality,
                                                                        internship_choice=1)
        self.choice_2 = test_internship_choice.create_internship_choice(organization, self.student_1, speciality,
                                                                        internship_choice=2)
        self.choice_3 = test_internship_choice.create_internship_choice(organization, self.student_1, speciality,
                                                                        internship_choice=3)
        self.choice_4 = test_internship_choice.create_internship_choice(organization, self.student_1, speciality,
                                                                        internship_choice=4)

        self.choice_5 = test_internship_choice.create_internship_choice(organization, self.student_2, speciality,
                                                                        internship_choice=1)
        self.choice_6 = test_internship_choice.create_internship_choice(organization, self.student_2, speciality,
                                                                        internship_choice=2)
        self.choice_7 = test_internship_choice.create_internship_choice(organization, self.student_2, speciality,
                                                                        internship_choice=3)

    def test_get_students_status(self):
        expected = []
        actual = student_resume.get_students_with_status()
        self.assertCountEqual(expected, actual)

        test_internship_student_information.create_student_information(self.student_1.person, "GENERALIST")
        test_internship_student_information.create_student_information(self.student_2.person, "GENERALIST")
        expected = [(self.student_1, True), (self.student_2, False)]
        actual = student_resume.get_students_with_status()
        self.assertCountEqual(expected, actual)
        for item_expected in expected:
            self.assertIn(item_expected, actual)









