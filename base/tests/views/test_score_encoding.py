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
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from base.tests import data_for_tests
from base.views import score_encoding
from base import models as mdl
from unittest.mock import patch
from django.contrib.auth.models import Permission



class OnlineEncodingTest(TestCase):
    def setUp(self):
        academic_year = data_for_tests.create_academic_year()

        student_1 = data_for_tests.create_student("Student1", "Etudiant1", "64641200")
        student_2 = data_for_tests.create_student("Student2", "Etudiant2", "60601200")

        self.offer_year_1 = data_for_tests.create_offer_year("SINF2MA", "Master en Sciences Informatique", academic_year)
        self.offer_year_2 = data_for_tests.create_offer_year("DROI1BA", "Bachelier en droit", academic_year)

        offer_enrollment_1 = data_for_tests.create_offer_enrollment(student_1, self.offer_year_1)
        offer_enrollment_2 = data_for_tests.create_offer_enrollment(student_2, self.offer_year_2)

        self.learning_unit_year = data_for_tests.create_learning_unit_year("LMEM2110", "Recent Continental Philosophy",
                                                                      academic_year)

        learning_unit_enrollment_1 = data_for_tests.create_learning_unit_enrollment(self.learning_unit_year,
                                                                                    offer_enrollment_1)
        learning_unit_enrollment_2 = data_for_tests.create_learning_unit_enrollment(self.learning_unit_year,
                                                                                    offer_enrollment_2)

        offer_year_calendar_1 = data_for_tests.create_offer_year_calendar(self.offer_year_1, academic_year)
        offer_year_calendar_2 = data_for_tests.create_offer_year_calendar(self.offer_year_2, academic_year)

        session_exam_1 = data_for_tests.create_session_exam(1, self.learning_unit_year, offer_year_calendar_1)
        session_exam_2 = data_for_tests.create_session_exam(1, self.learning_unit_year, offer_year_calendar_2)

        self.exam_enrollment_1 = data_for_tests.create_exam_enrollment(session_exam_1, learning_unit_enrollment_1)
        self.exam_enrollment_2 = data_for_tests.create_exam_enrollment(session_exam_2, learning_unit_enrollment_2)

        self.tutor = data_for_tests.create_tutor()
        data_for_tests.create_attribution(tutor=self.tutor, learning_unit_year=self.learning_unit_year)
        self.tutor.person.user = data_for_tests.create_user()
        self.tutor.person.save()
        self.tutor.save()

        perm = Permission.objects.get(codename="can_access_scoreencoding")
        self.tutor.person.user.user_permissions.add(perm)

        self.Client = Client()
        self.client.force_login(self.tutor.person.user)

    def test_filter_enrollments_by_offer_year(self):
        enrollments = [self.exam_enrollment_1, self.exam_enrollment_2]

        expected = [self.exam_enrollment_1]
        actual = score_encoding.filter_enrollments_by_offer_year(enrollments, self.offer_year_1)

        self.assertListEqual(expected, actual, "Should only return enrollments for the first offer year")

    def test_online_encoding_with_one_student_filled(self):
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data={"score_"+str(self.exam_enrollment_1.id): "15",
                                               "justification_"+str(self.exam_enrollment_1.id): "",
                                               "score_changed_"+str(self.exam_enrollment_1.id): "true",
                                               "score_" + str(self.exam_enrollment_2.id): "",
                                               "justification_" + str(self.exam_enrollment_2.id): "",
                                               "score_changed_" + str(self.exam_enrollment_2.id): "false"
                                               })

        self.exam_enrollment_1.refresh_from_db()
        self.assertEqual(self.exam_enrollment_1.score_draft, 15)
        # self.assertEqual(mock_send_message.called, True)
        # (actual_persons, actual_enrollments,
        #  actual_learning_unit_acronym, actual_offer_acronym) = mock_send_message.call_args
        # self.assertEqual(actual_persons, [self.tutor.person])
        # self.assertEqual(actual_enrollments, [self.exam_enrollment_1])
        # self.assertEqual(actual_learning_unit_acronym, self.learning_unit_year.acronym)
        # self.assertEqual(actual_offer_acronym, self.offer_year_1.acronym)








