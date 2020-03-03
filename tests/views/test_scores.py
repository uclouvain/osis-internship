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
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock, skipUnless

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.datetime_safe import date
from django.utils.translation import gettext as _
from rest_framework import status

from backoffice.settings.base import INSTALLED_APPS
from base.models.student import Student
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from internship.models.internship_score import InternshipScore, APD_NUMBER
from internship.models.internship_score_mapping import InternshipScoreMapping
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.score import ScoreFactory, ScoreMappingFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory
from internship.views.score import _get_scores_mean
from osis_common.document.xls_build import CONTENT_TYPE_XLS


class ScoresEncodingTest(TestCase):
    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.period = PeriodFactory(name='P1', date_end=date.today()-relativedelta(months=2), cohort=cls.cohort)
        cls.other_period = PeriodFactory(name='P2', date_end=date.today()-relativedelta(months=1),  cohort=cls.cohort,)
        cls.xlsfile = SimpleUploadedFile(
            name='upload.xls',
            content=str.encode('test'),
            content_type="application/vnd.ms-excel",
        )
        cls.xlsxfile = SimpleUploadedFile(
            name='upload.xlsx',
            content=str.encode('test'),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        cls.students = [InternshipStudentInformationFactory(cohort=cls.cohort) for _ in range(11)]
        cls.mandatory_internship = InternshipFactory(
            cohort=cls.cohort, speciality=SpecialtyFactory(cohort=cls.cohort)
        )
        cls.long_internship = InternshipFactory(
            cohort=cls.cohort, speciality=SpecialtyFactory(cohort=cls.cohort, sequence=1)
        )
        cls.chosen_internship = InternshipFactory(cohort=cls.cohort, speciality=None)
        internships = [cls.mandatory_internship, cls.long_internship, cls.chosen_internship]
        periods = [PeriodFactory(cohort=cls.cohort) for _ in range(2)]
        periods.append(cls.period)
        for student_info in cls.students:
            student = StudentFactory(person=student_info.person)
            for index, internship in enumerate(internships):
                StudentAffectationStatFactory(
                    student=student,
                    internship=internship,
                    speciality=internship.speciality if internship.speciality else SpecialtyFactory(),
                    period=periods[index]
                )
            ScoreFactory(student=student, period=cls.period, cohort=cls.cohort, APD_1='A')
        for apd in range(1, APD_NUMBER):
            ScoreMappingFactory(
                period=cls.period,
                cohort=cls.cohort,
                score_A=20, score_B=15, score_C=10, score_D=0,
                apd=apd
            )
        cls.unused_period = PeriodFactory(name="P99", cohort=cls.cohort, date_end=date.today()+relativedelta(months=+2))
        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

    def test_view_scores_encoding(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'scores.html')

    @mock.patch('internship.utils.importing.import_scores.import_xlsx')
    def test_post_upload_scores_success(self, mock_import):
        mock_import.return_value = None
        url = reverse('internship_upload_scores', kwargs={
            'cohort_id': self.cohort.pk,
        })
        redirect_url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(
            url,
            data={
                'file_upload': self.xlsxfile,
                'period': self.period.name
            }
        )
        self.assertRedirects(response, redirect_url)
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertEqual(messages_list[0].level_tag, 'success')

    @mock.patch('internship.utils.importing.import_scores.import_xlsx')
    def test_post_upload_scores_invalid_registration_id_error(self, mock_import):
        mock_import.return_value = {
            'registration_error':
            [
                [SimpleNamespace(row=6, value='invalid registration id')],
                [SimpleNamespace(row=7, value='invalid registration id')],
            ]
        }
        url = reverse('internship_upload_scores', kwargs={
            'cohort_id': self.cohort.pk,
        })
        redirect_url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(
            url,
            data={
                'file_upload': self.xlsxfile,
                'period': self.period.name
            }
        )
        self.assertRedirects(response, redirect_url)
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertIn(messages_list[0].level_tag, 'error')
        self.assertIn(self.period.name, str(messages_list[0]))

    @mock.patch('internship.utils.importing.import_scores.import_xlsx')
    def test_post_upload_scores_invalid_period(self, mock_import):
        mock_import.return_value = {'period_error': 'invalid_period'}
        url = reverse('internship_upload_scores', kwargs={
            'cohort_id': self.cohort.pk,
        })
        redirect_url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(
            url,
            data={
                'file_upload': self.xlsxfile,
                'period': self.period.name
            }
        )
        self.assertRedirects(response, redirect_url)
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertIn(messages_list[0].level_tag, 'error')
        self.assertIn('invalid_period', str(messages_list[0]))

    def test_post_upload_scores_extension_error(self):
        url = reverse('internship_upload_scores', kwargs={
            'cohort_id': self.cohort.pk,
        })
        redirect_url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(
            url,
            data={
                'file_upload': self.xlsfile,
                'period': self.period.name
            }
        )
        self.assertRedirects(response, redirect_url)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].level_tag, "error")
        self.assertIn(_('File extension must be .xlsx'), messages[0].message)

    def test_scores_encoding_paginated_view(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        self.assertEqual(len(response.context['students'].object_list), 10)
        self.assertEqual(response.context['students'].paginator.num_pages, 2)

    def test_append_scores_to_student(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        student_scores = response.context['students'].object_list[0].scores
        self.assertEqual(student_scores[0][0], self.period.name)
        self.assertIn(student_scores[0][1][0], [score[0] for score in InternshipScore.SCORE_CHOICES])

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_search_student_by_name_unaccent(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        person = PersonFactory(last_name="Éçàüî")
        searched_student = InternshipStudentInformationFactory(person=person, cohort=self.cohort)
        data = {
            'free_text': searched_student.person.last_name,
        }
        response = self.client.get(url, data=data)
        self.assertEqual(response.context['students'].object_list[0], searched_student)

    def test_search_scores_by_period(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
        }
        response = self.client.get(url, data=data)
        for student in response.context['students'].object_list:
            self.assertEqual(list(student.periods_scores.keys()), [self.period.name])

    def test_filter_all_grades_submitted(self):
        student_without_score = Student.objects.first()
        InternshipScore.objects.filter(student=student_without_score).delete()
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
            'all_grades_submitted_filter': True,
        }
        response = self.client.get(url, data=data)
        self.assertEqual(len(response.context['students'].object_list), len(self.students)-1)

    def test_filter_not_all_grades_submitted(self):
        student_without_score = Student.objects.first()
        InternshipScore.objects.filter(student=student_without_score).delete()
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
            'all_grades_submitted_filter': False,
        }
        response = self.client.get(url, data=data)
        for student in response.context['students'].object_list:
            self.assertFalse(student.periods_scores)

    def test_filter_evaluations_submitted(self):
        student_affectations = InternshipStudentAffectationStat.objects.filter(student__person=self.students[0].person)
        student_affectations.update(internship_evaluated=True)
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
            'evaluations_submitted_filter': True,
        }
        response = self.client.get(url, data=data)
        self.assertEqual(response.context['students'].object_list, [self.students[0]])

    def test_grades_converted_to_numerical_value(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        periods_scores = response.context['students'].object_list[0].periods_scores
        self.assertDictEqual(periods_scores, {self.period.name: 20})

    def test_export_scores(self):
        url = reverse('internship_download_scores', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'period': [self.period]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['content-type'],
            CONTENT_TYPE_XLS.split(';')[0]
        )

    def test_save_mapping(self):
        url = reverse('save_internship_score_mapping', kwargs={'cohort_id': self.cohort.pk})
        mapping = {'A': 10, 'B': 12, 'C': 16, 'D': 18}
        post_data = {}
        for key, value in mapping.items():
            post_data.update({'mapping{}_P1'.format(key): [mapping[key] for _ in range(1, APD_NUMBER)]})
        post_data.update({'activePeriod': 'P1'})
        self.client.post(url, data=post_data)
        mappings = InternshipScoreMapping.objects.filter(cohort=self.cohort)
        for m in mappings:
            for key, value in mapping.items():
                self.assertEqual(vars(m)['score_{}'.format(key)], value)

    def test_ajax_edit_score(self):
        edited_score = 10
        computed_score = 20
        student = Student.objects.first()
        score = InternshipScore.objects.get(student=student, period=self.period)
        self.assertIsNone(score.score)
        url = reverse('save_edited_score', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'student': student.registration_id,
            'edited': edited_score,
            'computed': computed_score,
            'period': self.period.name,
        })
        score.refresh_from_db()
        self.assertTemplateUsed(response, 'fragment/score_cell.html')
        self.assertEqual(score.score, edited_score)

    def test_ajax_delete_score(self):
        edited_score = 10
        computed_score = 20
        student = Student.objects.first()
        score = ScoreFactory(cohort=self.cohort, student=student, period=self.period, score=edited_score)
        url = reverse('delete_edited_score', kwargs={'cohort_id': self.cohort.pk})
        self.assertEqual(score.score, edited_score)
        response = self.client.post(url, data={
            'student': score.student.registration_id,
            'computed': computed_score,
            'period': self.period.name,
        })
        score.refresh_from_db()
        self.assertTemplateUsed(response, 'fragment/score_cell.html')
        self.assertIsNone(score.score)

    @mock.patch('internship.utils.mails.mails_management.send_score_encoding_recap')
    def test_send_recap(self, mock_send_mail):
        student_info = InternshipStudentInformationFactory(cohort=self.cohort)
        student = StudentFactory(person=student_info.person)
        period = PeriodFactory(name='PTEST', cohort=self.cohort, date_end=date.today()-timedelta(days=1))
        StudentAffectationStatFactory(student=student, period=period)
        ScoreFactory(period=self.period, student=student, cohort=self.cohort)
        url = reverse('send_summary', kwargs={'cohort_id': self.cohort.pk, 'period_id': period.pk})
        response = self.client.post(url, data={
            'selected_student': [student_info.pk]
        })
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertIn(
            _("Summaries have been sent successfully"),
            messages_list
        )
        self.assertTrue(mock_send_mail.called)

    def test_ajax_save_evaluation_status(self):
        affectation = StudentAffectationStatFactory(
            student=StudentFactory(),
            period=PeriodFactory(cohort=self.cohort)
        )
        self.assertFalse(affectation.internship_evaluated)
        url = reverse('save_evaluation_status', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'student': affectation.student.registration_id,
            'period': affectation.period.name,
            'status': 'true'
        })
        affectation.refresh_from_db()
        self.assertEqual(response.status_code, 204)
        self.assertTrue(affectation.internship_evaluated)

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_compute_evolution_score(self):
        student_name = "test_student"
        student_info = InternshipStudentInformationFactory(person__last_name=student_name, cohort=self.cohort)
        student = StudentFactory(person=student_info.person)
        PeriodFactory(name='last_period', cohort=self.cohort)
        ScoreFactory(student=student, period=self.period, cohort=self.cohort, APD_1='A')
        ScoreFactory(student=student, period=self.other_period, cohort=self.cohort, APD_1='C')
        ScoreMappingFactory(
            period=self.other_period,
            cohort=self.cohort,
            score_A=20, score_B=15, score_C=10, score_D=0,
            apd=1
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url, {'free_text': student_name})
        evolution_score = response.context['students'].object_list[0].evolution_score
        self.assertEqual(evolution_score, 15)

    def test_round_half_up_evolution_score(self):
        periods = {'P1': 1.5, 'P2': 1.5, 'P3': 1.5}
        evolution_score = _get_scores_mean(periods, len(periods.keys()))
        self.assertEqual(evolution_score, 2)

    def test_ajax_refresh_evolution_score(self):
        url = reverse('refresh_evolution_score', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'scores': '{"P1": 10.0, "P2": 20.0}',
            'period': self.period.name,
            'edited': 20
        })
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(json_response['evolution_score'], 20)
        self.assertIn("'P1': 20", json_response['updated_scores'])
        self.assertIn("'P2': 20", json_response['updated_scores'])

    def test_ajax_save_evolution_score(self):
        computed_score = 0
        new_score = 20
        student_info = InternshipStudentInformationFactory(cohort=self.cohort)
        student = StudentFactory(person=student_info.person)
        self.assertIsNone(student_info.evolution_score)
        url = reverse('save_evolution_score', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'computed': computed_score,
            'edited': new_score,
            'student': student.registration_id,
            'scores': '{}',
        })
        student_info.refresh_from_db()
        self.assertTemplateUsed(response, 'fragment/evolution_score_cell.html')
        self.assertEqual(student_info.evolution_score, new_score)

    def test_ajax_delete_evolution_score(self):
        computed_score = 0
        student_info = InternshipStudentInformationFactory(cohort=self.cohort, evolution_score=20)
        student = StudentFactory(person=student_info.person)
        url = reverse('delete_evolution_score', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'computed': computed_score,
            'scores': '{"P1": 0, "P2": 0}',
            'student': student.registration_id
        })
        student_info.refresh_from_db()
        self.assertTemplateUsed(response, 'fragment/evolution_score_cell.html')
        self.assertIsNone(student_info.evolution_score)

    def test_ajax_empty_score(self):
        student = Student.objects.first()
        url = reverse('empty_score', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'period_name': self.period.name,
            'registration_id': student.registration_id,
        })
        excused_score = InternshipScore.objects.filter(excused=True)
        self.assertTemplateUsed(response, 'fragment/score_cell.html')
        self.assertTrue(excused_score.exists())

    @mock.patch('internship.utils.importing.import_eval.import_xlsx')
    def test_post_upload_eval_success(self, mock_import):
        student_info = self.students[0]
        student = Student.objects.get(person=student_info.person)
        student_period_affectation = InternshipStudentAffectationStat.objects.get(
            student=student,
            period=self.period
        )
        self.assertFalse(student_period_affectation.internship_evaluated)
        mock_import.return_value = [{'registration_id': student.registration_id, 'period': self.period.name}]
        url = reverse('internship_upload_eval', kwargs={
            'cohort_id': self.cohort.pk,
        })
        redirect_url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(
            url,
            data={
                'file_upload': self.xlsxfile
            }
        )
        student_period_affectation.refresh_from_db()
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertRedirects(response, redirect_url)
        self.assertEqual(messages_list[0].level_tag, 'success')
        self.assertTrue(student_period_affectation.internship_evaluated)

    @mock.patch('internship.utils.importing.import_eval.import_xlsx')
    def test_post_upload_eval_error(self, mock_import):
        student = StudentFactory()
        mock_import.return_value = [{'registration_id': student.registration_id, 'period': self.period.name}]
        url = reverse('internship_upload_eval', kwargs={
            'cohort_id': self.cohort.pk,
        })
        redirect_url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(
            url,
            data={
                'file_upload': self.xlsxfile
            }
        )
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertRedirects(response, redirect_url)
        self.assertEqual(messages_list[0].level_tag, 'error')
        self.assertIn(student.registration_id, str(messages_list[0]))
