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
from django.test import TestCase
from base.tests.models import test_student
from internship.tests.models import test_organization, test_internship_speciality, test_internship_choice, \
    test_internship_offer, test_period, test_period_internship_places
from internship.utils import affect_student
from internship.models import internship_student_affectation_stat as mdl_student_affectation


class TestAffectStudent(TestCase):
    def setUp(self):
        self.student_1 = test_student.create_student("Student1", "Last", "1")
        self.student_2 = test_student.create_student("Student2", "Last", "2")

        organization_1 = test_organization.create_organization(name="organization1", reference="01")
        organization_2 = test_organization.create_organization(name="organization2", reference="02")
        organization_3 = test_organization.create_organization(name="organization3", reference="03")
        default_organization = test_organization.create_organization(name="Hôpital Erreur", reference="999")

        speciality_1 = test_internship_speciality.create_speciality(name="spec1")
        speciality_2 = test_internship_speciality.create_speciality(name="spec2")
        speciality_3 = test_internship_speciality.create_speciality(name="spec3")

        test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_1,
                                                        internship_choice=1)
        test_internship_choice.create_internship_choice(organization_2, self.student_1, speciality_1,
                                                        internship_choice=1, choice=2)
        test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_2,
                                                        internship_choice=2)
        test_internship_choice.create_internship_choice(organization_2, self.student_1, speciality_1,
                                                        internship_choice=3)
        test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_1,
                                                        internship_choice=4)
        test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_2,
                                                        internship_choice=5)
        test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_2,
                                                        internship_choice=6)

        test_internship_choice.create_internship_choice(organization_1, self.student_2, speciality_1,
                                                        internship_choice=1)
        test_internship_choice.create_internship_choice(organization_2, self.student_2, speciality_1,
                                                        internship_choice=1, choice=2)
        test_internship_choice.create_internship_choice(organization_1, self.student_2, speciality_2,
                                                        internship_choice=2)
        test_internship_choice.create_internship_choice(organization_2, self.student_2, speciality_1,
                                                        internship_choice=3)
        test_internship_choice.create_internship_choice(organization_1, self.student_2, speciality_1,
                                                        internship_choice=4)
        test_internship_choice.create_internship_choice(organization_1, self.student_2, speciality_2,
                                                        internship_choice=5)
        test_internship_choice.create_internship_choice(organization_1, self.student_2, speciality_2,
                                                        internship_choice=6)

        self.offer_1 = test_internship_offer.create_specific_internship_offer(organization_1, speciality_1)
        self.offer_2 = test_internship_offer.create_specific_internship_offer(organization_1, speciality_2)
        self.offer_3 = test_internship_offer.create_specific_internship_offer(organization_2, speciality_1)

        period_9 = test_period.create_period("P9")
        period_10 = test_period.create_period("P10")
        period_11 = test_period.create_period("P11")
        period_12 = test_period.create_period("P12")

        self.period_places_1 = test_period_internship_places.create_period_places(self.offer_1, period_9)
        test_period_internship_places.create_period_places(self.offer_1, period_9, 2)
        test_period_internship_places.create_period_places(self.offer_1, period_11, 2)
        test_period_internship_places.create_period_places(self.offer_2, period_10, 2)
        test_period_internship_places.create_period_places(self.offer_2, period_12, 2)
        test_period_internship_places.create_period_places(self.offer_3, period_9, 2)
        test_period_internship_places.create_period_places(self.offer_3, period_11, 2)

    def test_init_solver(self):
        solver = affect_student.init_solver()
        self.assertEqual(len(solver.students_by_registration_id), 2)
        self.assertEqual(len(solver.offers_by_organization_speciality), 3)

        self.assert_number_choices(self.student_1, solver, 7)
        self.assert_number_choices(self.student_2, solver, 7)

        self.assert_free_periods(self.offer_1, solver, ["P9", "P11"])
        self.assert_free_periods(self.offer_2, solver, ["P10", "P12"])
        self.assert_free_periods(self.offer_3, solver, ["P9", "P11"])

    def assert_number_choices(self, student, solver, number_choices):
        student_wrapper = solver.get_student(student.registration_id)
        self.assertTrue(student_wrapper)
        self.assertEqual(student_wrapper.get_number_choices(), number_choices)

    def assert_free_periods(self, offer, solver, free_periods):
        internship_wrapper = solver.get_offer(offer.organization.id, offer.speciality.id)
        self.assertTrue(internship_wrapper)
        actual_free_periods = internship_wrapper.get_free_periods()
        self.assertEqual(len(free_periods), len(actual_free_periods))
        for free_period in free_periods:
            self.assertIn(free_period, actual_free_periods)

    def test_offer_places_left(self):
        offer = affect_student.InternshipWrapper()
        offer.set_internship(self.offer_1)
        offer.set_period_places(self.period_places_1)

        for x in range(0, self.period_places_1.number_places):
            self.assertTrue(offer.is_not_full())
            offer.occupy(self.period_places_1.period.name)

        self.assertFalse(offer.is_not_full())

    def test_solve(self):
        solver = affect_student.init_solver()
        try:
            assignments = affect_student.launch_solver(solver)
        except Exception:
            self.fail()
        self.assertEqual(len(assignments), 8)

        affect_student.save_assignments_to_db(assignments)

        self.assertEqual(mdl_student_affectation.InternshipStudentAffectationStat.objects.all().count(), 8)

    def test_places_occupied(self):
        affectation = mdl_student_affectation.InternshipStudentAffectationStat(student=self.student_1,
                                                                               period=self.period_places_1.period,
                                                                               organization=self.offer_1.organization,
                                                                               speciality=self.offer_1.speciality,
                                                                               choice=1, cost=0)
        affectation.save()
        solver = affect_student.init_solver()
        internship_wrapper = solver.get_offer(self.offer_1.organization.id, self.offer_1.speciality.id)
        self.assertEqual(internship_wrapper.periods_places_left[self.period_places_1.period.name], 1)

        student_wrapper = solver.get_student(self.student_1.registration_id)
        self.assertEqual(len(student_wrapper.internship_assigned), 1)

