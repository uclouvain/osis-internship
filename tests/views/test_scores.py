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
from unittest import mock
from django.contrib.auth.models import User, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import gettext as _
from rest_framework import status

from base.tests.factories.student import StudentFactory
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.score import ScoreFactory


class ScoresEncodingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()
        self.period = PeriodFactory(cohort=self.cohort)
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
        for student_info in self.students:
            student = StudentFactory(person=student_info.person)
            ScoreFactory(student=student, period=self.period, cohort=self.cohort)

    def test_view_scores_encoding(self):
        url = reverse('internship_scores_encoding', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'scores.html')

    @mock.patch('internship.utils.importing.import_scores.import_xlsx')
    def test_post_upload_scores(self, mock_import):
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
        self.assertTrue(student_scores[0][1][0] in ['A', 'B', 'C', 'D', 'E'])
