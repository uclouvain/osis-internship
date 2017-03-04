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


def init_solver():
    solver = Solver()

    students_by_registration_id = _load_students_and_choices()
    solver.set_students(students_by_registration_id)

    offers_by_organization_speciality = _load_internship_and_places()
    solver.set_offers(offers_by_organization_speciality)

    return solver


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


class Solver:
    def __init__(self):
        self.students_by_registration_id = dict()
        self.offers_by_organization_speciality = dict()

    def set_students(self, students):
        self.students_by_registration_id = students

    def set_offers(self, offers):
        self.offers_by_organization_speciality = offers

    def get_student(self, registration_id):
        return self.students_by_registration_id.get(registration_id, None)

    def get_offer(self, organization_id, speciality_id):
        return self.offers_by_organization_speciality.get((organization_id , speciality_id), None)


class InternshipWrapper:
    def __init__(self):
        self.internship = None
        self.periods_places = dict()

    def set_internship(self, internship):
        self.internship = internship

    def set_period_places(self, period_places):
        period_name = period_places.period.name
        self.periods_places[period_name] = period_places

    def get_free_periods(self):
        free_periods = []
        for period_name, period_places in self.periods_places.items():
            if period_places.number_places > 0:
                free_periods.append(period_name)
        return free_periods


class StudentWrapper:
    def __init__(self):
        self.student = None
        self.choices = []
        self.choices_by_preference = dict()
        self.assignments = dict()

    def set_student(self, student):
        self.student = student

    def add_choice(self, choice):
        self.choices.append(choice)

        preference = choice.choice
        current_choices = self.choices_by_preference.get(preference, [])
        current_choices.append(choice)
        self.choices_by_preference[preference] = current_choices

    def get_number_choices(self):
        return len(self.choices)



