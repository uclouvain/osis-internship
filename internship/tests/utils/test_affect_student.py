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
from django.test import SimpleTestCase
from internship.utils import affect_student
from internship.tests.models import test_internship_choice, test_organization, test_internship_speciality, \
    test_internship_offer, test_period
from base.tests.models import test_student

SAMPLE1 = "./internship/tests/utils/ressources/sample1.txt"


class TestAffectStudent(SimpleTestCase):
    def setUp(self):
        self.solver = affect_student.Solver()
        self.solver.initialize_f(SAMPLE1)

    def test_initialize_problem(self):
        self.assertEqual(self.solver.get_number_offers(),  5)
        self.assertEqual(self.solver.get_number_students(), 4)

    def test_add_student(self):
        student = affect_student.StudentWrapper(45)
        student_bis = affect_student.StudentWrapper(41)
        other_solver = affect_student.Solver()

        self.assertFalse(other_solver.students_dict)

        other_solver.add_student(student)
        other_solver.add_student(student_bis)

        self.assertEqual(student, other_solver.get_student(45))
        self.assertEqual(student_bis, other_solver.get_student(41))
        self.assertFalse(other_solver.get_student(40))

    def test_add_solver(self):
        offer_1 = affect_student.Offer(1, 4, 5, [])
        offer_2 = affect_student.Offer(2, 6, 5, [])
        other_solver = affect_student.Solver()

        self.assertFalse(other_solver.offers_dict)

        other_solver.add_offer(offer_1)
        other_solver.add_offer(offer_2)

        self.assertEqual(offer_1, other_solver.get_offer(4, 5))
        self.assertEqual(offer_2, other_solver.get_offer(6, 5))
        self.assertFalse(other_solver.get_offer(9, 1))

    def test_solve(self):
        try:
            self.solver.solve()
        except Exception:
            self.fail()


class TestOffer(SimpleTestCase):
    def setUp(self):
        self.offer = affect_student.Offer(1, 10, 15, [4, 5, 0, 0])

    def test_init(self):
        self.assertEqual(self.offer.offer_id, 1)
        self.assertEqual(self.offer.organization_id, 10)
        self.assertEqual(self.offer.speciality_id, 15)
        self.assertEqual(self.offer.places, {1: 4, 2: 5, 3: 0, 4: 0})

    def test_get_number_place_for_period(self):
        self.assertEqual(self.offer.get_period_places(0), 0)
        self.assertEqual(self.offer.get_period_places(1), 4)
        self.assertEqual(self.offer.get_period_places(2), 5)
        self.assertEqual(self.offer.get_period_places(4), 0)
        self.assertEqual(self.offer.get_period_places(10), 0)

    def test_create_offer(self):
        offer_created = affect_student.Offer.create_offer("1 1 1 0 0 0 0 0 0 0 0 0 2 0 2")
        self.assertTrue(offer_created)
        self.assertEqual(offer_created.offer_id, 1)
        self.assertEqual(offer_created.organization_id, 1)
        self.assertEqual(offer_created.speciality_id, 1)
        self.assertEqual(len(offer_created.places), 12)

    def test_occupy_place(self):
        self.offer.occupy_place(1)
        self.assertEqual(self.offer.places_left[1], 3)

    def test_has_place(self):
        self.assertTrue(self.offer.has_place(1))
        self.assertFalse(self.offer.has_place(3))

    def test_get_free_periods(self):
        self.assertEqual(self.offer.get_free_periods(), [1, 2])

        offer = affect_student.Offer(1, 10, 15, [0, 1, 0, 0])
        self.assertEqual(offer.get_free_periods(), [2])
        offer.occupy_place(2)
        self.assertFalse(offer.get_free_periods())

    def test_add_places(self):
        self.assertEqual(self.offer.get_period_places(5), 0)
        self.offer.add_places(5, 7)
        self.assertEqual(self.offer.get_period_places(5), 7)


class TestStudent(SimpleTestCase):
    def setUp(self):
        self.student = test_student.create_student("first", "last", "64641200")
        organization_1 = test_organization.create_organization(name="organization1", reference="01")

        self.speciality_1 = test_internship_speciality.create_speciality(name="spec1")
        self.speciality_2 = test_internship_speciality.create_speciality(name="spec2")

        self.choice_1 = test_internship_choice.create_internship_choice(organization_1, self.student, self.speciality_1,
                                                                        internship_choice=1)
        self.choice_2 = test_internship_choice.create_internship_choice(organization_1, self.student, self.speciality_2,
                                                                        internship_choice=2)
        self.offer = test_internship_offer.create_specific_internship_offer(organization_1, self.speciality_1)
        self.period = test_period.create_period("P9")
        self.student_wrapper = affect_student.StudentWrapper(self.student)

    def test_init(self):
        self.assertEqual(self.student_wrapper.student, self.student)

    def test_add_choice(self):
        self.assertEqual(len(self.student.choices), 0)
        self.student.add_choice(self.choice_1)
        self.assertEqual(len(self.student.choices), 1)
        self.student.add_choice(self.choice_2)
        self.assertEqual(len(self.student.choices), 2)
        self.assertEqual(len(self.student.get_choices_for_preference(1)), 2)
        self.assertEqual(len(self.student.get_choices_for_preference(2)), 0)

    def test_specialities_chosen(self):
        self.student.add_choice(self.choice_1)

        self.assertIn(self.speciality_1, self.student.get_specialities_chosen())
        self.assertNotIn(self.speciality_2, self.student.get_specialities_chosen())

        self.student.add_choice(self.choice_2)

        self.assertIn(self.speciality_1, self.student.get_specialities_chosen())
        self.assertIn(self.speciality_2, self.student.get_specialities_chosen())

    def test_assign(self):
        self.student.assign(self.period, self.offer)
        self.assertEqual(len(self.student.assignments), 1)
        self.assertEqual(self.student.assignments[self.period], self.offer)
        self.assertFalse(self.student.assignments["P4"])

    def test_has_period_unassigned(self):
        self.student.assignments = {1 : 5,
                                    3 : 4}
        self.assertTrue(self.student.has_period_unassigned(2))
        self.assertFalse(self.student.has_period_unassigned(3))

    def test_get_assignments(self):
        self.student.assignments = {1: 4, 3: 5, 8: 9}
        assignments = self.student.get_assignments()

        self.assertEqual(len(self.student.get_assignments()), 3)
        self.assertIn((1, 4), assignments)
        self.assertIn((3, 5), assignments)
        self.assertIn((8, 9), assignments)


