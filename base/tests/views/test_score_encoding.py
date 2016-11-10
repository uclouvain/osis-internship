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
from base.tests import data_for_tests
from base.views import score_encoding


class SendMessage(TestCase):
    def setUp(self):
        academic_year = data_for_tests.create_academic_year()

        student_1 = data_for_tests.create_student("Student1", "Etudiant1", "64641200")
        student_2 = data_for_tests.create_student("Student2", "Etudiant2", "60601200")

        offer_year_1 = data_for_tests.create_offer_year("SINF2MA", "Master en Sciences Informatique", academic_year)
        offer_year_2 = data_for_tests.create_offer_year("DROI1BA", "Bachelier en droit", academic_year)

        offer_enrollment_1 = data_for_tests.create_offer_enrollment(student_1, offer_year_1)
        offer_enrollment_2 = data_for_tests.create_offer_enrollment(student_2, offer_year_2)

        learning_unit_year = data_for_tests.create_learning_unit_year("LMEM2110", "Recent Continental Philosophy",
                                                                      academic_year)

        learning_unit_enrollment_1 = data_for_tests.create_learning_unit_enrollment(learning_unit_year,
                                                                                    offer_enrollment_1)
        learning_unit_enrollment_2 = data_for_tests.create_learning_unit_enrollment(learning_unit_year,
                                                                                    offer_enrollment_2)

        offer_year_calendar_1 = data_for_tests.create_offer_year_calendar(offer_year_1, academic_year)
        offer_year_calendar_2 = data_for_tests.create_offer_year_calendar(offer_year_2, academic_year)

        session_exam_1 = data_for_tests.create_session_exam(1, learning_unit_year, offer_year_calendar_1)
        session_exam_2 = data_for_tests.create_session_exam(1, learning_unit_year, offer_year_calendar_2)

        self.exam_enrollment_1 = data_for_tests.create_exam_enrollment(session_exam_1, learning_unit_enrollment_1)
        self.exam_enrollment_2 = data_for_tests.create_exam_enrollment(session_exam_2, learning_unit_enrollment_2)

    def test_do_nothing(self):
        pass



