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
from datetime import timedelta
from unittest import skip

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.utils import timezone

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from internship.business.assignment import difference, Assignment
from internship.business.statistics import load_solution_sol, compute_stats
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_enrollment import InternshipEnrollment
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.factories.internship_enrollment import InternshipEnrollmentFactory
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.period_internship_places import PeriodInternshipPlacesFactory
from internship.tests.factories.speciality import SpecialtyFactory

N_STUDENTS = 30
N_MANDATORY_INTERNSHIPS = 6
N_NON_MANDATORY_INTERNSHIPS = 20
N_ORGANIZATIONS = 10
N_PERIODS = 8


class AssignmentTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()

        cls.mandatory_internships, cls.mandatory_specialties = _create_mandatory_internships(cls)
        cls.non_mandatory_internships, cls.non_mandatory_specialties = _create_non_mandatory_internships(cls)
        cls.students = _create_internship_students(cls)

        cls.hospital_error = OrganizationFactory(name='Hospital Error', cohort=cls.cohort, reference=999)
        cls.organizations = [OrganizationFactory(cohort=cls.cohort) for _ in range(0, N_ORGANIZATIONS)]
        cls.periods = [PeriodFactory(cohort=cls.cohort) for _ in range(0, N_PERIODS)]

        cls.specialties = cls.mandatory_specialties + cls.non_mandatory_specialties
        cls.internships = cls.mandatory_internships + cls.non_mandatory_internships

        cls.offers = _create_internship_offers(cls)
        cls.places = _declare_offer_places(cls)
        _make_student_choices(cls)

        cls.prior_student = _block_prior_student_choices(cls)

        cls.internship_with_offer_shortage, cls.unlucky_student = _make_shortage_scenario(cls)

        _execute_assignment_algorithm(cls)
        cls.affectations = InternshipStudentAffectationStat.objects.all()

    def test_algorithm_execution_all_periods_assigned(self):
        for student in self.students:
            student_affectations = self.affectations.filter(student=student)
            self.assertEqual(len(student_affectations), len(self.periods)-1)

    @skip('skip force hospital error test')
    def test_force_hospital_error_assignment(self):
        unlucky_student_affectation = self.affectations.get(
            student=self.unlucky_student,
            internship=self.internship_with_offer_shortage
        )
        self.assertEqual(unlucky_student_affectation.organization, self.hospital_error)

    def test_prior_student_choices_with_blocked_periods_respected(self):
        prior_student_affectations = self.affectations.filter(student=self.prior_student)
        prior_enrollments = InternshipEnrollment.objects.filter(student=self.prior_student)
        for affectation in prior_student_affectations:
            prior_enrollment = prior_enrollments.get(internship=affectation.internship)
            self.assertEqual(affectation.organization, prior_enrollment.place)
            self.assertEqual(affectation.period, prior_enrollment.period)
            self.assertEqual(affectation.speciality, prior_enrollment.internship_offer.speciality)

    def test_prior_student_choices_with_unblocked_periods_respected(self):
        prior_student_affectations = self.affectations.filter(student=self.prior_student)
        prior_enrollments = InternshipEnrollment.objects.filter(student=self.prior_student)
        for affectation in prior_student_affectations:
            prior_enrollment = prior_enrollments.get(internship=affectation.internship)
            self.assertEqual(affectation.organization, prior_enrollment.place)
            self.assertEqual(affectation.period, prior_enrollment.period)
            self.assertEqual(affectation.speciality, prior_enrollment.internship_offer.speciality)

    def test_affectation_statistics(self):
        solution = load_solution_sol(self.cohort, self.affectations)
        stats = compute_stats(self.cohort, solution)
        self.assertEqual(stats['tot_stud'], N_STUDENTS)
        self.assertEqual(stats['erasmus_students'], 1)


def _make_student_choices(cls):
    for student in cls.students:
        for internship in cls.internships:
            available_organizations = cls.organizations.copy()
            specialty = internship.speciality or random.choice(cls.non_mandatory_specialties)
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


def _block_prior_student_choices(cls):
    prior_student = random.choice(cls.students)
    prior_internships = cls.mandatory_internships + [cls.non_mandatory_internships[0]]
    student_choices = InternshipChoice.objects.filter(
        student=prior_student,
        choice=1,
        internship__in=prior_internships
    )
    for index, choice in enumerate(student_choices):
        InternshipEnrollmentFactory(
            student=prior_student,
            place=choice.organization,
            internship=choice.internship,
            period=cls.periods[index]
        )
    return prior_student


def _declare_offer_places(cls):
    places = []
    for offer in cls.offers:
        for period in cls.periods:
            places.append(PeriodInternshipPlacesFactory(period=period, internship_offer=offer))
    return places


def _create_internship_offers(cls):
    offers = []
    cls.organizations.append(cls.hospital_error)
    for specialty in cls.specialties:
        for organization in cls.organizations:
            offers.append(OfferFactory(cohort=cls.cohort, organization=organization, speciality=specialty))
    cls.organizations.remove(cls.hospital_error)
    return offers


def _create_internship_students(cls):
    internship_students = [InternshipStudentInformationFactory(
        cohort=cls.cohort,
        person=PersonFactory()
    ) for _ in range(0, N_STUDENTS)]
    students = [StudentFactory(person=student.person) for student in internship_students]
    return students


def _create_mandatory_internships(cls):
    mandatory_specialties = [SpecialtyFactory(mandatory=True) for _ in range(0, N_MANDATORY_INTERNSHIPS)]
    mandatory_internships = [
        InternshipFactory(
            cohort=cls.cohort,
            name=spec.name,
            speciality=spec
        )
        for spec in mandatory_specialties
    ]
    return mandatory_internships, mandatory_specialties


def _create_non_mandatory_internships(cls):
    non_mandatory_specialties = [SpecialtyFactory(mandatory=False) for _ in range(0, N_NON_MANDATORY_INTERNSHIPS)]
    non_mandatory_internships = [
        InternshipFactory(
            cohort=cls.cohort,
            name="Chosen internship {}".format(i + 1)
        )
        for i in range(0, 4)
    ]
    return non_mandatory_internships, non_mandatory_specialties


def _make_shortage_scenario(cls):
    '''Make scenario for internship offer with not enough places for student'''
    cls.organizations.append(cls.hospital_error)
    specialty_with_offer_shortage = SpecialtyFactory(mandatory=True, cohort=cls.cohort)
    internship_with_offer_shortage = InternshipFactory(
        cohort=cls.cohort,
        name=specialty_with_offer_shortage.name,
        speciality=specialty_with_offer_shortage,
        position=-1
    )
    for organization in cls.organizations:
        number_places = 999 if organization is cls.hospital_error else 0
        shortage_offer = OfferFactory(
            cohort=cls.cohort,
            organization=organization,
            speciality=specialty_with_offer_shortage
        )
        for period in cls.periods:
            PeriodInternshipPlacesFactory(
                period=period,
                internship_offer=shortage_offer,
                number_places=number_places
            )
    cls.organizations.remove(cls.hospital_error)
    unlucky_student = random.choice(cls.students)
    available_organizations = cls.organizations.copy()
    for choice in range(1, 5):
        organization = random.choice(available_organizations)
        available_organizations.remove(organization)
        create_internship_choice(
            organization=organization,
            student=unlucky_student,
            internship=internship_with_offer_shortage,
            choice=choice,
            speciality=specialty_with_offer_shortage,
        )
    return internship_with_offer_shortage, unlucky_student


def _execute_assignment_algorithm(cls):
    assignment = Assignment(cls.cohort)
    assignment.TIMEOUT = 1
    assignment.solve()
    assignment.persist_solution()


class ListUtilsTestCase(TestCase):
    def test_difference_non_empty_lists(self):
        first_list = [1, 2, 3, 4, 5]
        second_list = [4, 5]
        expected = [1, 2, 3]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_second_list(self):
        first_list = [1, 2, 3, 4, 5]
        second_list = []
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_first_list(self):
        first_list = []
        second_list = [1, 2]
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_lists(self):
        first_list = []
        second_list = []
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_list_without_common_elements(self):
        first_list = [1, 2, 3, 4]
        second_list = [5, 6]
        expected = [1, 2, 3, 4]
        self.assertEqual(expected, difference(first_list, second_list))


class AlgorithmExecutionBlockedTest(TestCase):
    def setUp(self):
        self.cohort = CohortFactory()
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.assignment = Assignment(cohort=self.cohort)

    @skip('skip execution block')
    def test_algorithm_execution_blocked(self):
        self.cohort.publication_start_date = timezone.now() - timedelta(days=5)
        with self.assertLogs() as logger:
            self.assignment.solve()
            self.assertIn("blocked due to execution after publication date", str(logger.output))
            self.assertFalse(self.assignment.affectations)
