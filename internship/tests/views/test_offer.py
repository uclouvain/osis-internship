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
import unittest

from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialityFactory


class OfferViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.cohort = CohortFactory()

    def test_home(self):
        # FIXME: specify organization_sort and speciality_sort
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internships.html')

    def test_home_with_offer(self):
        organization = OrganizationFactory(cohort=self.cohort)
        speciality = SpecialityFactory(cohort=self.cohort)

        offer = OfferFactory(organization=organization, speciality=speciality)

        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internships.html')

    def test_internship_detail_student_choice(self):
        offer = OfferFactory(organization=OrganizationFactory(cohort=self.cohort))

        url = reverse('internship_detail_student_choice', kwargs={
            'cohort_id': self.cohort.id,
            'offer_id': offer.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_detail.html')

        self.assertEqual(response.context['internship'], offer)

    def test_block(self):
        url = reverse('internships_block', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.get(url)
        self.assertRedirects(response, reverse('internships_home', kwargs={
            'cohort_id': self.cohort.id,
        }))

    @unittest.skip("Refactor the code of the tested view")
    def test_save_modification_student(self):
        url = reverse('internship_save_modification_student', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.post(url, data={'registration_id': 0})
        self.assertRedirects(response, reverse('internships_modification_student', args=[0]))
