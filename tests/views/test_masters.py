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
import faker

from unittest import mock

from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory, override_settings

from internship.models import master_allocation
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.master import MasterFactory
from internship.tests.factories.master_allocation import MasterAllocationFactory
from internship.tests.factories.organization import OrganizationFactory


class MasterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()

    @override_settings(DEBUG=True)
    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_masters_index_2(self, mock_render, mock_decorators):
        from django.db import connection
        from django.db import reset_queries

        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        fake = faker.Faker()
        organization = OrganizationFactory(cohort=self.cohort, reference=fake.random_int(min=10, max=100))

        request_factory = RequestFactory()
        request = request_factory.get(reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        }))
        request.user = mock.Mock()

        from internship.views.master import masters

        reset_queries()
        self.assertEqual(len(connection.queries), 0)

        masters(request, self.cohort.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(context['cohort_id'], self.cohort.id)

    def test_masters_index(self):
        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'masters.html')

    def test_masters_index_with_master(self):
        fake = faker.Faker()

        organization = OrganizationFactory(cohort=self.cohort, reference=fake.random_int(min=10, max=100))
        master = MasterAllocationFactory(organization=organization)

        url = "{}?hospital={}".format(reverse('internships_masters', kwargs={'cohort_id': self.cohort.id}),
                                      organization.id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'masters.html')

        masters = response.context['allocations'].__dict__['object_list']
        self.assertEqual(len(masters), 1)
        self.assertEqual(masters[0], master)

    def test_masters_index_bad_masters(self):
        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'masters.html')

    def test_delete_master(self):
        master_test = MasterFactory()
        fake = faker.Faker()
        organization_test = OrganizationFactory(cohort=self.cohort, reference=fake.random_int(min=10, max=100))
        allocation = MasterAllocationFactory(master=master_test, organization=organization_test)
        url = reverse('master_delete', kwargs={
            'cohort_id': self.cohort.id,
            'master_id': master_test.id
        })
        allocations = master_allocation.find_by_master(self.cohort, master_test)
        self.assertIn(allocation, allocations)
        response = self.client.get(url)
        self.assertRedirects(response, reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        }))
        allocations = master_allocation.find_by_master(self.cohort, master_test)
        self.assertNotIn(allocation, allocations)
