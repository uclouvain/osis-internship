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

SAMPLE1 = "./internship/tests/utils/ressources/sample1.txt"


class TestAffectStudent(SimpleTestCase):
    def setUp(self):
        self.solver = affect_student.Solver()
        self.solver.initialize_f(SAMPLE1)

    def test_initialize_problem(self):
        self.assertEqual(self.solver.get_number_offers(),  5)
        self.assertEqual(self.solver.get_number_students(), 4)

    def test_add_student(self):
        student = affect_student.Student(45)
        student_bis = affect_student.Student(41)
        other_solver = affect_student.Solver()

        self.assertFalse(other_solver.students)

        other_solver.add_student(student)
        other_solver.add_student(student_bis)

        self.assertEqual(student, other_solver.get_student(45))
        self.assertEqual(student_bis, other_solver.get_student(41))
        self.assertFalse(other_solver.get_student(40))

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
        self.assertEqual(self.offer.places, [4, 5, 0, 0])

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
        self.assertEqual(offer_created.places, [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2])

    def test_occupy_place(self):
        self.offer.occupy_place(1)
        self.assertEqual(self.offer.places_left[0], 3)

    def test_has_place(self):
        self.assertTrue(self.offer.has_place(1))
        self.assertFalse(self.offer.has_place(3))

    def test_get_free_periods(self):
        self.assertEqual(self.offer.get_free_periods(), [1, 2])

        offer = affect_student.Offer(1, 10, 15, [0, 1, 0, 0])
        self.assertEqual(offer.get_free_periods(), [2])
        offer.occupy_place(2)
        self.assertFalse(offer.get_free_periods())


class TestStudent(SimpleTestCase):
    def setUp(self):
        self.student = affect_student.Student(2)

    def test_init(self):
        self.assertEqual(self.student.student_id, 2)

    def test_add_choice(self):
        choice_1 = affect_student.Choice(1, 2, 1, 1, False)
        choice_2 = affect_student.Choice(1, 3, 1, 2, False)
        self.student.add_choice(choice_1)
        self.student.add_choice(choice_2)
        self.assertEqual(len(self.student.choices), 2)

    def test_add_choice_by_preference(self):
        choice_1 = affect_student.Choice(2, 4, 1, 2, False)
        choice_2 = affect_student.Choice(1, 3, 1, 1, False)
        choice_3 = affect_student.Choice(1, 5, 1, 2, False)
        self.student.add_choice(choice_1)
        self.student.add_choice(choice_2)
        self.student.add_choice(choice_3)

        self.assertEqual(len(self.student._choices_by_preference), 2)
        self.assertEqual(len(self.student.get_choices_for_preference(1)), 1)
        self.assertEqual(len(self.student.get_choices_for_preference(2)), 2)

    def test_specialities_chosen(self):
        choice_1 = affect_student.Choice(2, 4, 5, 2, False)
        choice_2 = affect_student.Choice(1, 3, 4, 1, False)
        choice_3 = affect_student.Choice(1, 5, 5, 2, False)
        self.student.add_choice(choice_1)
        self.student.add_choice(choice_2)
        self.student.add_choice(choice_3)
        self.assertIn(5, self.student.get_specialities_chosen())
        self.assertIn(4, self.student.get_specialities_chosen())

    def test_create_student(self):
        student = affect_student.Student.create_student("1 1 1 1 1 1")
        self.assertTrue(student)
        self.assertEqual(student.student_id, 1)

    def test_assign(self):
        self.student.assign(9, 5)
        self.student.assign(10, 8)
        self.assertEqual(len(self.student.assignments), 2)
        self.assertEqual(self.student.assignments[9], 5)
        self.assertEqual(self.student.assignments[10], 8)

    def test_has_all_period_assigned(self):
        self.student.assignments = {8: 4,
                                     9: 5}
        self.assertFalse(self.student.has_all_periods_assigned())
        self.student.assignments = {9: 4,
                                     10: 5,
                                     11: 6,
                                     12: 8}
        self.assertTrue(self.student.has_all_periods_assigned())

    def test_priority(self):
        self.assertFalse(self.student.is_a_priority)
        choice = affect_student.Choice(2, 4, 5, 2, True)
        self.student.add_choice(choice)
        self.assertTrue(self.student.is_a_priority)

    def test_has_period_unassigned(self):
        self.student.assignments = {1 : 5,
                                    3 : 4}
        self.assertTrue(self.student.has_period_unassigned(2))
        self.assertFalse(self.student.has_period_unassigned(3))


class TestChoice(SimpleTestCase):
    def setUp(self):
        self.choice = affect_student.Choice(1, 5, 4, 1, True)

    def test_init(self):
        self.assertEqual(self.choice.internship_id, 1)
        self.assertEqual(self.choice.organization_id, 5)
        self.assertEqual(self.choice.speciality_id, 4)
        self.assertEqual(self.choice.preference, 1)
        self.assertEqual(self.choice.priority, True)

    def test_create_choice(self):
        choice = affect_student.Choice.create_choice("1 1 1 1 1 1")
        self.assertTrue(choice)
        self.assertEqual(choice.internship_id, 1)
        self.assertEqual(choice.organization_id, 1)
        self.assertEqual(choice.speciality_id, 1)
        self.assertEqual(choice.preference, 1)
        self.assertEqual(choice.priority, True)


