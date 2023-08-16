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

import pendulum
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from internship.business.statistics import load_solution_sol
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory


class ViewAffectationStatisticsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)
        cls.cohort = CohortFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_affectation_result(self):
        url = reverse('internship_affectation_hospitals', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_affectation_hospitals.html')

    def test_affectation_result_sumup(self):
        specialty = SpecialtyFactory(cohort=self.cohort)
        organization = OrganizationFactory(cohort=self.cohort)
        affectation = StudentAffectationStatFactory(organization=organization, speciality=specialty)

        url = reverse('internship_affectation_sumup', kwargs={
            'cohort_id': self.cohort.id
        })

        response = self.client.get("{}?hospital={}&specialty={}".format(url, organization.id, specialty.id))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_affectation_sumup.html')

        self.assertEqual(response.context[0]['active_hospital'], affectation.organization)
        self.assertEqual(response.context[0]['active_specialty'], affectation.speciality)

        self.assertIn(affectation.organization, response.context[0]['hospitals'])
        self.assertIn(affectation.speciality.name, response.context[0]['hospital_specialties'])

    def test_affectation_statistics(self):
        url = reverse('internship_affectation_statistics', kwargs={
            'cohort_id': self.cohort.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_affectation_statistics.html')

    def test_load_solution_should_sort_periods_for_humans(self):
        specialty = SpecialtyFactory(cohort=self.cohort)

        periods = [
            PeriodFactory(
                cohort=self.cohort,
                date_end=pendulum.today()._add_timedelta(timedelta(days=30*_)).end_of('month')
            ) for _ in range(11)
        ]

        periods.insert(1, PeriodFactory(name="A1", cohort=self.cohort))
        periods.insert(-1, PeriodFactory(name="Z1", cohort=self.cohort))

        organization = OrganizationFactory(cohort=self.cohort)
        affectations = [
            StudentAffectationStatFactory(period=p, organization=organization, speciality=specialty) for p in periods
        ]

        sol = load_solution_sol(self.cohort, affectations)

        ordered_keys = list(sol[list(sol.keys())[0]].keys())
        ordered_keys.remove('score')

        self.assertEqual(ordered_keys.index('A1'), 0)
        self.assertEqual(ordered_keys.index('Z1'), len(ordered_keys) - 1)
