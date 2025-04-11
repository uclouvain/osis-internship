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
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.datetime_safe import date
from django.utils.translation import gettext as _
from mock import Mock
from rest_framework import status

from backoffice.settings.base import INSTALLED_APPS
from base.models.student import Student
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.utils.cache import RequestCache
from internship.models.internship_score import InternshipScore, APD_NUMBER
from internship.models.internship_score_mapping import InternshipScoreMapping
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.organization import Organization
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.score import ScoreFactory, ScoreMappingFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory
from internship.views.score import _get_scores_mean
from osis_common.document.xls_build import CONTENT_TYPE_XLS


class ScoresEncodingTest(TestCase):
    def setUp(self):
        self.cohort = CohortFactory()
        self.period = PeriodFactory(name='P1', date_end=date.today() - relativedelta(months=2), cohort=self.cohort)
        self.other_period = PeriodFactory(
            name='P2',
            date_end=date.today() - relativedelta(months=1),
            cohort=self.cohort,
        )

        self.xlsfile = SimpleUploadedFile(
            name='upload.xls',
            content=str.encode('test'),
            content_type="application/vnd.ms-excel",
        )
        self.xlsxfile = SimpleUploadedFile(
            name='upload.xlsx',
            content=str.encode('test'),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.students = [InternshipStudentInformationFactory(cohort=self.cohort) for _ in range(11)]
        self.mandatory_internship = InternshipFactory(
            cohort=self.cohort, speciality=SpecialtyFactory(cohort=self.cohort)
        )
        self.long_internship = InternshipFactory(
            cohort=self.cohort, speciality=SpecialtyFactory(cohort=self.cohort, sequence=1)
        )
        self.chosen_internship = InternshipFactory(cohort=self.cohort, speciality=None)
        internships = [self.mandatory_internship, self.long_internship, self.chosen_internship]
        periods = [self.period] + [PeriodFactory(cohort=self.cohort) for _ in range(2)]
        for student_info in self.students:
            student = StudentFactory(person=student_info.person)
            for index, internship in enumerate(internships):
                affectation = StudentAffectationStatFactory(
                    student=student,
                    internship=internship,
                    speciality=internship.speciality if internship.speciality else SpecialtyFactory(cohort=self.cohort),
                    organization=OrganizationFactory(cohort=self.cohort),
                    period=periods[index]
                )
                if affectation.period.name == 'P1':
                    ScoreFactory(
                        student_affectation=affectation,
                        APD_1='A',
                        validated=True
                    )
        for apd in range(1, APD_NUMBER):
            ScoreMappingFactory(
                period=self.period,
                cohort=self.cohort,
                score_A=20, score_B=15, score_C=10, score_D=0,
                apd=apd
            )
        self.unused_period = PeriodFactory(
            name="P99",
            cohort=self.cohort,
            date_end=date.today() + relativedelta(months=+2)
        )
        self.user = PersonFactory().user
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.all_apds_validated = {'APD_{}'.format(i): 'D' for i in range(1, APD_NUMBER + 1)}

        self.client.force_login(self.user)

        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        RequestCache(user=self.user, path=url).clear()

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
        StudentAffectationStatFactory(
            student=StudentFactory(person=person),
            period__cohort=self.cohort,
            organization__cohort=self.cohort,
            speciality__cohort=self.cohort,
        )
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
        InternshipScore.objects.filter(student_affectation__student=student_without_score).delete()
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
            'all_grades_submitted_filter': True,
        }
        response = self.client.get(url, data=data)
        self.assertEqual(len(response.context['students'].object_list), len(self.students)-1)

    def test_filter_not_all_grades_submitted(self):
        student_without_score = Student.objects.first()
        InternshipScore.objects.filter(student_affectation__student=student_without_score).delete()
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
            'all_grades_submitted_filter': False,
        }
        response = self.client.get(url, data=data)
        for student in response.context['students'].object_list:
            self.assertFalse(student.periods_scores)

    def test_filter_not_all_grades_submitted_should_exclude_fake_hospitals(self):
        fake_hospital = OrganizationFactory(cohort=self.cohort, fake=True)
        student_without_score = Student.objects.first()
        InternshipScore.objects.filter(student_affectation__student=student_without_score).delete()
        ScoreFactory(
            student_affectation__student=student_without_score,
            student_affectation__organization=fake_hospital,
            student_affectation__period=self.period,
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        data = {
            'period': self.period.pk,
            'all_grades_submitted_filter': False,
        }
        response = self.client.get(url, data=data)
        self.assertEqual(len(response.context['students'].object_list), 0)

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

    def test_filter_all_apds_validated(self):
        student_with_all_apds = Student.objects.first()
        InternshipScore.objects.filter(student_affectation__student=student_with_all_apds).update(
            **self.all_apds_validated
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url, data={'all_apds_validated_filter': True})
        self.assertEqual(len(response.context['students'].object_list), 1)

    def test_filter_not_all_apds_validated(self):
        student_with_not_all_apds = Student.objects.first()
        InternshipScore.objects.all().exclude(student_affectation__student=student_with_not_all_apds).update(
            **self.all_apds_validated
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url, data={'all_apds_validated_filter': False})
        self.assertEqual(len(response.context['students'].object_list), 1)

    def test_grades_converted_to_numerical_value(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        periods_scores = response.context['students'].object_list[0].periods_scores
        self.assertDictEqual(periods_scores, {self.period.name: [20]})

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
        score = InternshipScore.objects.get(
            student_affectation__student=student,
            student_affectation__period=self.period
        )
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
        student = StudentFactory()
        score = ScoreFactory(
            student_affectation__student=student,
            student_affectation__period=self.period,
            score=edited_score,
            validated=True
        )
        url = reverse('delete_edited_score', kwargs={'cohort_id': self.cohort.pk})
        self.assertEqual(score.score, edited_score)
        response = self.client.post(url, data={
            'student': score.student_affectation.student.registration_id,
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
        student_affectation = StudentAffectationStatFactory(student=student, period=period)
        ScoreFactory(student_affectation=student_affectation, validated=True)
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

        ScoreFactory(
            student_affectation__student=student,
            student_affectation__period=self.period,
            student_affectation__organization__cohort=self.cohort,
            student_affectation__speciality__cohort=self.cohort,
            APD_1='A',
            validated=True
        )
        ScoreFactory(
            student_affectation__student=student,
            student_affectation__period=self.other_period,
            student_affectation__organization__cohort=self.cohort,
            student_affectation__speciality__cohort=self.cohort,
            APD_1='C',
            validated=True
        )

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
        periods = {'P1': [1.5], 'P2': [1.5], 'P3': [1.5]}
        evolution_score = _get_scores_mean(periods, len(periods.keys()))
        self.assertEqual(evolution_score, 2)

    def test_ajax_refresh_evolution_score(self):
        url = reverse('refresh_evolution_score', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'scores': '{"P1": [10.0], "P2": [20.0]}',
            'period': self.period.name,
            'edited': 20
        })
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(json_response['evolution_score'], 20)
        self.assertIn("'P1': 20", json_response['updated_scores'])
        self.assertIn("'P2': [20.0]", json_response['updated_scores'])

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

    def test_show_excused_score_disregarded_in_evolution_score_computation(self):
        student_info = InternshipStudentInformationFactory(cohort=self.cohort, person__last_name="A")
        student = StudentFactory(person=student_info.person)
        new_score = 10
        ScoreFactory(
            student_affectation__student=student,
            student_affectation__period=self.period,
            student_affectation__organization__cohort=self.cohort,
            student_affectation__speciality__cohort=self.cohort,
            excused=True,
            score=new_score,
            validated=True
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        filtered_object_list = [obj for obj in response.context['students'].object_list if obj == student_info]
        numeric_scores = filtered_object_list[0].numeric_scores
        evolution_score = filtered_object_list[0].evolution_score
        self.assertEqual(numeric_scores[self.period.name], [{'excused': new_score, 'reason': None}])
        self.assertEqual(evolution_score, 0)

    @mock.patch('internship.utils.importing.import_eval.import_xlsx')
    def test_post_upload_eval_success(self, mock_import):
        student_info = self.students[0]
        student = Student.objects.get(person=student_info.person)
        student_period_affectation = InternshipStudentAffectationStat.objects.filter(
            student=student, period=self.period
        ).first()
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

    def test_show_only_validated_scores(self):
        # create student with no validated score
        student_with_no_validated_score = StudentFactory(
            person=InternshipStudentInformationFactory(person__last_name='AAA', cohort=self.cohort).person
        )
        ScoreFactory(
            student_affectation__period=self.period,
            student_affectation__student=student_with_no_validated_score,
            student_affectation__organization__cohort=self.cohort,
            student_affectation__speciality__cohort=self.cohort,
            APD_1='A',
            validated=False
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        student_with_score_not_validated = response.context['students'].object_list[0]
        student_with_score_validated = response.context['students'].object_list[1]
        self.assertTrue(student_with_score_validated.scores)
        self.assertFalse(student_with_score_not_validated.scores)

    @mock.patch('internship.utils.exporting.score_encoding_xls.export_xls_with_scores')
    def test_export_only_validated_scores(self, mock_export: Mock):
        # create student with no validated score
        student_with_no_validated_score = StudentFactory(
            person=InternshipStudentInformationFactory(person__last_name='AAA', cohort=self.cohort).person
        )
        ScoreFactory(
            student_affectation__period=self.period,
            student_affectation__student=student_with_no_validated_score,
            APD_1='A',
            validated=False
        )
        url = reverse('internship_download_scores', kwargs={'cohort_id': self.cohort.pk})
        self.client.post(url, data={'period': self.period.name})
        args, kwargs = mock_export.call_args
        exported_students = args[2]
        student_with_score_not_validated = exported_students[0]
        student_with_score_validated = exported_students[1]
        self.assertFalse(student_with_score_not_validated.scores)
        self.assertTrue(student_with_score_validated.scores)

    def test_form_edit_score_consultation(self):
        score = ScoreFactory(
            student_affectation__period=self.period,
            APD_1='A',
            validated=False
        )
        url = reverse('internship_edit_score', kwargs={
            'cohort_id': self.cohort.pk,
            'student_registration_id': score.student_affectation.student.registration_id,
            'period_id': self.period.pk
        })
        response = self.client.get(url)
        self.assertTemplateUsed(response, "score_form.html")

    def test_form_edit_score_should_create_not_existing_score_and_affectation(self):
        student = StudentFactory()
        url = reverse('internship_edit_score', kwargs={
            'cohort_id': self.cohort.pk,
            'student_registration_id': student.registration_id,
            'period_id': self.period.pk
        })
        response = self.client.get(url)

        affectation = InternshipStudentAffectationStat.objects.get(student=student, period=self.period)
        score = InternshipScore.objects.get(student_affectation=affectation)

        self.assertEqual(score.student_affectation, affectation)
        self.assertEqual(affectation.student, student)

        self.assertTemplateUsed(response, "score_form.html")

    def test_form_edit_score_post_invalid(self):
        score = ScoreFactory(
            student_affectation__period=self.period,
            APD_1='A',
            validated=False
        )
        url = reverse('internship_edit_score', kwargs={
            'cohort_id': self.cohort.pk,
            'student_registration_id': score.student_affectation.student.registration_id,
            'period_id': self.period.pk
        })
        response = self.client.post(url, data={'apd-1': 'B'})
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertTemplateUsed(response, "score_form.html")
        self.assertEqual(messages_list[0].level_tag, 'error')
        # keep user input values when reloading form if error
        self.assertEqual(response.context['score'].APD_1, 'B')

    def test_form_edit_score_post_valid(self):
        score = ScoreFactory(
            student_affectation__period=self.period,
            APD_1='A',
            validated=False
        )
        url = reverse('internship_edit_score', kwargs={
            'cohort_id': self.cohort.pk,
            'student_registration_id': score.student_affectation.student.registration_id,
            'period_id': self.period.pk
        })
        response = self.client.post(url, data={
            'apd-1': 'B',
            'apd-2': 'B',
            'apd-3': 'B',
            'apd-4': 'B',
            'apd-5': 'B',
        })
        messages_list = [msg for msg in response.wsgi_request._messages]
        self.assertRedirects(response, reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk}))
        self.assertEqual(messages_list[0].level_tag, 'success')

    def test_should_display_internship_comments(self):
        # create student with comment
        student_with_comment = StudentFactory(
            person=InternshipStudentInformationFactory(person__last_name='AAA', cohort=self.cohort).person
        )
        comment_content = "test comment"
        ScoreFactory(
            student_affectation__period=self.period,
            student_affectation__student=student_with_comment,
            student_affectation__organization__cohort=self.cohort,
            student_affectation__speciality__cohort=self.cohort,
            APD_1='A',
            validated=True,
            comments={"impr_areas": comment_content}
        )
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        student_with_comment = response.context['students'].object_list[0]
        self.assertEqual(student_with_comment.comments[self.period.name], [{_("Improvement areas"): comment_content}])

    def test_should_filter_scores_by_organization(self):
        organization = Organization.objects.first()
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url, data={'organization': organization.pk})
        student = response.context['students'].object_list[0]
        self.assertIn(organization.name, str(student.organizations))

    def test_should_filter_scores_by_specialty(self):
        specialty = InternshipSpeciality.objects.first()
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url, data={'specialty': specialty.pk})
        student = response.context['students'].object_list[0]
        self.assertIn(specialty.name, str(student.specialties))

    def test_should_filter_scores_by_specialty_and_organization(self):
        organization = Organization.objects.first()
        specialty = InternshipSpeciality.objects.first()

        student_info = InternshipStudentInformationFactory(cohort=self.cohort, person__last_name="A")
        ScoreFactory(
            student_affectation__student=StudentFactory(person=student_info.person),
            student_affectation__period=self.period,
            student_affectation__organization=organization,
            student_affectation__speciality=specialty,
            validated=True
        )

        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url, data={'organization': organization.pk, 'specialty': specialty.pk})
        student = response.context['students'].object_list[0]
        self.assertIn(specialty.name, str(student.specialties))
        self.assertIn(organization.name, str(student.organizations))
        self.assertEqual(student.person, student_info.person)

    def test_should_download_summary(self):
        url = reverse('internship_download_summary', kwargs={
            'cohort_id': self.cohort.pk,
            'student_id': self.students[0].pk
        })
        response = self.client.get(url)
        cohort_slug = self.cohort.name.strip().replace(' ', '_')
        student_name = self.students[0].person.last_name
        self.assertEqual(
            response.headers['Content-Disposition'],
            f"attachment; filename=score_summary_{cohort_slug}_{student_name}.pdf"
        )
