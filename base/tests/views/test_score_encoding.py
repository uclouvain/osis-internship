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
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory

from base.tests.models import test_person, test_exam_enrollment, test_academic_year, test_offer_year_calendar, \
                              test_offer_year, test_learning_unit_year, test_program_manager, test_tutor, test_student,\
                              test_offer_enrollment, test_learning_unit_enrollment
from attribution.tests.models import test_attribution
from base.tests.models.test_session_exam import create_session_exam
from base.views import score_encoding
from base.models.exam_enrollment import ExamEnrollment

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory

class OnlineEncodingTest(TestCase):
    def setUp(self):
        academic_year = AcademicYearFactory(year=datetime.now().year)
        self.learning_unit_year = LearningUnitYearFactory(acronym="LMEM2110",
                                                          title="Recent Continental Philosophy",
                                                          academic_year=academic_year)

        self.offer_year_1 = test_offer_year.create_offer_year("SINF2MA", "Master en Sciences Informatique",
                                                              academic_year)
        self.offer_year_2 = test_offer_year.create_offer_year("DROI1BA", "Bachelier en droit", academic_year)

        self.exam_enrollment_1 = test_exam_enrollment.create_exam_enrollment_with_student(1, "64641200", self.offer_year_1, self.learning_unit_year,
                                                                     academic_year)
        self.exam_enrollment_2 = test_exam_enrollment.create_exam_enrollment_with_student(2, "60601200", self.offer_year_2, self.learning_unit_year,
                                                                     academic_year)

        self.tutor = create_tutor_with_user(1)
        test_attribution.create_attribution(tutor=self.tutor, learning_unit_year=self.learning_unit_year)
        add_permission(self.tutor.person.user, "can_access_scoreencoding")

        self.program_manager_1 = ProgramManagerFactory(offer_year=self.offer_year_1)
        add_permission(self.program_manager_1.person.user, "can_access_scoreencoding")

        self.program_manager_2 = ProgramManagerFactory(offer_year=self.offer_year_2)
        add_permission(self.program_manager_2.person.user, "can_access_scoreencoding")

        self.Client = Client()

    def test_filter_enrollments_by_offer_year(self):
        enrollments = [self.exam_enrollment_1, self.exam_enrollment_2]

        expected = [self.exam_enrollment_1]
        actual = score_encoding.filter_enrollments_by_offer_year(enrollments, self.offer_year_1)

        self.assertListEqual(expected, actual, "Should only return enrollments for the first offer year")

    def test_tutor_encoding_with_a_student(self):
        self.client.force_login(self.tutor.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_one_student_filled())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, None, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, None, None)

    def test_tutor_encoding_final_scores_for_a_student(self):
        self.client.force_login(self.tutor.person.user)
        self.exam_enrollment_1.score_final = 16
        self.exam_enrollment_1.score_draft = 16
        self.exam_enrollment_1.save()
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_one_student_filled())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 16, 16, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, None, None)

    def test_pgm_encoding_for_a_student(self):
        self.client.force_login(self.program_manager_1.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, 15, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, None, None)

    def test_pgm_encoding_with_justification_for_a_student(self):
        self.client.force_login(self.program_manager_2.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled_and_one_with_justification())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, None, None, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, "ABSENCE_JUSTIFIED", "ABSENCE_JUSTIFIED")

    def test_tutor_encoding_with_all_students(self):
        self.client.force_login(self.tutor.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, None, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, 18, None, None, None)

    def test_tutor_double_encoding_with_all_students(self):
        self.client.force_login(self.tutor.person.user)
        prepare_exam_enrollment_for_double_encoding_validation(self.exam_enrollment_1)
        prepare_exam_enrollment_for_double_encoding_validation(self.exam_enrollment_2)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, None, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, 18, None, None, None)

    def test_tutor_encoding_with_all_students_and_a_justification(self):
        self.client.force_login(self.tutor.person.user)
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled_and_one_with_justification())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, None, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, "ABSENCE_JUSTIFIED", None)

    def test_pgm_double_encoding_for_a_student(self):
        self.client.force_login(self.program_manager_1.person.user)
        url = reverse('online_double_encoding_validation', args=[self.learning_unit_year.id])
        prepare_exam_enrollment_for_double_encoding_validation(self.exam_enrollment_1)
        response = self.client.post(url, data=self.get_form_with_all_students_filled())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, 15, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, None, None)

    def test_encoding_by_specific_criteria(self):
        self.client.force_login(self.program_manager_1.person.user)
        url = reverse('specific_criteria_submission')
        response = self.client.post(url, data=self.get_form_for_specific_criteria())

        self.refresh_exam_enrollments_from_db()
        self.assert_exam_enrollments(self.exam_enrollment_1, 15, 15, None, None)
        self.assert_exam_enrollments(self.exam_enrollment_2, None, None, None, None)

    @patch("base.utils.send_mail.send_message_after_all_encoded_by_manager")
    def test_email_after_encoding_all_students_for_offer_year(self, mock_send_email):
        self.client.force_login(self.program_manager_1.person.user)
        mock_send_email.return_value = None
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled())

        self.assertTrue(mock_send_email.called)
        (persons, enrollments, learning_unit_acronym, offer_acronym), kwargs = mock_send_email.call_args
        self.assertEqual(persons, [self.tutor.person])
        self.assertEqual(enrollments, [self.exam_enrollment_1])
        self.assertEqual(learning_unit_acronym, self.learning_unit_year.acronym)
        self.assertEqual(offer_acronym, self.offer_year_1.acronym)

    @patch("base.utils.send_mail.send_message_after_all_encoded_by_manager")
    def test_email_after_encoding_all_students_for_offer_year_with_justification(self, mock_send_email):
        self.client.force_login(self.program_manager_2.person.user)
        mock_send_email.return_value = None
        url = reverse('online_encoding_form', args=[self.learning_unit_year.id])
        response = self.client.post(url, data=self.get_form_with_all_students_filled_and_one_with_justification())

        self.assertTrue(mock_send_email.called)
        (persons, enrollments, learning_unit_acronym, offer_acronym), kwargs = mock_send_email.call_args
        self.assertEqual(persons, [self.tutor.person])
        self.assertEqual(enrollments, [self.exam_enrollment_2])
        self.assertEqual(learning_unit_acronym, self.learning_unit_year.acronym)
        self.assertEqual(offer_acronym, self.offer_year_2.acronym)

    def assert_exam_enrollments(self, exam_enrollment, score_draft, score_final, justification_draft,
                                justification_final):
        self.assertEqual(exam_enrollment.score_draft, score_draft)
        self.assertEqual(exam_enrollment.score_final, score_final)
        self.assertEqual(exam_enrollment.justification_draft, justification_draft)
        self.assertEqual(exam_enrollment.justification_final, justification_final)

    def get_form_with_one_student_filled(self):
        return {"score_" + str(self.exam_enrollment_1.id): "15",
                "justification_" + str(self.exam_enrollment_1.id): "",
                "score_changed_" + str(self.exam_enrollment_1.id): "true",
                "score_" + str(self.exam_enrollment_2.id): "",
                "justification_" + str(self.exam_enrollment_2.id): "",
                "score_changed_" + str(self.exam_enrollment_2.id): "false"
                }

    def get_form_with_all_students_filled(self):
        return {"score_" + str(self.exam_enrollment_1.id): "15",
                "justification_" + str(self.exam_enrollment_1.id): "",
                "score_changed_" + str(self.exam_enrollment_1.id): "true",
                "score_" + str(self.exam_enrollment_2.id): "18",
                "justification_" + str(self.exam_enrollment_2.id): "",
                "score_changed_" + str(self.exam_enrollment_2.id): "true"
                }

    def get_form_with_all_students_filled_and_one_with_justification(self):
        return {"score_" + str(self.exam_enrollment_1.id): "15",
                "justification_" + str(self.exam_enrollment_1.id): "",
                "score_changed_" + str(self.exam_enrollment_1.id): "true",
                "score_" + str(self.exam_enrollment_2.id): "",
                "justification_" + str(self.exam_enrollment_2.id): "ABSENCE_JUSTIFIED",
                "score_changed_" + str(self.exam_enrollment_2.id): "true"
                }

    def get_form_for_specific_criteria(self):
        return {"score_" + str(self.exam_enrollment_1.id): "15",
                "justification_" + str(self.exam_enrollment_1.id): "",
                "score_changed_" + str(self.exam_enrollment_1.id): "true",
                "program": str(self.offer_year_1.id)
                }

    def refresh_exam_enrollments_from_db(self):
        self.exam_enrollment_1.refresh_from_db()
        self.exam_enrollment_2.refresh_from_db()

class OutsideEncodingPeriodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = create_user(username='score_encoding', password='score_encoding')
        add_permission(self.user, "can_access_scoreencoding")
        self.client.login(username='score_encoding', password='score_encoding')
        self.person = test_person.create_person_with_user(user=self.user)
        academic_year = test_academic_year.create_academic_year()
        offer_year = test_offer_year.create_offer_year("SINF2MA", "Master en Sciences Informatique",academic_year)
        self.offer_year_calendar = test_offer_year_calendar.create_offer_year_calendar(offer_year, academic_year)
        self.learning_unit_year = test_learning_unit_year.create_learning_unit_year("LINGI2359",
                                                                                    "Software engineering seminar",
                                                                                    academic_year)
        self.first_session_exam = create_session_exam(1, self.learning_unit_year, self.offer_year_calendar)

    def test_redirection_to_current_exam_session(self):
        url = reverse('outside_scores_encodings_period')
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (reverse('scores_encoding'), reverse('outside_scores_encodings_period')))  # Redirection

    def test_redirection_to_outside_encoding_period(self):
        self.first_session_exam.delete()
        url = reverse('scores_encoding')
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (reverse('outside_scores_encodings_period'), reverse('scores_encoding')))  # Redirection

class GetScoreEncodingViewProgramManagerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        #Creation user/person and assign it as a "program manager"
        self.user = create_user(username='score_encoding_pgrm', password='score_encoding_pgrm')
        add_permission(self.user, "can_access_scoreencoding")
        self.client.login(username='score_encoding_pgrm', password='score_encoding_pgrm')
        self.person = test_person.create_person_with_user(user=self.user)
        academic_year = test_academic_year.create_academic_year()
        self.offer_year_bio2ma = test_offer_year.create_offer_year("BIO2MA", "Master en Biologie", academic_year)
        self.offer_year_bio2bac = test_offer_year.create_offer_year("BIO2BAC", "Bachelier en Biologie", academic_year)
        self.program_manager = test_program_manager.create_program_manager(offer_year=self.offer_year_bio2ma, person=self.person)
        self.program_manager = test_program_manager.create_program_manager(offer_year=self.offer_year_bio2bac, person=self.person)

        # Offer : BIO2MA - 2 Learning unit with exam
        self.offer_year_calendar_bio2ma = test_offer_year_calendar.create_offer_year_calendar(self.offer_year_bio2ma, academic_year)
        self.learning_unit_year = test_learning_unit_year.create_learning_unit_year("NTAR2359", "Biology methodology",
                                                                                    academic_year)
        self.learning_unit_year_2 = test_learning_unit_year.create_learning_unit_year("MIOA898", "Microsom seminar",
                                                                                    academic_year)
        self.first_session_exam = create_session_exam(1, self.learning_unit_year, self.offer_year_calendar_bio2ma)
        self.first_session_exam_2 = create_session_exam(1, self.learning_unit_year_2, self.offer_year_calendar_bio2ma)

        # Offer: BIO2BAC - 1 learning unit with exam
        self.offer_year_calendar_bio2bac = test_offer_year_calendar.create_offer_year_calendar(self.offer_year_bio2bac,
                                                                                       academic_year)
        self.learning_unit_year_3 = test_learning_unit_year.create_learning_unit_year("ECTH056", "Ecosystem theory",
                                                                                      academic_year)
        self.first_session_exam_3 = create_session_exam(1, self.learning_unit_year_3, self.offer_year_calendar_bio2bac)


        self.students=[]
        for index in range(0,20):
            # Creation of 20 students
            self.students.append(test_student.create_student("Student" + str(index), "Etudiant" + str(index), index))
            if index < 5:
                # For the 5 first students register to the BIO2MA
                offer_enrollment = test_offer_enrollment.create_offer_enrollment(self.students[index], self.offer_year_bio2ma)
                learning_unit_enrollment = test_learning_unit_enrollment.create_learning_unit_enrollment(
                                                                              offer_enrollment=offer_enrollment,
                                                                              learning_unit_year=self.learning_unit_year)
                learning_unit_enrollment_2 = test_learning_unit_enrollment.create_learning_unit_enrollment(
                                                                            offer_enrollment=offer_enrollment,
                                                                            learning_unit_year=self.learning_unit_year_2)
                test_exam_enrollment.create_exam_enrollment(self.first_session_exam, learning_unit_enrollment)
                test_exam_enrollment.create_exam_enrollment(self.first_session_exam_2, learning_unit_enrollment_2)
            else:
                # For the other register to the BIO2BAC
                offer_enrollment = test_offer_enrollment.create_offer_enrollment(self.students[index],  self.offer_year_bio2bac)
                learning_unit_enrollment = test_learning_unit_enrollment.create_learning_unit_enrollment(offer_enrollment=offer_enrollment,
                                                                                                         learning_unit_year=self.learning_unit_year_3)
                test_exam_enrollment.create_exam_enrollment(self.first_session_exam_3, learning_unit_enrollment)

    def test_get_score_encoding_list_empty(self):
        ExamEnrollment.objects.all().delete() #remove all exam enrolment [No subscription to exam]
        url = reverse('scores_encoding')
        response = self.client.get(url)
        context = response.context[-1]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(context['notes_list'])

    def test_get_score_encoding(self):
         url = reverse('scores_encoding')
         response = self.client.get(url)
         context = response.context[-1]
         self.assertEqual(response.status_code, 200)
         self.assertEqual(len(context['notes_list']),3)

def prepare_exam_enrollment_for_double_encoding_validation(exam_enrollment):
    exam_enrollment.score_reencoded = 14
    exam_enrollment.score_draft = 14
    exam_enrollment.save()


def add_permission(user, codename):
    perm = get_permission(codename)
    user.user_permissions.add(perm)


def create_program_manager_with_user(num_id, offer_year):
    program_manager = test_program_manager.create_program_manager(offer_year)

    perm = get_permission("can_access_scoreencoding")
    program_manager.person.user = create_user("pgm" + str(num_id))
    program_manager.person.user.user_permissions.add(perm)
    program_manager.person.save()
    return program_manager


def create_tutor_with_user(num_id):
    tutor = test_tutor.create_tutor(first_name="tutor" + str(num_id), last_name="tutor" + str(num_id))
    tutor.person.user = create_user("tutor" + str(num_id))
    tutor.person.save()
    return tutor


def get_permission(codename):
    return Permission.objects.get(codename=codename)


def create_user(username="foo", password="test"):
    user = User.objects.create_user(username=username, password=password, email="test@test.com")
    return user
