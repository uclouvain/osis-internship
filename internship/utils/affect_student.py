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
from internship import models as mdl_internship


MAX_PREFERENCE = 4
AUTHORIZED_PERIODS = ["P9", "P10", "P11", "P12"]
NUMBER_INTERNSHIPS = len(AUTHORIZED_PERIODS)
REFERENCE_DEFAULT_ORGANIZATION = 999

# TODO remove places already occupied
def affect_student():
    solver = init_solver()
    assignments = launch_solver(solver)
    save_assignments_to_db(assignments)


def init_solver():
    solver = Solver()

    periods = _load_periods()
    solver.set_periods(periods)

    solver.default_organization = _load_default_organization()

    students_by_registration_id = _load_students_and_choices()
    solver.set_students(students_by_registration_id)

    offers_by_organization_speciality = _load_internship_and_places()
    solver.set_offers(offers_by_organization_speciality)

    return solver


def launch_solver(solver):
    solver.solve()
    assignments = solver.get_solution()
    return assignments


def save_assignments_to_db(assignments):
    for affectation in assignments:
        affectation.save()


def _load_students_and_choices():
    students_by_registration_id = dict()
    student_choices = mdl_internship.internship_choice.get_non_mandatory_internship_choices()
    for choice in student_choices:
        student = choice.student
        student_wrapper = students_by_registration_id.get(student.registration_id, None)
        if not student_wrapper:
            student_wrapper = StudentWrapper()
            student_wrapper.set_student(student)
            students_by_registration_id[student.registration_id] = student_wrapper
        student_wrapper.add_choice(choice)
    return students_by_registration_id


def _load_internship_and_places():
    offers_by_organization_speciality = dict()
    internships_periods_places = mdl_internship.period_internship_places.PeriodInternshipPlaces.objects.all()
    for period_places in internships_periods_places:
        internship = period_places.internship
        key = (internship.organization.id, internship.speciality.id)
        internship_wrapper = offers_by_organization_speciality.get(key, None)
        if not internship_wrapper:
            internship_wrapper = InternshipWrapper()
            internship_wrapper.set_internship(internship)
            offers_by_organization_speciality[key] = internship_wrapper
        internship_wrapper.set_period_places(period_places)
    return offers_by_organization_speciality


def _load_periods():
    periods = mdl_internship.period.Period.objects.all()
    return list(filter(lambda period: period.name.strip() in AUTHORIZED_PERIODS, periods))


def _load_default_organization():
    return mdl_internship.organization.Organization.objects.get(reference=REFERENCE_DEFAULT_ORGANIZATION)


class Solver:
    def __init__(self):
        self.students_by_registration_id = dict()
        self.students_lefts_to_assign = []
        self.offers_by_organization_speciality = dict()
        self.offers_by_speciality = dict()
        self.periods = []
        self.default_organization = None

    def set_students(self, students):
        self.students_by_registration_id = students
        self.students_lefts_to_assign = list(students.values())

    def set_offers(self, offers):
        self.offers_by_organization_speciality = offers
        self.__init_offers_by_speciality(offers)

    def set_periods(self, periods):
        self.periods = periods

    def __init_offers_by_speciality(self, offers):
        for offer in offers.values():
            speciality = offer.internship.speciality
            current_offers_for_speciality = self.offers_by_speciality.get(speciality.id, [])
            current_offers_for_speciality.append(offer)
            self.offers_by_speciality[speciality.id] = current_offers_for_speciality

    def get_student(self, registration_id):
        return self.students_by_registration_id.get(registration_id, None)

    def get_offer(self, organization_id, speciality_id):
        return self.offers_by_organization_speciality.get((organization_id, speciality_id), None)

    def get_solution(self):
        assignments = []
        for student_wrapper in self.students_by_registration_id.values():
            for affectation in student_wrapper.get_assignments():
                assignments.append(affectation)
        return assignments

    def solve(self):
        self.__assign_choices()
        # self.__assign_unfulfilled_students()
        # self.__assign_to_default_offer()

    def __assign_choices(self):
        for preference in range(1, MAX_PREFERENCE + 1):
            for internship in range(0, NUMBER_INTERNSHIPS):
                students_to_assign = []
                for student_wrapper in self.students_lefts_to_assign:
                    self.__assign_student_choices(preference, student_wrapper)
                    if not student_wrapper.has_all_internships_assigned():
                        students_to_assign.append(student_wrapper)

                self.students_lefts_to_assign = students_to_assign

    def __assign_student_choices(self, preference, student_wrapper):
        student_preference_choices = student_wrapper.get_choices_for_preference(preference)
        for choice in student_preference_choices:
            if self.__assign_choice_to_student(choice, student_wrapper):
                break

    def __assign_choice_to_student(self, choice, student_wrapper):
        if student_wrapper.has_internship_assigned(choice.internship_choice):
            return False
        internship_wrapper = self.get_offer(choice.organization.id, choice.speciality.id)
        if not internship_wrapper:
            return False
        free_period_name = self.__get_valid_period(internship_wrapper, student_wrapper)
        if not free_period_name:
            return False
        self.__occupy_offer(free_period_name, internship_wrapper, student_wrapper, choice)
        return True

    @staticmethod
    def __get_valid_period(internship_wrapper, student_wrapper):
        free_periods_name = internship_wrapper.get_free_periods()
        student_periods_possible = filter(lambda period: student_wrapper.has_period_assigned(period) is False,
                                          free_periods_name)
        free_period_name = next(student_periods_possible, None)
        return free_period_name

    def __assign_unfulfilled_students(self):
        for internship in range(0, NUMBER_INTERNSHIPS):
            students_to_assign = []
            for student_wrapper in self.students_lefts_to_assign:
                self.__assign_first_possible_offer_to_student(student_wrapper)
                if not student_wrapper.has_all_internships_assigned():
                    students_to_assign.append(student_wrapper)
            self.students_lefts_to_assign = students_to_assign

    def __assign_first_possible_offer_to_student(self, student_wrapper):
        for speciality_id, offers in self.offers_by_speciality.items():
            for offer in filter(lambda possible_offer: possible_offer.is_not_full() is False, offers):
                free_period_name = self.__get_valid_period(offer, student_wrapper)
                if free_period_name:
                    period_places = offer.occupy(free_period_name)
                    student_wrapper.assign(period_places, 0, 0)
                    return True
        return False

    def __assign_to_default_offer(self):
        for student_wrapper in self.students_lefts_to_assign:
            student_wrapper.fill_assignments(self.periods, self.default_organization)

    @staticmethod
    def __occupy_offer(free_period_name, internship_wrapper, student_wrapper, choice):
        period_places = internship_wrapper.occupy(free_period_name)
        student_wrapper.assign(period_places, choice.internship_choice, choice.choice)


class InternshipWrapper:
    def __init__(self):
        self.internship = None
        self.periods_places = dict()
        self.periods_places_left = dict()

    def set_internship(self, internship):
        self.internship = internship

    def set_period_places(self, period_places):
        period_name = period_places.period.name
        self.periods_places[period_name] = period_places
        self.periods_places_left[period_name] = period_places.number_places

    def period_is_not_full(self, period_name):
        return self.periods_places_left.get(period_name, 0) > 0

    def get_free_periods(self):
        free_periods = []
        for period_name in self.periods_places_left.keys():
            if self.period_is_not_full(period_name):
                free_periods.append(period_name)
        return free_periods

    def is_not_full(self):
        return len(self.get_free_periods()) > 0

    def occupy(self, period_name):
        self.periods_places_left[period_name] -= 1
        return self.periods_places[period_name]


class StudentWrapper:
    def __init__(self):
        self.student = None
        self.choices = []
        self.choices_by_preference = dict()
        self.assignments = dict()
        self.internship_assigned = []
        self.specialities_by_internship = dict()

    def set_student(self, student):
        self.student = student

    def add_choice(self, choice):
        self.choices.append(choice)

        preference = choice.choice
        current_choices = self.choices_by_preference.get(preference, [])
        current_choices.append(choice)
        self.choices_by_preference[preference] = current_choices

        self.specialities_by_internship[choice.internship_choice] = choice.speciality

    def get_number_choices(self):
        return len(self.choices)

    def assign(self, period_places, internship_choice, preference, cost=0):
        period_name = period_places.period.name
        self.assignments[period_name] = \
            mdl_internship.internship_student_affectation_stat.\
            InternshipStudentAffectationStat(period=period_places.period,
                                             organization=period_places.internship.organization,
                                             speciality=period_places.internship.speciality,
                                             student=self.student,
                                             choice=preference,
                                             cost=cost)
        self.internship_assigned.append(internship_choice)

    def has_internship_assigned(self, internship):
        return internship in self.internship_assigned

    def has_all_internships_assigned(self):
        return len(self.internship_assigned) == NUMBER_INTERNSHIPS

    def get_choices_for_preference(self, preference):
        return self.choices_by_preference.get(preference, [])

    def has_period_assigned(self, period_name):
        return period_name in self.assignments

    def get_assignments(self):
        return self.assignments.values()

    def selected_specialities(self):
        return list(set([choice.speciality for choice in self.choices]))

    def fill_assignments(self, periods, default_organization, cost=0):
        if not self.choices:
            return
        for period in filter(lambda p: p.name not in self.assignments, periods):
            speciality = self.choices[0].speciality
            for internship, spec in self.specialities_by_internship.items():
                if not self.has_internship_assigned(internship):
                    speciality = spec
                    break
            self.assignments[period.name] = \
                mdl_internship.internship_student_affectation_stat. \
                InternshipStudentAffectationStat(period=period,
                                                 organization=default_organization,
                                                 speciality=speciality,
                                                 student=self.student,
                                                 choice=0,
                                                 cost=cost)
            self.internship_assigned.append(-1)
    # TODO fill empty assignments



