##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase

from base.tests.models import test_person, test_student
from internship.models import internship_choice as mdl_internship_choice
from internship.models import period_internship_places as mdl_period_places
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialityFactory
from internship.tests.models import (test_internship_choice,
                                     test_internship_offer,
                                     test_internship_speciality,
                                     test_organization, test_period)
from internship.tests.factories.cohort import CohortFactory


class TestModifyStudentChoices(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("username", "test@test.com", "passtest",
                                             first_name='first_name', last_name='last_name')
        self.user.save()
        add_permission(self.user, "is_internship_manager")
        self.person = test_person.create_person_with_user(self.user)
        self.client.force_login(self.user)

        self.student = test_student.create_student("first", "last", "64641200")

        self.speciality_1 = test_internship_speciality.create_speciality(name="urgence")
        self.speciality_2 = test_internship_speciality.create_speciality(name="chirurgie")

        self.organization_1 = test_organization.create_organization(reference="01")
        self.organization_2 = test_organization.create_organization(reference="02")
        self.organization_3 = test_organization.create_organization(reference="03")
        self.organization_4 = test_organization.create_organization(reference="04")
        self.organization_5 = test_organization.create_organization(reference="05")

        self.offer_1 = test_internship_offer.create_specific_internship_offer(self.organization_1, self.speciality_1)
        self.offer_2 = test_internship_offer.create_specific_internship_offer(self.organization_2, self.speciality_1)
        self.offer_3 = test_internship_offer.create_specific_internship_offer(self.organization_3, self.speciality_1)
        self.offer_4 = test_internship_offer.create_specific_internship_offer(self.organization_4, self.speciality_1)

        self.offer_5 = test_internship_offer.create_specific_internship_offer(self.organization_1, self.speciality_2)
        self.offer_6 = test_internship_offer.create_specific_internship_offer(self.organization_5, self.speciality_2)

    @classmethod
    def generate_form(cls, iterable):
        form = {}
        for idx, item in enumerate(iterable):
            offer, preference, priority = item
            values = {
                'form-%d-offer' % idx: str(offer.id),
                'form-%d-preference' % idx: str(preference),
                'form-%d-priority' % idx: 'on' if priority else 'off',
            }
            form.update(values)

        counter_str = str(idx + 1)
        form.update({
            'form-TOTAL_FORMS': counter_str,
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': counter_str,
            'form-MAX_NUM_FORMS': counter_str,
        })

        return form

    def test_with_one_choice(self):
        kwargs = {
            'internship_id': 1,
            'speciality_id': self.speciality_2.id,
            'registration_id': self.student.registration_id
        }
        selection_url = reverse("specific_internship_student_modification", kwargs=kwargs)

        data = self.generate_form([
            (self.offer_5, 1, True),
            (self.offer_6, 0, False)
        ])

        response = self.client.post(selection_url, data=data)
        self.assertEqual(response.status_code, 200)

        qs = mdl_internship_choice.search_by_student_or_choice(student=self.student)
        self.assertEqual(qs.count(), 1)

        choice = qs.first()
        self.assertEqual(choice.organization, self.organization_1)
        self.assertEqual(choice.speciality, self.speciality_2)
        self.assertEqual(choice.internship_choice, 1)
        self.assertEqual(choice.choice, 1)
        self.assertTrue(choice.priority)

    def test_with_multiple_choice(self):
        kwargs = {
            'internship_id': 1,
            'speciality_id': self.speciality_1.id,
            'registration_id': self.student.registration_id
        }
        selection_url = reverse("specific_internship_student_modification", kwargs=kwargs)

        data = self.generate_form([
            (self.offer_1, 1, False),
            (self.offer_2, 2, False),
            (self.offer_3, 3, False),
            (self.offer_4, 4, False),
        ])

        response = self.client.post(selection_url, data=data)
        self.assertEqual(response.status_code, 200)

        qs = mdl_internship_choice.search_by_student_or_choice(student=self.student)
        self.assertEqual(qs.count(), 4)

        data = self.generate_form([
            (self.offer_1, 1, False),
            (self.offer_2, 0, False),
            (self.offer_3, 2, False),
            (self.offer_4, 0, False),
        ])

        self.client.post(selection_url, data=data)

        qs = mdl_internship_choice.search_by_student_or_choice(student=self.student)
        self.assertEqual(qs.count(), 2)

    def test_with_incorrect_speciality(self):
        kwargs = {
            'internship_id': 1,
            'speciality_id': self.speciality_1.id,
            'registration_id': self.student.registration_id
        }
        selection_url = reverse("specific_internship_student_modification", kwargs=kwargs)

        data = self.generate_form([
            (self.offer_1, 1, True),
            (self.offer_5, 2, True),
            (self.offer_3, 0, True),
            (self.offer_4, 0, True),
        ])

        response = self.client.post(selection_url, data=data)
        self.assertEqual(response.status_code, 200)

        qs = mdl_internship_choice.search_by_student_or_choice(student=self.student)
        self.assertEqual(qs.count(), 1)

    def test_replace_previous_choices(self):
        previous_choice = test_internship_choice.create_internship_choice(test_organization.create_organization(),
                                                                          self.student, self.speciality_1, 2)
        kwargs = {
            'internship_id': 2,
            'speciality_id': self.speciality_2.id,
            'registration_id': self.student.registration_id
        }
        selection_url = reverse("specific_internship_student_modification", kwargs=kwargs)

        data = self.generate_form([
            (self.offer_5, 1, True),
            (self.offer_6, 0, False),
        ])

        response = self.client.post(selection_url, data=data)
        self.assertEqual(response.status_code, 200)

        qs = mdl_internship_choice.search_by_student_or_choice(student=self.student)

        self.assertEqual(qs.count(), 1)
        self.assertNotEqual(previous_choice, qs.first())


class TestModifyPeriods(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("username", "test@test.com", "passtest",
                                             first_name='first_name', last_name='last_name')
        self.user.save()
        add_permission(self.user, "is_internship_manager")
        self.person = test_person.create_person_with_user(self.user)

        self.client.force_login(self.user)

        self.speciality = test_internship_speciality.create_speciality(name="urgence")
        self.organization = test_organization.create_organization(reference="01")
        self.offer = test_internship_offer.create_specific_internship_offer(self.organization, self.speciality)

        MAX_PERIOD = 12
        for period in range(1, MAX_PERIOD + 1):
            test_period.create_period("P%d" % period)

    def testAccessUrl(self):
        cohort = CohortFactory()

        organization = OrganizationFactory(cohort=cohort)
        speciality = SpecialityFactory(cohort=cohort)
        offer = OfferFactory(organization=organization, speciality=speciality)

        kwargs = {
            'internship_id': offer.id,
            'cohort_id': cohort.id,
        }
        url = reverse("edit_period_places", kwargs=kwargs)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_save_period_places(self):
        cohort = CohortFactory()

        organization = OrganizationFactory(cohort=cohort)
        speciality = SpecialityFactory(cohort=cohort)
        offer = OfferFactory(organization=organization, speciality=speciality)

        kwargs = {
            'internship_id': offer.id,
            'cohort_id': cohort.id,
        }

        url = reverse("save_period_places",  kwargs=kwargs)

        response = self.client.post(url, data={
            "P1": 2,
            "P5": 8,
        })

        number_of_period_places = mdl_period_places.PeriodInternshipPlaces.objects.count()
        self.assertEqual(number_of_period_places, 2)


def add_permission(user, codename):
    perm = get_permission(codename)
    user.user_permissions.add(perm)


def get_permission(codename):
    return Permission.objects.get(codename=codename)
