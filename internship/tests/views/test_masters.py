from unittest import mock

from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.tests.factories.cohort import CohortFactory


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
