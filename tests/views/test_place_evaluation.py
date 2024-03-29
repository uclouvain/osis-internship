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
from datetime import timedelta

from dateutil.utils import today
from django.contrib.auth.models import Permission, User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from internship.models.internship_place_evaluation_item import PlaceEvaluationItem
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.place_evaluation_item import PlaceEvaluationItemFactory
from osis_common.document.xls_build import CONTENT_TYPE_XLS


class PlaceEvaluationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)
        cls.cohort = CohortFactory()
        cls.organization = OrganizationFactory(cohort=cls.cohort)
        cls.periods = [
            PeriodFactory(name=f"P{_}", date_end=today()+timedelta(days=_), cohort=cls.cohort) for _ in [1, 2, 3]
        ]

    def setUp(self):
        self.client.force_login(self.user)
        self.items = [PlaceEvaluationItemFactory(cohort=self.cohort) for _ in range(3)]
        self.item = self.items[1]

    def test_place_evaluation(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('place_evaluation', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_evaluation.html')

    def test_place_evaluation_item_new(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('place_evaluation_new', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_evaluation_item_form.html')
        self.assertFalse(response.context['form'].instance.id)

    def test_place_evaluation_item_edit(self):
        kwargs = {'cohort_id': self.cohort.id, 'item_id': self.item.id}
        url = reverse('place_evaluation_edit', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_evaluation_item_form.html')
        self.assertEqual(response.context['form'].instance, self.item)

    def test_place_evaluation_item_delete(self):
        item_exists = PlaceEvaluationItem.objects.filter(id=self.item.id).exists
        self.assertTrue(item_exists())
        kwargs = {'cohort_id': self.cohort.id, 'item_id': self.item.id}
        url = reverse('place_evaluation_delete', kwargs=kwargs)
        response = self.client.get(url)
        self.assertRedirects(response, reverse('place_evaluation', kwargs={'cohort_id': self.cohort.id}))
        self.assertFalse(item_exists())

    def test_place_evaluation_move_up(self):
        original_order = self.item.order
        kwargs = {'cohort_id': self.cohort.id, 'item_id': self.item.id}
        url = reverse('place_evaluation_item_move_up', kwargs=kwargs)
        response = self.client.get(url)
        self.assertRedirects(response, reverse('place_evaluation', kwargs={'cohort_id': self.cohort.id}))
        self.item.refresh_from_db()
        self.assertEqual(self.item.order, original_order-1)

    def test_place_evaluation_move_down(self):
        original_order = self.item.order
        kwargs = {'cohort_id': self.cohort.id, 'item_id': self.item.id}
        url = reverse('place_evaluation_item_move_down', kwargs=kwargs)
        response = self.client.get(url)
        self.assertRedirects(response, reverse('place_evaluation', kwargs={'cohort_id': self.cohort.id}))
        self.item.refresh_from_db()
        self.assertEqual(self.item.order, original_order+1)

    def test_place_evaluation_results(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('place_evaluation_results', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_evaluation_results.html')

    def test_export_place_evaluation_results(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('export_place_evaluation_results', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response['content-type'], CONTENT_TYPE_XLS.split(';')[0])

    def test_place_evaluation_config(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('place_evaluation_config', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'place_evaluation_config.html')

    def test_save_place_evaluation_config(self):
        kwargs = {'cohort_id': self.cohort.id, }
        url = reverse('place_evaluation_config', kwargs=kwargs)
        self.client.post(url, data={'active_period': ['P1']})

        for period in self.periods:
            period.refresh_from_db()

        self.assertTrue(self.periods[0].place_evaluation_active)
        self.assertFalse(self.periods[1].place_evaluation_active)
