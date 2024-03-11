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

from base.models.student import Student
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from internship.business.assignment import difference, Assignment, _permute_affectations
from internship.business.statistics import load_solution_sol, compute_stats
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_enrollment import InternshipEnrollment
from internship.models.internship_modality_period import InternshipModalityPeriod
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.period import Period, get_effective_periods
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
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory

N_STUDENTS = 30
N_MANDATORY_INTERNSHIPS = 6
N_NON_MANDATORY_INTERNSHIPS = 20
N_ORGANIZATIONS = 10
N_PERIODS = 8


class AssignmentTest(TestCase):
    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.periods = [PeriodFactory(name=f"P{_}", cohort=cls.cohort) for _ in range(1, N_PERIODS)]

        cls.mandatory_internships, cls.mandatory_specialties = _create_mandatory_internships(cls)
        cls.non_mandatory_internships, cls.non_mandatory_specialties = _create_non_mandatory_internships(cls)
        cls.students = _create_internship_students(cls)

        cls.hospital_error = OrganizationFactory(name='Hospital Error', cohort=cls.cohort, reference=999)
        cls.organizations = [OrganizationFactory(cohort=cls.cohort) for _ in range(0, N_ORGANIZATIONS)]
        cls.remedial_period = PeriodFactory(name='PR1', cohort=cls.cohort, remedial=True)

        cls.specialties = cls.mandatory_specialties + cls.non_mandatory_specialties
        cls.internships = cls.mandatory_internships + cls.non_mandatory_internships

        cls.offers = _create_internship_offers(cls)
        cls.places = _declare_offer_places(cls)
        _make_student_choices(cls)

        cls.prior_student = _block_prior_student_choices(cls)
        cls.prior_non_mandatory_student = _block_prior_student_choice_non_mandatory(cls)

        # force Stages au choix in first period
        for sc_internship in cls.non_mandatory_internships:
            p1 = Period.objects.get(name='P1')
            InternshipModalityPeriod(internship=sc_internship, period=p1).save()

        _execute_assignment_algorithm(cls.cohort)
        cls.affectations = InternshipStudentAffectationStat.objects.all()

        cls.prior_student_affectations = cls.affectations.filter(student=cls.prior_student)
        cls.prior_enrollments = InternshipEnrollment.objects.filter(student=cls.prior_student)

        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

    @skip('print algorithm execution results')
    def test_algorithm_execution_print_results(self):
        affectations = InternshipStudentAffectationStat.objects.all()
        for student in Student.objects.all():
            if student in [self.prior_student, self.prior_non_mandatory_student]:
                print('PRIOR STUDENT')
            for aff in affectations.filter(student=student).order_by('period__name'):
                print(aff.student, aff.internship, aff.period, aff.organization, aff.period.cohort)
            print('--')

    def test_algorithm_execution_all_periods_assigned(self):
        for student in [student for student in self.students if student != self.prior_student]:
            student_affectations = self.affectations.filter(student=student)
            self.assertEqual(len(student_affectations), len(self.periods))

    def test_algorithm_discard_remedial_periods(self):
        for student in self.students:
            student_affectations = self.affectations.filter(student=student, period=self.remedial_period)
            self.assertFalse(student_affectations)

    @skip('skip force hospital error test')
    def test_force_hospital_error_assignment(self):
        self.internship_with_offer_shortage, self.unlucky_student = _make_shortage_scenario(self)
        unlucky_student_affectation = self.affectations.get(
            student=self.unlucky_student,
            internship=self.internship_with_offer_shortage
        )
        self.assertEqual(unlucky_student_affectation.organization, self.hospital_error)

    def test_prior_student_choices_with_periods_respected(self):
        for affectation in self.prior_student_affectations:
            prior_enrollment = self.prior_enrollments.get(internship=affectation.internship)
            self.assertEqual(affectation.organization, prior_enrollment.place)
            self.assertEqual(affectation.period, prior_enrollment.period)
            self.assertEqual(affectation.speciality, prior_enrollment.internship_offer.speciality)

    def test_affectation_statistics(self):
        solution = load_solution_sol(self.cohort, self.affectations)
        stats = compute_stats(self.cohort, solution)
        self.assertEqual(stats['tot_stud'], N_STUDENTS)
        self.assertEqual(stats['erasmus_students'], 2)

    def test_should_constraint_mandatory_internship_to_defined_periods_if_any(self):
        for student in [student for student in self.students if student != self.prior_student]:
            student_affectations = self.affectations.filter(student=student)
            for aff in student_affectations:
                aff_constraint_periods = aff.internship.internshipmodalityperiod_set.all().values_list(
                    'period__name', flat=True
                )
                if aff_constraint_periods:
                    self.assertTrue(aff.period.name in aff_constraint_periods)

    def test_one_non_mandatory_internship_by_student(self):
        affectations = InternshipStudentAffectationStat.objects.all()
        for student in Student.objects.all():
            self.assertTrue(
                len([aff for aff in affectations.filter(student=student) if aff.internship.speciality is None]) == 1
            )


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
    prior_student = cls.students[0]
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


def _block_prior_student_choice_non_mandatory(cls):
    # force non mandatory internship on first period
    prior_student = cls.students[1]

    non_mandatory = cls.non_mandatory_internships[0]
    student_choice = InternshipChoice.objects.get(student=prior_student, choice=1, internship=non_mandatory)
    InternshipEnrollmentFactory(
        student=prior_student,
        place=student_choice.organization,
        internship=student_choice.internship,
        period=cls.periods[0]
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
    # add a period constraint on specialty-0
    for period in [period for period in cls.periods if period.name in ['P6', 'P7']]:
        InternshipModalityPeriod(internship=mandatory_internships[0], period=period).save()
    return mandatory_internships, mandatory_specialties


def _create_non_mandatory_internships(cls):
    non_mandatory_specialties = [
        SpecialtyFactory(name=f"chosen-speciality-{_}", mandatory=False) for _ in range(0, N_NON_MANDATORY_INTERNSHIPS)
    ]
    non_mandatory_internships = [
        InternshipFactory(
            cohort=cls.cohort,
            name=f"chosenint_{i+1}"
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


def _execute_assignment_algorithm(cohort):
    assignment = Assignment(cohort)
    assignment.TIMEOUT = 1
    assignment.solve()
    assignment.persist_solution()


class BalancingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.organizations = [OrganizationFactory(cohort=cls.cohort) for _ in range(0, N_ORGANIZATIONS)]
        cls.last_switch = []

    def test_permute_exchanged_affectation_information(self):
        specialty = SpecialtyFactory()
        period = PeriodFactory()
        internship = InternshipFactory(speciality=specialty)
        defavored_affectation = StudentAffectationStatFactory(
            speciality=specialty,
            organization=self.organizations[-1],
            period=period,
            internship=internship,
            cost=10,
            choice="I"
        )
        favored_affectation = StudentAffectationStatFactory(
            speciality=specialty,
            organization=self.organizations[1],
            period=period,
            internship=internship,
            cost=0
        )
        self.affectations = InternshipStudentAffectationStat.objects.all()
        for choice, organization in enumerate(self.organizations[:4], start=1):
            create_internship_choice(
                organization=organization,
                student=defavored_affectation.student,
                internship=internship,
                choice=choice,
                speciality=specialty,
            )
        _permute_affectations(self, [defavored_affectation], [favored_affectation], InternshipChoice.objects.all())
        InternshipStudentAffectationStat.objects.bulk_update(self.affectations, fields=['organization'])
        self.assertEqual(
            self.affectations.get(student=defavored_affectation.student).organization, self.organizations[1]
        )
        self.assertEqual(
            self.affectations.get(student=favored_affectation.student).organization, self.organizations[-1]
        )


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


class AlgorithmExecutionOnCohortSiblingsTest(TestCase):
    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def setUpTestData(cls):

        cls.parent_cohort = CohortFactory(
            name='parent', is_parent=True,
            publication_start_date=None, subscription_start_date=None, subscription_end_date=None
        )

        cls.cohorts = [CohortFactory(name=name, parent_cohort=cls.parent_cohort) for name in ['m1', 'm2', 'm3']]
        periods_names = {'m1': ["P1", "P2"], 'm2': ["P3", "P4"], 'm3': ["P5", "P6", "P7", "P8", "P9"]}
        specialties_names = {
            'm1': ["Urgence", "Geriatrie", "Anesthésie", "Gynécologie"],
            'm2': ["Chirurgie", "Urgence", "Geriatrie", "Pédiatrie", "Gynécologie", "Médecine Interne"],
            'm3': [
                "Chirurgie", "Urgence", "Geriatrie", "Anesthésie",
                "Medecine Générale", "Gynécologie", "Médecine Interne"
            ],
        }

        all_specialties = {specialty for specialties_list in specialties_names.values() for specialty in
                           specialties_list}

        students = [StudentFactory(person=PersonFactory()) for _ in range(0, N_STUDENTS)]

        non_mandatory_specialties_names = ["Chirurgie plastique", "Médecine Nucléaire", "Neurologie", "Radiologie"]

        for name in non_mandatory_specialties_names:
            all_specialties.add(name)

        for cohort in cls.cohorts:
            mandatory_specialties = [
                SpecialtyFactory(name=_, cohort=cohort, mandatory=True) for _ in specialties_names[cohort.name]
            ]
            non_mandatory_specialties = [
                SpecialtyFactory(name=_, cohort=cohort, mandatory=False) for _ in non_mandatory_specialties_names
            ]
            periods = [PeriodFactory(name=_, cohort=cohort) for _ in periods_names[cohort.name]]
            mandatory_internships = [
                InternshipFactory(cohort=cohort, name=spec.name, speciality=spec) for spec in mandatory_specialties
            ]

            non_mandatory_internship = InternshipFactory(cohort=cohort, name="Stage au choix")

            students_info = [
                InternshipStudentInformationFactory(cohort=cohort, person=student.person) for student in students
            ]

            hospital_error = OrganizationFactory(name='Hospital Error', cohort=cohort, reference=999)
            organizations = [OrganizationFactory(cohort=cohort) for _ in range(0, 5)]

            offers = [
                OfferFactory(cohort=cohort, organization=organization, speciality=specialty)
                for specialty in mandatory_specialties + non_mandatory_specialties for organization in organizations
            ]

            # ensure enough places

            places = [
                PeriodInternshipPlacesFactory(period=period, internship_offer=offer, number_places=len(students))
                for period in periods for offer in offers
            ]

            all_specialties = InternshipSpeciality.objects.filter(name__in=list(all_specialties))

            error_offers = [
                OfferFactory(cohort=cohort, organization=hospital_error, speciality=specialty)
                for specialty in all_specialties
            ]
            hospital_error_places = [
                PeriodInternshipPlacesFactory(period=period, internship_offer=offer, number_places=len(students))
                for period in periods for offer in error_offers
            ]

            for student in students:
                for internship in mandatory_internships:
                    for choice in range(1, 5):
                        organization = random.choice(organizations)
                        create_internship_choice(
                            organization=organization,
                            student=student,
                            internship=internship,
                            choice=choice,
                            speciality=internship.speciality,
                        )
                create_internship_choice(
                    organization=random.choice(organizations),
                    student=student,
                    internship=non_mandatory_internship,
                    choice=1,
                    speciality=random.choice(non_mandatory_specialties),
                )

        # force Medecine Generale only in P8
        mg_internship = next(
            internship for internship in mandatory_internships if internship.speciality.name == "Medecine Générale"
        )
        m3_p8 = Period.objects.get(cohort__name='m3', name='P8')
        m3_p7 = Period.objects.get(cohort__name='m3', name='P7')
        m3_p6 = Period.objects.get(cohort__name='m3', name='P6')
        InternshipModalityPeriod(internship=mg_internship, period=m3_p8).save()
        InternshipModalityPeriod(internship=mg_internship, period=m3_p7).save()
        InternshipModalityPeriod(internship=mg_internship, period=m3_p6).save()

        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

        # execute algorithms for each cohort
        _execute_assignment_algorithm(cls.cohorts[0])
        _execute_assignment_algorithm(cls.cohorts[1])
        _execute_assignment_algorithm(cls.cohorts[2])

    @skip('print algorithm execution results')
    def test_algorithm_execution_print_results(self):
        affectations = InternshipStudentAffectationStat.objects.all()
        for student in Student.objects.all():
            for aff in affectations.filter(student=student).order_by('period__name'):
                print(aff.student, aff.internship, aff.period, aff.organization, aff.period.cohort)
            print('--')

    def test_all_periods_affected_for_each_student(self):
        affectations = InternshipStudentAffectationStat.objects.all()
        periods_count = len([period for cohort in self.cohorts for period in get_effective_periods(cohort.id)])
        for student in Student.objects.all():
            self.assertEqual(affectations.filter(student=student).count(), periods_count)

    def test_algorithm_execution_check_no_duplicate_mandatory_internships_across_cohorts(self):
        affectations = InternshipStudentAffectationStat.objects.all()
        for student in Student.objects.all():
            student_affectations = affectations.filter(student=student)
            student_affected_internships_specialties = []
            for aff in student_affectations:
                if aff.internship.speciality:
                    self.assertNotIn(aff.internship.speciality.name, student_affected_internships_specialties)
                    student_affected_internships_specialties.append(aff.internship.speciality.name)

    def test_algorithm_execution_check_medecine_generale_is_in_P6_or_P7_or_P8(self):
        medecine_generale_affectations = InternshipStudentAffectationStat.objects.filter(
            internship__speciality__name="Medecine Générale"
        )
        self.assertGreater(len(medecine_generale_affectations), 0)
        for aff in medecine_generale_affectations:
            self.assertIn(aff.period.name, ["P6", "P7", "P8"])

    def test_one_non_mandatory_internship_by_student(self):
        affectations = InternshipStudentAffectationStat.objects.all()
        for student in Student.objects.all():
            self.assertTrue(
                len([aff for aff in affectations.filter(student=student) if aff.internship.speciality is None]) == 1
            )


class AssignmentWithPeriodModalityTest(TestCase):
    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.periods = [PeriodFactory(name=f"P{_}", cohort=cls.cohort) for _ in range(1, N_PERIODS)]

        cls.mandatory_internships, cls.mandatory_specialties = _create_mandatory_internships(cls)
        cls.non_mandatory_internships, cls.non_mandatory_specialties = _create_non_mandatory_internships(cls)
        cls.students = _create_internship_students(cls)

        cls.hospital_error = OrganizationFactory(name='Hospital Error', cohort=cls.cohort, reference=999)
        cls.organizations = [OrganizationFactory(cohort=cls.cohort) for _ in range(0, N_ORGANIZATIONS)]

        cls.specialties = cls.mandatory_specialties + cls.non_mandatory_specialties
        cls.internships = cls.mandatory_internships + cls.non_mandatory_internships

        cls.offers = _create_internship_offers(cls)
        cls.places = _declare_offer_places(cls)
        _make_student_choices(cls)

        # force Stages au choix in first period
        for sc_internship in cls.non_mandatory_internships:
            p1 = Period.objects.get(name='P1')
            InternshipModalityPeriod(internship=sc_internship, period=p1).save()

        _execute_assignment_algorithm(cls.cohort)
        cls.affectations = InternshipStudentAffectationStat.objects.all()

        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

    def test_all_periods_affected_for_each_student(self):
        self.affectations = InternshipStudentAffectationStat.objects.all()
        periods_count = get_effective_periods(self.cohort.id).count()
        for student in Student.objects.all():
            self.assertEqual(self.affectations.filter(student=student).count(), periods_count)

    def test_should_assign_chosen_internship_only_in_P1(self):
        chosen_internship_affectations = self.affectations.filter(internship__in=self.non_mandatory_internships)
        self.assertGreater(len(chosen_internship_affectations), 0)
        for aff in chosen_internship_affectations:
            self.assertIn(aff.period.name, ["P1"])

    @skip('print algorithm execution results')
    def test_algorithm_execution_print_results(self):
        periods = Period.objects.all().order_by('name')
        for student in Student.objects.all():
            for period in periods:
                try:
                    aff = self.affectations.get(student=student, period=period)
                    print(aff.student, aff.internship, aff.period, aff.organization, aff.period.cohort)
                except InternshipStudentAffectationStat.DoesNotExist:
                    print(student, "-----------", period, "-", "-")
            print('--')
