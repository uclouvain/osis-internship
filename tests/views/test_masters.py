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
import json
from unittest import skipUnless

import faker
from django.contrib.auth.models import Permission, User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from backoffice.settings.base import INSTALLED_APPS
from base.models.enums import person_source_type
from base.models.person import Person
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_address import PersonAddressFactory
from internship.models import master_allocation
from internship.models.internship_master import InternshipMaster
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.master import MasterFactory
from internship.tests.factories.master_allocation import MasterAllocationFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory
from osis_common.document.xls_build import CONTENT_TYPE_XLS


class MasterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)
        cls.cohort = CohortFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_masters_index(self):
        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'masters.html')

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_search_master_by_name_unaccent(self):
        organization = OrganizationFactory(cohort=self.cohort)
        master_with_accent = MasterFactory(person__last_name='Éçàüî')
        MasterAllocationFactory(organization=organization, master=master_with_accent)
        url = reverse('internships_masters', kwargs={
            'cohort_id': self.cohort.id,
        })
        query_string = '?name={}'.format("Éçàüî")
        response = self.client.get("{}{}".format(url, query_string))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['allocations'].object_list[0].master, master_with_accent)

    def test_masters_index_with_master(self):
        fake = faker.Faker()

        organization = OrganizationFactory(cohort=self.cohort, reference=fake.random_int(min=10, max=100))
        master = MasterAllocationFactory(organization=organization)

        url = "{}?hospital={}".format(reverse('internships_masters', kwargs={'cohort_id': self.cohort.id}),
                                      organization.id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'masters.html')

        masters = response.context['allocations'].object_list
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
        master_test = MasterFactory(person__source=person_source_type.INTERNSHIP)

        # master and person exists before delete
        self.assertTrue(InternshipMaster.objects.filter(pk=master_test.pk).exists())
        self.assertTrue(Person.objects.filter(pk=master_test.person.pk).exists())

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

        # master and person have been deleted
        self.assertFalse(InternshipMaster.objects.filter(pk=master_test.pk).exists())
        self.assertFalse(Person.objects.filter(pk=master_test.person.pk).exists())

    def test_export_masters(self):
        url = reverse('master_export', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response['content-type'], CONTENT_TYPE_XLS.split(';')[0])

    def test_person_exists(self):
        person = PersonFactory(source=person_source_type.BASE)
        person_address = PersonAddressFactory(person=person)
        url = reverse('person_exists', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data=json.dumps({'email': person.email}), content_type='application/json')
        person_with_address_dict = {
            'birth_date': person.birth_date,
            'city': person_address.city,
            'country': person_address.country.pk,
            'email': person.email,
            'first_name': person.first_name,
            'gender': person.gender,
            'id': person.pk,
            'last_name': person.last_name,
            'location': person_address.location,
            'person': person.pk,
            'phone': person.phone,
            'postal_code': person_address.postal_code,
            'source': person.source,
        }
        response_dict = json.loads(response.content.decode('utf-8'))
        for key, value in person_with_address_dict.items():
            self.assertEqual(value, response_dict[key])

    def test_reload_master_form_with_existing_instance(self):
        person = PersonFactory(source=person_source_type.BASE)
        url = reverse('master_new', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={'existing-person-id': person.pk})
        self.assertTemplateUsed(response, 'master_form.html')
        self.assertEqual(response.context['person'], person)

    def test_save_master_form_with_existing_instance(self):
        person = PersonFactory(source=person_source_type.BASE)
        hospital = OrganizationFactory(cohort=self.cohort)
        specialty = SpecialtyFactory(cohort=self.cohort)
        url = reverse('master_save', kwargs={'cohort_id': self.cohort.pk})
        response = self.client.post(url, data={
            'existing-person-id': person.pk,
            'hospital': hospital.pk,
            'specialty': specialty.pk
        })
        self.assertRedirects(response, '{}?{}'.format(
            reverse('internships_masters', kwargs={'cohort_id': self.cohort.id}),
            '{}{}'.format('hospital=', hospital.pk)
        ))
        self.assertEqual(InternshipMaster.objects.first().person, person)
