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

START_PERIOD = 9
END_PERIOD = 12
MAX_PREFERENCE = 4
NUMBER_INTERNSHIPS = 4


class Solver:
    def __init__(self):
        self.offers = []
        self.students = []

        self.offers_dict = dict()
        self.students_left_to_assign = []

    def initialize_f(self, filename):
        with open(filename) as file:
            number_offers, number_students = [int(x) for x in file.readline().split()]
            file.readline()

            for x in range(0, number_offers):
                self.__add_offer_from_line(file.readline())

            file.readline()

            for x in range(0, number_students):
                line = file.readline()
                self.__add_student_from_line(line)

            self.students_left_to_assign = self.students[:]

    def __add_student_from_line(self, line):
        student = Student.create_student(line)
        choice = Choice.create_choice(line)
        student.add_choice(choice)
        self.students.append(student)

    def __add_offer_from_line(self, line):
        offer = Offer.create_offer(line)
        key = (offer.organization_id, offer.speciality_id)
        self.offers_dict[key] = offer
        self.offers.append(offer)

    def get_number_offers(self):
        return len(self.offers)

    def get_number_students(self):
        return len(self.students)

    def solve(self):
        for preference in range(1, MAX_PREFERENCE + 1):
            for internship in range(1, NUMBER_INTERNSHIPS + 1):
                student_temp = []
                for student in self.students_left_to_assign:
                    if student.has_all_periods_assigned():
                        continue
                    choices = student.get_choices_for_preference(preference)
                    for choice in choices:
                        offer_key = (choice.organization_id, choice.speciality_id)
                        if offer_key not in self.offers_dict and not self.offers_dict[offer_key].has_place():
                            continue
                        offer = self.offers_dict[offer_key]
                        assigned = False
                        for period in offer.get_free_periods():
                            if student.has_period_unassigned(period):
                                student.assign(period, offer.offer_id)
                                assigned = True
                                break
                        if assigned:
                            break
                    student_temp.append(student)

                self.students_left_to_assign = student_temp


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

    def get_free_periods(self):
        periods = []
        for period in range(1, len(self.places)):
            if self.has_place(period):
                periods.append(period)
        return periods


class Student:
    def __init__(self, student_id):
        self.student_id = student_id
        self.choices = []
        self.assignments = dict()
        self.is_a_priority = False

        self._choices_by_preference = dict()
        self.cost = 0  # TODO compute cost

    def add_choice(self, choice):
        self.choices.append(choice)
        self.__add_by_preference(choice)
        self.__update_priority(choice)

    def __add_by_preference(self, choice):
        current_choices_for_preference = self._choices_by_preference.get(choice.preference, [])
        current_choices_for_preference.append(choice)
        self._choices_by_preference[choice.preference] = current_choices_for_preference

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

    def get_choices_for_preference(self, preference):
        return self._choices_by_preference.get(preference, [])

    def has_period_unassigned(self, period):
        return False if period in self.assignments else True


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



