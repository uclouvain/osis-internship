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
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.models.cohort import Cohort
from internship.tests.factories.cohort import CohortFactory


class ViewHomeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

    def test_view_cohort_selection(self):
        url = reverse('internship')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_view_cohort_get_selection(self):
        number_of_cohorts = Cohort.objects.all().count()

        response = self.client.get(reverse('internship'))
        self.assertEqual(response.status_code, 200)

        cohorts = response.context['cohorts']
        self.assertTemplateUsed(response, 'cohort/selection.html')
        self.assertEqual(cohorts.count(), number_of_cohorts)

    def test_cohort_home_not_found(self):
        response = self.client.post(reverse('internships_home', kwargs={
            'cohort_id': 0,
        }))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'page_not_found.html')

    def test_cohort_home(self):
        cohort = CohortFactory()

        response = self.client.post(reverse('internships_home', kwargs={
            'cohort_id': cohort.id
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cohort'], cohort)
