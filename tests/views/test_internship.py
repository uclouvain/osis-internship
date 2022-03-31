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
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from base.tests.models import test_person, test_student
from internship.models import internship_choice as mdl_internship_choice
from internship.models import period_internship_places as mdl_period_places
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.models import test_internship_offer, test_internship_speciality, test_organization, test_period


class TestModifyStudentChoices(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("username", "test@test.com", "passtest",
                                            first_name='first_name', last_name='last_name')
        cls.user.save()
        add_permission(cls.user, "is_internship_manager")
        cls.person = test_person.create_person_with_user(cls.user)

        cls.cohort = CohortFactory()

        cls.student = test_student.create_student("first", "last", "64641200")

        cls.speciality_1 = test_internship_speciality.create_speciality(name="urgence", cohort=cls.cohort)
        cls.speciality_2 = test_internship_speciality.create_speciality(name="chirurgie", cohort=cls.cohort)

        cls.organization_1 = test_organization.create_organization(reference="01", cohort=cls.cohort)
        cls.organization_2 = test_organization.create_organization(reference="02", cohort=cls.cohort)
        cls.organization_3 = test_organization.create_organization(reference="03", cohort=cls.cohort)
        cls.organization_4 = test_organization.create_organization(reference="04", cohort=cls.cohort)
        cls.organization_5 = test_organization.create_organization(reference="05", cohort=cls.cohort)

        cls.offer_1 = test_internship_offer.create_specific_internship_offer(cls.organization_1, cls.speciality_1,
                                                                             cohort=cls.cohort)
        cls.offer_2 = test_internship_offer.create_specific_internship_offer(cls.organization_2, cls.speciality_1,
                                                                             cohort=cls.cohort)
        cls.offer_3 = test_internship_offer.create_specific_internship_offer(cls.organization_3, cls.speciality_1,
                                                                             cohort=cls.cohort)
        cls.offer_4 = test_internship_offer.create_specific_internship_offer(cls.organization_4, cls.speciality_1,
                                                                             cohort=cls.cohort)

        cls.offer_5 = test_internship_offer.create_specific_internship_offer(cls.organization_1, cls.speciality_2,
                                                                             cohort=cls.cohort)
        cls.offer_6 = test_internship_offer.create_specific_internship_offer(cls.organization_5, cls.speciality_2,
                                                                             cohort=cls.cohort)

    def setUp(self):
        self.client.force_login(self.user)

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
        internship = InternshipFactory(cohort=self.cohort)
        kwargs = {
            'cohort_id': self.cohort.id,
            'internship_id': internship.id,
            'speciality_id': self.speciality_2.id,
            'student_id': self.student.id
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
        self.assertEqual(choice.internship, internship)
        self.assertEqual(choice.choice, 1)
        self.assertTrue(choice.priority)

    def test_with_multiple_choice(self):
        internship = InternshipFactory(cohort=self.cohort)
        kwargs = {
            'cohort_id': self.cohort.id,
            'internship_id': internship.id,
            'speciality_id': self.speciality_1.id,
            'student_id': self.student.id
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
        internship = InternshipFactory(cohort=self.cohort)
        kwargs = {
            'cohort_id': self.cohort.id,
            'internship_id': internship.id,
            'speciality_id': self.speciality_1.id,
            'student_id': self.student.id
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
        internship = InternshipFactory(cohort=self.cohort)
        previous_choice = create_internship_choice(test_organization.create_organization(),
                                                   self.student, self.speciality_1, internship)
        kwargs = {
            'cohort_id': self.cohort.id,
            'internship_id': internship.id,
            'speciality_id': self.speciality_2.id,
            'student_id': self.student.id
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

        self.cohort = CohortFactory()

        self.speciality = test_internship_speciality.create_speciality(name="urgence", cohort=self.cohort)
        self.organization = test_organization.create_organization(reference="01", cohort=self.cohort)
        self.offer = test_internship_offer.create_specific_internship_offer(self.organization, self.speciality,
            cohort=self.cohort)

        MAX_PERIOD = 12
        for period in range(1, MAX_PERIOD + 1):
            test_period.create_period("P%d" % period, cohort=self.cohort)

        self.internship_offer = OfferFactory(cohort=self.cohort)

        self.client.force_login(self.user)

    def testAccessUrl(self):
        kwargs = {
            'internship_id': self.internship_offer.id,
            'cohort_id': self.cohort.id,
        }
        url = reverse("edit_period_places", kwargs=kwargs)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_save_period_places(self):
        PeriodFactory(name="P1", cohort=self.cohort)
        PeriodFactory(name="P5", cohort=self.cohort)

        kwargs = {
            'internship_id': self.internship_offer.id,
            'cohort_id': self.cohort.id,
        }

        url = reverse("save_period_places", kwargs=kwargs)

        self.client.post(url, data={
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
