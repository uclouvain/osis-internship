import unittest

from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.tests.factories.cohort import CohortFactory


class ViewAffectationStatisticsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

    def test_affectation_result(self):
        cohort = CohortFactory()
        url = reverse('internship_affectation_statistics', kwargs={
            'cohort_id': cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_affectation_statics.html')

    def test_affectation_result_sumup(self):
        cohort = CohortFactory()
        url = reverse('internship_affectation_sumup', kwargs={
            'cohort_id': cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_affectation_sumup.html')
