##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import io
import unittest

import faker
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.tests.factories.cohort import CohortFactory
from internship.tests.utils.test_student_loader import create_csv_stream


class CohortAdminTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest', is_staff=True, is_superuser=True)
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.user.save()

    def test_cohort_simple_get(self):
        cohort = CohortFactory()

        self.client.force_login(self.user)

        url = reverse('admin:cohort-import-students',
                      kwargs={'cohort_id': cohort.id})

        response = self.client.get(url)

        self.assertTemplateUsed(response,
                                'admin/internship/cohort/import_students.html')

    def test_cohort_upload_csv_file(self):
        cohort = CohortFactory()

        self.client.force_login(self.user)
        url = reverse('admin:cohort-import-students',
                      kwargs={
                          'cohort_id': cohort.id,
                      })

        with create_csv_stream('demo.csv') as str_io:
            response = self.client.post(url, {'file_upload': str_io})
            cohort_url = reverse('admin:internship_cohort_change',
                                 args=[cohort.id])
            self.assertRedirects(response, cohort_url)

    @unittest.skip('Remove this test, useless, because we are sure we will receive .csv file')
    def test_cohort_upload_text_file(self):
        cohort = CohortFactory()

        self.client.force_login(self.user)

        url = reverse('admin:cohort-import-students',
                      kwargs={
                          'cohort_id': cohort.id,
                      })

        fake = faker.Faker()

        def row_compute():
            return ' '.join([
                fake.time(pattern='%Y-%m-%d %H:%M:%S'),
                '[{}]'.format(fake.numerify(text='########')),
                fake.random_element(elements=('ERROR', 'WARNING', 'INFO', 'DEBUG')),
                fake.sentence(nb_words=10, variable_nb_words=True)
            ])

        text = '\n'.join(row_compute()
                         for idx in range(fake.random_int(min=10, max=50)))

        with io.StringIO(text) as str_io:
            response = self.client.post(url, {'file_upload': str_io},
                                        follow=True)

            cohort_url = reverse('admin:internship_cohort_change',
                                 args=[cohort.id])

            self.assertRedirects(response, cohort_url)
