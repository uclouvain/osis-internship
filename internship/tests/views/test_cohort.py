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

from internship.forms.cohort import CohortForm
from internship.models.cohort import Cohort
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.organization import Organization
from internship.tests.factories.cohort import CohortFactory

import datetime

from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.organization_address import OrganizationAddressFactory
from internship.tests.factories.speciality import SpecialityFactory


class ViewCohortTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

    def test_new_get(self):
        url = reverse('cohort_new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cohort/cohort_form.html')

    def test_new_port(self):
        cohort = CohortFactory.build()

        form_data = {
            'name': cohort.name,
            'publication_start_date': cohort.publication_start_date.strftime('%Y-%m-%d'),
            'subscription_start_date': cohort.subscription_start_date.strftime('%Y-%m-%d'),
            'subscription_end_date': cohort.subscription_end_date.strftime('%Y-%m-%d'),
            'free_internships_number': cohort.free_internships_number,
            'description': cohort.description,
        }

        form = CohortForm(data=form_data)

        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('cohort_new'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('internship'))

    def test_copy_organization_from_cohort(self):
        cohort = CohortFactory()

        organization = OrganizationFactory(cohort=cohort)
        address = OrganizationAddressFactory(organization=organization)

        speciality = SpecialityFactory(cohort=cohort)

        copy_cohort_name = 'Copy of {} {}'.format(cohort.name, datetime.datetime.now())

        form_data = {
            'name': copy_cohort_name,
            'publication_start_date': cohort.publication_start_date.strftime('%Y-%m-%d'),
            'subscription_start_date': cohort.subscription_start_date.strftime('%Y-%m-%d'),
            'subscription_end_date': cohort.subscription_end_date.strftime('%Y-%m-%d'),
            'free_internships_number': cohort.free_internships_number,
            'description': cohort.description,

            'copy_organizations_from_cohort': cohort.id,
            'copy_specialities_from_cohort': cohort.id,
        }

        form = CohortForm(data=form_data)

        self.assertTrue(form.is_valid())

        response = self.client.post(reverse('cohort_new'), data=form_data)
        self.assertRedirects(response, reverse('internship'))

        copy_cohort = Cohort.objects.filter(name=copy_cohort_name).first()

        self.assertEqual(copy_cohort.name, copy_cohort_name)

        copy_organization = Organization.objects.filter(cohort=copy_cohort).first()
        copy_speciality = InternshipSpeciality.objects.filter(cohort=copy_cohort).first()

        self.assertIsNotNone(copy_organization)
        self.assertIsNotNone(copy_speciality)

        self.assertEqual(organization.name, copy_organization.name)
        self.assertEqual(speciality.name, copy_speciality.name)

    def test_edit_cohort_not_found(self):
        response = self.client.get(reverse('cohort_edit', kwargs={
            'cohort_id': 0,
        }))

        self.assertEqual(response.status_code, 404)

    def test_edit_get_cohort_found(self):
        cohort = CohortFactory()

        response = self.client.get(reverse('cohort_edit', kwargs={
            'cohort_id': cohort.id,
        }))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cohort/cohort_form.html')

    def test_edit_post_cohort_found(self):
        cohort = CohortFactory()

        four_weeks = datetime.timedelta(weeks=4)

        original_cohort = Cohort.objects.get(pk=cohort.id)

        original_cohort.name = 'Update {}'.format(cohort.name)

        original_cohort.publication_start_date += four_weeks
        original_cohort.subscription_start_date += four_weeks
        original_cohort.subscription_end_date += four_weeks

        form_data = {
            'name': original_cohort.name,
            'publication_start_date': original_cohort.publication_start_date.strftime('%Y-%m-%d'),
            'subscription_start_date': original_cohort.subscription_start_date.strftime('%Y-%m-%d'),
            'subscription_end_date': original_cohort.subscription_end_date.strftime('%Y-%m-%d'),
            'free_internships_number': cohort.free_internships_number,
            'description': cohort.description,
        }
        form = CohortForm(data=form_data)

        self.assertTrue(form.is_valid())

        url = reverse('cohort_edit', kwargs={
            'cohort_id': cohort.id
        })

        response = self.client.post(url, data=form_data)

        self.assertRedirects(response, reverse('internship'))

        cohort.refresh_from_db()

        self.assertEqual(cohort.name, original_cohort.name)
        self.assertEqual(cohort.publication_start_date, original_cohort.publication_start_date)
        self.assertEqual(cohort.subscription_start_date, original_cohort.subscription_start_date)
        self.assertEqual(cohort.subscription_end_date, original_cohort.subscription_end_date)

