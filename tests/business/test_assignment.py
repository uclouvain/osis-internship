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
import random
from datetime import timedelta
from pprint import pprint
from unittest import skip

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.utils import timezone

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from internship.business.assignment import difference, Assignment
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.period_internship_places import PeriodInternshipPlacesFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory


class AssignmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()

        self._create_mandatory_internships()
        self._create_non_mandatory_internships()
        self._create_internship_students()

        self.hospital_error = OrganizationFactory(cohort=self.cohort, reference=999)
        self.organizations = [OrganizationFactory(cohort=self.cohort) for _ in range(0, 10)]
        self.periods = [PeriodFactory(cohort=self.cohort) for _ in range(0, 8)]

        self.specialties = self.mandatory_specialties + self.non_mandatory_specialties
        self.internships = self.mandatory_internships + self.non_mandatory_internships

        self._create_internship_offers()
        self._declare_offer_places()
        self._make_student_choices()

    @skip('skip execution block')
    def test_algorithm_execution_blocked(self):
        self.cohort.publication_start_date = timezone.now() - timedelta(days=5)
        with self.assertLogs() as logger:
            self.assignment.solve()
            self.assertIn("blocked due to execution after publication date", str(logger.output))
            self.assertFalse(self.assignment.affectations)

    def test_algorithm_execution_all_periods_assigned(self):
        self.assignment = Assignment(self.cohort)
        self.assignment.TIMEOUT = 1
        self.assignment.solve()
        self.assignment.persist_solution()
        affectations = InternshipStudentAffectationStat.objects.all()
        for student in self.students:
            student_affectations = affectations.filter(student=student)
            self.assertEqual(len(student_affectations), len(self.periods)-1)

    def _make_student_choices(self):
        for student in self.students:
            for internship in self.internships:
                available_organizations = self.organizations.copy()
                specialty = internship.speciality or random.choice(self.non_mandatory_specialties)
                for choice in range(1, 5):
                    organization = random.choice(available_organizations)
                    available_organizations.remove(organization)
                    create_internship_choice(
                        organization=organization,
                        student=student,
                        internship=internship,
                        choice=choice,
                        speciality=specialty,
                    )

    def _declare_offer_places(self):
        self.places = []
        for offer in self.offers:
            for period in self.periods:
                self.places.append(PeriodInternshipPlacesFactory(period=period, internship_offer=offer))

    def _create_internship_offers(self):
        self.offers = []
        for organization in self.organizations:
            for specialty in self.specialties:
                self.offers.append(OfferFactory(cohort=self.cohort, organization=organization, speciality=specialty))

    def _create_internship_students(self):
        self.internship_students = [InternshipStudentInformationFactory(
            cohort=self.cohort,
            person=PersonFactory()
        ) for _ in range(0, 30)]
        self.students = [StudentFactory(person=student.person) for student in self.internship_students]

    def _create_non_mandatory_internships(self):
        self.non_mandatory_specialties = [SpecialtyFactory(mandatory=False) for _ in range(0, 20)]
        self.non_mandatory_internships = [
            InternshipFactory(
                cohort=self.cohort,
                name="Chosen internship {}".format(i + 1)
            )
            for i in range(0, 4)
        ]

    def _create_mandatory_internships(self):
        self.mandatory_specialties = [SpecialtyFactory(mandatory=True) for _ in range(0, 6)]
        self.mandatory_internships = [
            InternshipFactory(
                cohort=self.cohort,
                name=spec.name,
                speciality=spec
            )
            for spec in self.mandatory_specialties
        ]


class ListUtilsTestCase(TestCase):
    def test_difference_non_empty_lists(self):
        first_list = [1,2,3,4,5]
        second_list = [4,5]
        expected = [1,2,3]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_second_list(self):
        first_list = [1,2,3,4,5]
        second_list = []
        expected = [1,2,3,4,5]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_first_list(self):
        first_list = []
        second_list = [1,2]
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_lists(self):
        first_list = []
        second_list = []
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_list_without_common_elements(self):
        first_list = [1,2,3,4]
        second_list = [5,6]
        expected = [1,2,3,4]
        self.assertEqual(expected, difference(first_list, second_list))