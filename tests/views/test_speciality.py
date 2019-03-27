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
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from internship.models.internship_speciality import InternshipSpeciality
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.views import speciality as view_speciality



class SpecialityViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.cohort = CohortFactory()

    def test_home(self):
        url = reverse('internships_specialities', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'specialities.html')

    def test_create(self):
        url = reverse('speciality_create', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speciality_form.html')

    def test_delete(self):
        specialities = InternshipSpeciality.objects.filter(cohort=self.cohort).count()
        self.assertEqual(specialities, 0)

        speciality = SpecialtyFactory(cohort=self.cohort)

        specialities = InternshipSpeciality.objects.filter(cohort=self.cohort).count()
        self.assertEqual(specialities, 1)

        url = reverse('speciality_delete', kwargs={
            'cohort_id': self.cohort.id,
            'speciality_id': speciality.id
        })

        response = self.client.get(url)

        specialities = InternshipSpeciality.objects.filter(cohort=self.cohort).count()
        self.assertEqual(specialities, 0)

        self.assertRedirects(response, reverse('internships_specialities', kwargs={
            'cohort_id': self.cohort.id,
        }))

    def test_modification(self):
        speciality = SpecialtyFactory(cohort=self.cohort)

        url = reverse('speciality_modification', kwargs={
            'cohort_id': self.cohort.id,
            'speciality_id': speciality.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speciality_form.html')
        self.assertEqual(response.context['speciality'], speciality)

    def test_new(self):
        speciality = SpecialtyFactory()

        url = reverse('speciality_new', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.post(url, data={
            'mandatory': True,
            'name': speciality.name,
            'acronym': speciality.acronym,
            'sequence': ""
        })

        self.assertRedirects(response, reverse('internships_specialities', kwargs={
            'cohort_id': self.cohort.id,
        }))

    def test_save_unique_specialty(self):
        url = reverse('speciality_save', kwargs={
            'cohort_id': self.cohort.id,
            'speciality_id': 1,
        })

        specialty = {
            'mandatory': False,
            'name': "TEST",
            'acronym': "TE",
            'sequence': "1"
        }

        response = self.client.post(url, data=specialty)

        self.assertRedirects(response, reverse('internships_specialities', kwargs={'cohort_id': self.cohort.id,}))

        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].level_tag, "success")
        self.assertIn(specialty['name'], messages[0].message)

    def test_save_with_duplicate_acronym(self):
        first_specialty = SpecialtyFactory(name='TEST', acronym='TE1', cohort=self.cohort)
        second_specialty = SpecialtyFactory(name='TEST-1', acronym='TE2', cohort=self.cohort)

        url = reverse('speciality_save', kwargs={
            'cohort_id': self.cohort.id,
            'speciality_id': second_specialty.id,
        })

        specialty_with_same_acronym = {
            'mandatory': False,
            'name': "TEST-2",
            'acronym': first_specialty.acronym,
            'sequence': "1"
        }

        response = self.client.post(url, data=specialty_with_same_acronym)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speciality_form.html')

        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].level_tag, "error")
        self.assertIn(first_specialty.acronym, messages[0].message)
