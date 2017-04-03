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

    def test_save(self):
        url = reverse('internships_save', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.post(url)
        self.assertRedirects(response, reverse('internships_stud', kwargs={
            'cohort_id': self.cohort.id,
        }))

    @unittest.skip("Refactor the code of the tested view")
    def test_save_modification_student(self):
        url = reverse('internship_save_modification_student', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.post(url, data={'registration_id': 0})
        self.assertRedirects(response, reverse('internships_modification_student', args=[0]))

    def test_internships_stud(self):
        url = reverse('internships_stud', kwargs={
            'cohort_id': self.cohort.id,
        })

        response = self.client.get(url)
        self.assertTemplateUsed(response, 'internships_stud.html')