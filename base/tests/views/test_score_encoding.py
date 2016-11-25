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

        self.offer_year_1 = data_for_tests.create_offer_year("SINF2MA", "Master en Sciences Informatique", academic_year)
        self.offer_year_2 = data_for_tests.create_offer_year("DROI1BA", "Bachelier en droit", academic_year)

        self.learning_unit_year = data_for_tests.create_learning_unit_year("LMEM2110", "Recent Continental Philosophy",
                                                                           academic_year)

        self.exam_enrollment_1 = self.create_exam_enrollment(1, "64641200", self.offer_year_1, self.learning_unit_year,
                                                             academic_year)
        self.exam_enrollment_2 = self.create_exam_enrollment(2, "60601200", self.offer_year_2, self.learning_unit_year,
                                                             academic_year)

        self.tutor = self.create_tutor_with_user(1)
        data_for_tests.create_attribution(tutor=self.tutor, learning_unit_year=self.learning_unit_year)
        self.add_permission(self.tutor.person.user, "can_access_scoreencoding")

        self.program_manager_1 = self.create_program_manager_with_user(1, self.offer_year_1)
        self.add_permission(self.program_manager_1.person.user, "can_access_scoreencoding")

        self.program_manager_2 = self.create_program_manager_with_user(2, self.offer_year_2)
        self.add_permission(self.program_manager_2.person.user, "can_access_scoreencoding")

        self.Client = Client()

    @staticmethod
    def add_permission(user, codename):
        perm = OnlineEncodingTest.get_permission(codename)
        user.user_permissions.add(perm)


    @staticmethod
    def create_program_manager_with_user(num_id, offer_year):
        program_manager = data_for_tests.create_program_manager(offer_year)

        perm = OnlineEncodingTest.get_permission("can_access_scoreencoding")
        program_manager.person.user = data_for_tests.create_user("pgm" + str(num_id))
        program_manager.person.user.user_permissions.add(perm)
        program_manager.person.save()
        return program_manager

    @staticmethod
    def create_tutor_with_user(num_id):
        tutor = data_for_tests.create_tutor(first_name="tutor"+str(num_id), last_name="tutor" + str(num_id))
        tutor.person.user = data_for_tests.create_user("tutor"+str(num_id))
        tutor.person.save()
        return tutor

    @staticmethod
    def create_exam_enrollment(num_id, registration_id, offer_year, learning_unit_year, academic_year):
        student = data_for_tests.create_student("Student" + str(num_id), "Etudiant" + str(num_id), registration_id)
        offer_enrollment = data_for_tests.create_offer_enrollment(student, offer_year)
        learning_unit_enrollment = data_for_tests.create_learning_unit_enrollment(learning_unit_year,
                                                                                    offer_enrollment)
        offer_year_calendar = data_for_tests.create_offer_year_calendar(offer_year, academic_year)
        session_exam = data_for_tests.create_session_exam(1, learning_unit_year, offer_year_calendar)
        return data_for_tests.create_exam_enrollment(session_exam, learning_unit_enrollment)

    @staticmethod
    def get_permission(codename):
        return Permission.objects.get(codename=codename)

    def test_filter_enrollments_by_offer_year(self):
        enrollments = [self.exam_enrollment_1, self.exam_enrollment_2]

        expected = [self.exam_enrollment_1]
        actual = score_encoding.filter_enrollments_by_offer_year(enrollments, self.offer_year_1)

        self.assertListEqual(expected, actual, "Should only return enrollments for the first offer year")

    def test_online_encoding_with_one_student_filled_by_tutor(self):
        self.client.force_login(self.tutor.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data={"score_"+str(self.exam_enrollment_1.id): "15",
                                               "justification_"+str(self.exam_enrollment_1.id): "",
                                               "score_changed_"+str(self.exam_enrollment_1.id): "true",
                                               "score_" + str(self.exam_enrollment_2.id): "",
                                               "justification_" + str(self.exam_enrollment_2.id): "",
                                               "score_changed_" + str(self.exam_enrollment_2.id): "false"
                                               })

        self.exam_enrollment_1.refresh_from_db()
        self.exam_enrollment_2.refresh_from_db()
        self.assertEqual(self.exam_enrollment_1.score_draft, 15)
        self.assertEqual(self.exam_enrollment_2.score_draft, None)

    def test_online_encoding_with_one_student_filled_by_pgm(self):
        pass

    def test_online_encoding_with_all_student_filled_by_tutor(self):
        self.client.force_login(self.tutor.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data={"score_"+str(self.exam_enrollment_1.id): "15",
                                               "justification_"+str(self.exam_enrollment_1.id): "",
                                               "score_changed_"+str(self.exam_enrollment_1.id): "true",
                                               "score_" + str(self.exam_enrollment_2.id): "18",
                                               "justification_" + str(self.exam_enrollment_2.id): "",
                                               "score_changed_" + str(self.exam_enrollment_2.id): "true"
                                               })

        self.exam_enrollment_1.refresh_from_db()
        self.exam_enrollment_2.refresh_from_db()
        self.assertEqual(self.exam_enrollment_1.score_draft, 15)
        self.assertEqual(self.exam_enrollment_2.score_draft, 18)







