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


class Solver:
    def __init__(self):
        self.offers = []
        self.students = []

    def initialize_f(self, filename):
        with open(filename) as file:
            number_offers, number_students = [int(x) for x in file.readline().split()]
            file.readline()
            for x in range(0, number_offers):
                line = file.readline()
                self.offers.append(Offer.create_offer(line))
            file.readline()
            for x in range(0, number_students):
                line = file.readline()
                student = Student.create_student(line)
                choice = Choice.create_choice(line)
                student.add_choice(choice)
                self.students.append(student)

    def get_number_offers(self):
        return len(self.offers)

    def get_number_students(self):
        return len(self.students)

    def solve(self):
        for student in self.students:
            pass


class Offer:
    def __init__(self, offer_id, organization_id, speciality_id, places):
        self.offer_id = offer_id
        self.organization_id = organization_id
        self.speciality_id = speciality_id
        self.places = places

        self.places_left = places[:]

    def get_period_places(self, period):
        index = period - 1
        if index > len(self.places_left) or index < 0:
            return 0
        return self.places_left[index]

    @staticmethod
    def create_offer(line):
        line_in_ints = [int(x) for x in line.split()]
        offer_id = line_in_ints[0]
        organization_id = line_in_ints[1]
        speciality_id = line_in_ints[2]
        places = line_in_ints[3:]
        return Offer(offer_id, organization_id, speciality_id, places)

    def has_place(self, period):
        return self.get_period_places(period) > 0

    def occupy_place(self, period):
        index = period - 1
        self.places_left[index] -= 1


class Student:
    def __init__(self, student_id):
        self.student_id = student_id
        self.choices = []
        self.assignments = dict()
        self.is_a_priority = False

        self.choices_by_preference = dict()
        self.cost = 0  # TODO compute cost

    def add_choice(self, choice):
        self.choices.append(choice)
        self.__add_by_preference(choice)
        self.__update_priority(choice)

    def __add_by_preference(self, choice):
        current_choices_for_preference = self.choices_by_preference.get(choice.preference, [])
        current_choices_for_preference.append(choice)
        self.choices_by_preference[choice.preference] = current_choices_for_preference

    def __update_priority(self, choice):
        if choice.priority:
            self.is_a_priority = True

    @staticmethod
    def create_student(line):
        line_in_ints = [int(x) for x in line.split()]
        student_id = line_in_ints[0]
        return Student(student_id)

    def assign(self, period, offer_id):
        self.assignments[period] = offer_id

    def has_all_period_assigned(self):
        START_PERIOD = 9
        END_PERIOD = 12
        periods = [x for x in range(START_PERIOD, END_PERIOD+1)]
        for period in periods:
            if period not in self.assignments:
                return False
        return True

    def get_specialities_chosen(self):
        specialities = set()
        for choice in self.choices:
            specialities.add(choice.speciality_id)
        return list(specialities)

    def get_cost(self):
        return self.cost


class Choice:
    def __init__(self, internship_id, organization_id, speciality_id, preference, priority):
        self.internship_id = internship_id
        self.organization_id = organization_id
        self.speciality_id = speciality_id
        self.preference = preference
        self.priority = priority
        self.offer_id = -1

    @staticmethod
    def create_choice(line):
        line_in_ints = [int(x) for x in line.split()]
        organization_id = line_in_ints[1]
        speciality_id = line_in_ints[2]
        internship_id = line_in_ints[3]
        preference = line_in_ints[4]
        priority = bool(line_in_ints[5])
        return Choice(internship_id, organization_id, speciality_id, preference, priority)



