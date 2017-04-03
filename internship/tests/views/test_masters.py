from unittest import mock

import faker
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.master import MasterFactory
from internship.tests.factories.organization import OrganizationFactory


class MasterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.cohort = CohortFactory()

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
