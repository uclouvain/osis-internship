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
from unittest import mock

import faker
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory, override_settings

from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.master import MasterFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialityFactory


class MasterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.cohort = CohortFactory()

    @override_settings(DEBUG=True)
    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('django.shortcuts.render')
    def test_masters_index_2(self, mock_render, mock_decorators):
        from django.db import connection
        from django.db import reset_queries

        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        fake = faker.Faker()
        organization = OrganizationFactory(cohort=self.cohort, reference=fake.random_int(min=10, max=100))
        # speciality = SpecialityFactory(cohort=self.cohort)
        master = MasterFactory(organization=organization)

        master2 = MasterFactory()

        request_factory = RequestFactory()
        request = request_factory.get(reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        }))
        request.user = mock.Mock()

        from internship.views.master import internships_masters

        reset_queries()
        self.assertEqual(len(connection.queries), 0)

        internships_masters(request, self.cohort.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(context['cohort'], self.cohort)

        masters_count = context['all_masters'].count()

        # print("Queries", len(connection.queries))
        # from pprint import pprint as pp
        # pp(connection.queries)

        from internship.models.internship_master import InternshipMaster
        self.assertEqual(masters_count,
                         InternshipMaster.objects.filter(organization=organization).count())

        specs = InternshipMaster.objects.filter(organization=organization)\
            .distinct('speciality')\
            .values_list('speciality', flat=True)\
            .order_by('speciality')

        self.assertEqual(len(context['all_spec']), specs.count())

        self.assertEqual(set(context['all_spec']), set(list(specs)))

    def test_masters_index(self):
        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internships_masters.html')

    def test_masters_index_with_master(self):
        fake = faker.Faker()

        organization = OrganizationFactory(cohort=self.cohort, reference=fake.random_int(min=10, max=100))
        master = MasterFactory(organization=organization)

        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internships_masters.html')

        masters = response.context['all_masters']
        self.assertEqual(masters.count(), 1)
        self.assertEqual(masters.first(), master)

    def test_masters_index_bad_masters(self):
        fake = faker.Faker()
        master = MasterFactory(organization=OrganizationFactory(reference=fake.random_int(min=10, max=100)))

        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internships_masters.html')

        masters = response.context['all_masters']
        self.assertEqual(masters.count(), 0)


        url = reverse('internships_masters', kwargs={
            'cohort_id': master.organization.cohort.id,
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internships_masters.html')

        masters = response.context['all_masters']
        self.assertEqual(masters.count(), 1)
        self.assertEqual(masters.first(), master)

    def test_masters_delete_dont_follow(self):
        url = reverse('delete_internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })

        with mock.patch('internship.models.internship_master.search',
                        return_value=mock.Mock()) as mock_search:
            data = {'first_name': 'demo', 'name': 'demo'}
            response = self.client.post(url, data=data)
            self.assertRedirects(response, reverse('internships_masters', kwargs={
                'cohort_id': self.cohort.id,
            }))
            self.assertTrue(mock_search.called)

    def test_masters_upload(self):
        url = reverse('upload_internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })
