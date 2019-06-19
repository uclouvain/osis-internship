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
import random

from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase

from base.tests.factories.student import StudentFactory
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory

CHOICES = [1, 2, 3, 4]

class OfferViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()
        self.organization = OrganizationFactory(cohort=self.cohort)
        self.specialty = SpecialtyFactory(mandatory=True, cohort=self.cohort)
        self.offer = OfferFactory(cohort=self.cohort, organization=self.organization,  speciality=self.specialty)
        students = [StudentFactory() for _ in range(0, 4)]
        mandatory_internship = InternshipFactory(cohort=self.cohort, speciality=self.specialty)
        non_mandatory_internship = InternshipFactory(cohort=self.cohort)

        for internship in [mandatory_internship, non_mandatory_internship]:
            for choice in CHOICES:
                create_internship_choice(
                    organization=self.organization,
                    student=students[0],
                    speciality=self.specialty,
                    choice=choice,
                    internship=internship
                )
        for student in students[1:]:
            create_internship_choice(
                organization=self.organization,
                student=student,
                speciality=self.specialty,
                choice=random.choice([2, 3, 4]),
                internship=mandatory_internship
            )

    def test_home(self):
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'internships.html')

    def test_home_with_organization_filter(self):
        organization = OrganizationFactory(cohort=self.cohort)
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
        })
        get_params = '?organization_sort={}'.format(organization.name)
        response = self.client.get(url+get_params)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'internships.html')

    def test_home_with_specialty_filter(self):
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
        })
        get_params = '?speciality_sort={}'.format(self.specialty.name)
        response = self.client.get(url+get_params)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'internships.html')

    def test_home_with_both_filters(self):
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
        })
        get_params = '?speciality_sort={}&organization_sort={}'.format(self.specialty.name, self.organization.name)
        response = self.client.get(url+get_params)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'internships.html')

    def test_home_with_offer(self):
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
            'specialty_id': self.specialty.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'internships.html')

    def test_internship_detail_student_choice(self):
        url = reverse('internship_detail_student_choice', kwargs={
            'cohort_id': self.cohort.id,
            'offer_id': self.offer.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'internship_detail.html')

        self.assertEqual(response.context['internship'], self.offer)


class OfferChoiceDistributionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()
        students = [StudentFactory() for _ in range(0, 4)]
        self.specialty = SpecialtyFactory(mandatory=1, cohort=self.cohort)
        mandatory_internship = InternshipFactory(cohort=self.cohort, speciality=self.specialty)
        non_mandatory_internship = InternshipFactory(cohort=self.cohort)
        organization = OrganizationFactory(cohort=self.cohort)
        OfferFactory(
            cohort=self.cohort,
            organization=organization,
            speciality=self.specialty
        )
        for internship in [mandatory_internship, non_mandatory_internship]:
            for choice in CHOICES:
                create_internship_choice(
                    organization=organization,
                    student=students[0],
                    speciality=self.specialty,
                    choice=choice,
                    internship=internship
                )
        for student in students[1:]:
            create_internship_choice(
                organization=organization,
                student=student,
                speciality=self.specialty,
                choice=random.choice([2, 3, 4]),
                internship=mandatory_internship
            )

    def test_count_number_first_choices(self):
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
            'specialty_id': self.specialty.id
        })
        response = self.client.get(url)
        self.assertEqual(response.context['all_internships'][0].number_first_choice, 2)
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_count_number_other_choices(self):
        url = reverse('internships', kwargs={
            'cohort_id': self.cohort.id,
            'specialty_id': self.specialty.id
        })
        response = self.client.get(url)
        self.assertEqual(response.context['all_internships'][0].number_other_choice, 9)
        self.assertEqual(response.status_code, HttpResponse.status_code)