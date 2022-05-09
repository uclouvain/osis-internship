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
from django.contrib.auth.models import User
from django.db.models import Max
from django.test import TestCase
from django.urls import reverse

from internship.models.cohort import Cohort
from internship.models.period import Period
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.period import PeriodFactory


class PeriodTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('demo-internship', email='demo@demo.org', password='secret')
        cls.cohort = CohortFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_list_periods_but_cohort_not_exist(self):
        unknown_cohort_id = Cohort.objects.all().aggregate(Max('id'))['id__max'] + 1
        url = reverse('internships_periods', kwargs={'cohort_id': unknown_cohort_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_list_periods_new_cohort(self):
        url = reverse('internships_periods', kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'periods.html')
        self.assertEqual(len(response.context['periods']), 0)

    def test_list_periods_existing_cohort_with_periods(self):
        period = PeriodFactory(cohort=self.cohort)

        url = reverse('internships_periods', kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(url)

        self.assertEqual(len(response.context['periods']), 1)
        self.assertEqual(response.context['periods'][0], period)

    def test_period_create_cohort_not_exist(self):
        unknown_cohort_id = Cohort.objects.all().aggregate(Max('id'))['id__max'] + 1

        url = reverse('periods_create', kwargs={'cohort_id': unknown_cohort_id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_period_create_cohort_exist(self):
        url = reverse('periods_create', kwargs={'cohort_id': self.cohort.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'period_create.html')

    def test_period_save_ok(self):
        period = PeriodFactory(cohort=self.cohort, name='P24', remedial=False)

        queryset = Period.objects.filter(cohort=self.cohort, name='P24')
        self.assertEqual(queryset.count(), 1)
        period_db = queryset.first()
        self.assertEqual(period_db.id, period.id)

        url = self.url_for_cohort_period('period_save', self.cohort, period)
        data = {
            'name': 'P243',
            'date_start': period.date_start.date(),
            'date_end': period.date_end.date(),
            'remedial': True
        }
        response = self.client.post(url, data=data)

        queryset = Period.objects.filter(cohort=self.cohort, name='P243')
        self.assertEqual(queryset.count(), 1)

        period_db = queryset.first()
        self.assertEqual(period_db.id, period.id)
        self.assertEqual(period_db.date_start, period.date_start.date())
        self.assertEqual(period_db.date_end, period.date_end.date())
        self.assertTrue(period_db.remedial)

        kwargs = {
            'cohort_id': self.cohort.id,
        }

        self.assertRedirects(
            response,
            reverse('internships_periods', kwargs=kwargs)
        )

    def test_period_new_cohort_not_exist(self):
        unknown_cohort_id = Cohort.objects.all().aggregate(Max('id'))['id__max'] + 1
        url = reverse('period_new', kwargs={'cohort_id': unknown_cohort_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_period_new_cohort_exist(self):
        url = reverse('period_new', kwargs={'cohort_id': self.cohort.id})
        period_factory = PeriodFactory.build()

        period = {
            'name': period_factory.name,
            'date_start': period_factory.date_start.strftime('%Y-%m-%d'),
            'date_end': period_factory.date_end.strftime('%Y-%m-%d'),
        }
        response = self.client.post(url, data=period, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_period_delete_ok(self):
        period = PeriodFactory(cohort=self.cohort)

        from internship.models.period import Period
        queryset = Period.objects.filter(cohort=self.cohort)

        self.assertEqual(queryset.count(), 1)

        url = self.url_for_cohort_period('period_delete', self.cohort, period)
        response = self.client.get(url)

        kwargs = {
            'cohort_id': self.cohort.id
        }
        self.assertRedirects(
            response,
            reverse('internships_periods', kwargs=kwargs)
        )

        queryset = Period.objects.filter(cohort=self.cohort)
        self.assertEqual(queryset.count(), 0)

    def test_period_delete_cohort_404(self):
        unknown_cohort_id = Cohort.objects.all().aggregate(Max('id'))['id__max'] + 1

        url = self.url_for_cohort_period('period_delete', unknown_cohort_id, 0)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_period_delete_cohort_ok_period_404(self):
        period = PeriodFactory()

        url = self.url_for_cohort_period('period_delete', self.cohort, period)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_period_get_ok(self):
        period = PeriodFactory(cohort=self.cohort)

        url = self.url_for_cohort_period('period_get', self.cohort, period)

        response = self.client.get(url)
        self.assertTemplateUsed(response, 'period_create.html')
        self.assertEqual(response.context['period'], period)
        self.assertEqual(response.context['cohort'], self.cohort)

        url_form = self.url_for_cohort_period('period_save', self.cohort, period)
        self.assertEqual(response.context['url_form'], url_form)

    def test_period_get_cohort_not_exist(self):
        unknown_cohort_id = Cohort.objects.all().aggregate(Max('id'))['id__max'] + 1

        url = self.url_for_cohort_period('period_get', unknown_cohort_id, 0)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_period_get_cohort_exist_but_period_not_exist(self):
        url = self.url_for_cohort_period('period_get', self.cohort, 0)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_period_get_cohort_exist_but_period_not_assign_to_cohort(self):
        period = PeriodFactory()

        url = self.url_for_cohort_period('period_get', self.cohort, period)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @staticmethod
    def url_for_cohort_period(view_name, cohort, period):
        kwargs = {
            'cohort_id': cohort if isinstance(cohort, int) else cohort.id,
            'period_id': period if isinstance(period, int) else period.id,
        }
        return reverse(view_name, kwargs=kwargs)
