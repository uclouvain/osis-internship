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

from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.cohort import Cohort
from internship.models.internship import Internship
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_enrollment import InternshipEnrollment
from internship.models.internship_offer import InternshipOffer
from internship.models.period_internship_places import PeriodInternshipPlaces
from internship.models.organization import Organization
from internship.models.period import Period
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from base.models.student import Student
from django.db.models.functions import Length
from internship.utils.list_utils import difference
from internship.utils.period_utils import *
from internship.utils.period_place_utils import *
import random

class AssignmentSolver:
    def __init__(self, cohort):
        self.cohort = cohort
        self.costs  = {1: 0, 2: 1, 3: 2, 4: 3, 'E': 0, 'I': 10, 'X': 1000}

    def initialize_data(self):
        self.affectations = []
        self.student_informations      = InternshipStudentInformation.objects.filter(cohort=self.cohort).order_by("?")
        self.person_ids                = self.student_informations.values_list("person_id", flat=True)
        self.students                  = Student.objects.filter(person_id__in=self.person_ids)
        self.internships               = Internship.objects.filter(cohort=self.cohort).order_by("speciality__order_position", "name")
        self.mandatory_internships     = self.internships.exclude(speciality__isnull=True)
        self.non_mandatory_internships = self.internships.filter(speciality__isnull=True)
        self.default_organization      = Organization.objects.filter(cohort=self.cohort, reference="999").first()
        self.forbidden_organizations   = Organization.objects.annotate(reference_length=Length('reference')) \
                                          .exclude(reference="00").filter(cohort=self.cohort, reference_length=3)
        self.default_speciality        = InternshipSpeciality.objects.filter(cohort=self.cohort, acronym="MO").first()
        self.pending_organization      = Organization.objects.filter(cohort=self.cohort, reference="604").first()
        self.offers                    = InternshipOffer.objects.filter(cohort=self.cohort)
        self.periods                   = Period.objects.extra(select={"period_number": "CAST(substr(name, 2) AS INTEGER)"}) \
                                          .exclude(name="P12").filter(cohort=self.cohort).order_by("period_number")
        self.offer_ids                 = self.offers.values_list("id", flat=True)
        self.available_places          = PeriodInternshipPlaces.objects.filter(internship_offer_id__in=self.offer_ids).values()
        self.mandatory_periods         = self.periods.exclude(name="P1").exclude(name="P2")
        self.errors_count              = 0

    def solve(self):
        self.initialize_data()
        self.assign_enrollments_to_students(self.internships)
        for internship in self.internships:
            self.assign_priority_choices_to_students(internship)
            self.assign_best_offer_for_student_choices(self.student_informations, internship)
        self.assign_default_speciality_and_organization_for_students_with_empty_periods(self.default_speciality, self.pending_organization, self.students, self.periods)

    def persist_solution(self):
        for affectation in self.affectations:
            affectation.save()

    def assign_enrollments_to_students(self, internships):
        enrollments = InternshipEnrollment.objects.filter(internship__in=internships)
        for enrollment in enrollments:
            affectation = self.build_student_affectation(enrollment.place, enrollment.student, enrollment.period, \
                            enrollment.internship_offer.speciality, "E", True)

            self.update_period_places_for_affectation(affectation)
            self.affectations.append(affectation)

    def assign_priority_choices_to_students(self, internship):
        priority_student_ids = InternshipChoice.objects.filter(internship=internship, priority=True).values("student").distinct()
        for student_id in priority_student_ids:
            student = Student.objects.get(pk=student_id["student"])
            self.assign_offer_to_student(student, internship)

    def assign_best_offer_for_student_choices(self, student_informations, internship):
        for student_information in student_informations:
            student = Student.objects.filter(person_id=student_information.person_id).first()
            self.assign_offer_to_student(student, internship)

    def assign_offer_to_student(self, student, internship):
        choices = InternshipChoice.objects.filter(student=student, internship=internship).order_by("choice")
        if self.student_has_empty_periods(student, self.affectations) and \
                self.student_has_no_current_affectation_to_internship(student, internship, self.affectations):
            affectation = self.assign_choices_to_student(student, choices, internship)
            self.affectations.extend(affectation)

    def assign_choices_to_student(self, student, choices, internship):
        affectations = []

        for choice in choices:
            periods = self.find_first_student_available_periods_for_internship_choice(student, internship, choice)
            if len(periods) > 0:
                affectations.extend(self.build_affectation_for_periods(student, choice.organization, periods, choice.speciality, choice.choice, choice.priority))
                break

        if len(affectations) == 0 and internship.speciality: # None of student choices available?
            affectations.extend(self.find_best_affectation_outside_of_choices(student, internship, choices))

        return affectations

    def assign_default_speciality_and_organization_for_students_with_empty_periods(self, speciality, organization, students, periods):
        for student in students:
            if self.student_has_empty_periods(student, self.affectations):
                periods      = self.all_available_periods(student, self.non_mandatory_internships[0], self.periods)
                affectations = self.build_affectation_for_periods(student, organization, periods, speciality, "I", False)
                self.affectations.extend(affectations)

    def find_first_student_available_periods_for_internship_choice(self, student, internship, choice):
        periods_with_places = self.find_available_periods_for_internship_choice(internship, choice)
        return self.first_relevant_periods(student, internship, periods_with_places)

    def find_best_affectation_outside_of_choices(self, student, internship, choices):
        student_periods = self.find_first_student_available_periods_for_internship(student, internship)

        if len(student_periods) == 0:
            student_periods = self.find_first_student_available_periods_regardless_of_internship(student, internship)

        offer = self.find_best_available_offer_for_internship_periods(internship, choices, student_periods)
        return self.build_affectation_for_periods(student, offer.organization, student_periods, offer.speciality, "I", False)

    def find_first_student_available_periods_for_internship(self, student, internship):
        periods_with_places  = self.find_available_periods_for_internship(internship)
        return self.first_relevant_periods(student, internship, periods_with_places)

    def find_first_student_available_periods_regardless_of_internship(self, student, internship):
        periods = []
        if internship.speciality:
            internship_periods = self.mandatory_periods
            periods = self.first_relevant_periods(student, internship, internship_periods)

        if len(periods) == 0:
            internship_periods = self.periods
            periods = self.first_relevant_periods(student, internship, internship_periods)
        return periods

    def first_relevant_periods(self, student, internship, periods):
        available_periods    = self.all_available_periods(student, internship, periods)
        grouped_periods      = list(group_periods_by_consecutives(available_periods, length=internship.length_in_periods))

        if len(grouped_periods) > 0:
            return random.choice(grouped_periods)
        else:
            return grouped_periods

    def all_available_periods(self, student, internship, periods):
        student_affectations = self.get_student_affectations(student, self.affectations)
        unavailable_periods  = self.get_periods_from_affectations(student_affectations)
        available_periods    = difference(periods, unavailable_periods)
        return available_periods

    def find_best_available_offer_for_internship_periods(self, internship, choices, periods):
        unavailable_organizations = list(map(lambda choice: choice.organization, choices))
        available_offers          = self.find_offers_for_available_organizations(internship, unavailable_organizations)
        period_places             = self.get_available_period_places_for_periods(available_offers, periods)

        if len(period_places) > 0:
            return available_offers.filter(pk=period_places[0]["internship_offer_id"]).first()
        else:
            if internship.alternate_speciality:
                offer = self.find_offer_in_alternate_speciality_for_internship(internship, periods)
                return offer
            else:
                self.errors_count += 1
                offer = self.find_offer_in_default_organization_for_internship(internship)
                return offer

    def find_offer_in_alternate_speciality_for_internship(self, internship, periods):
        available_offers = self.find_offers_for_speciality(internship.alternate_speciality)
        period_places    = self.get_available_period_places_for_periods(available_offers, periods)
        if len(period_places) > 0:
            return available_offers.filter(pk=period_places[0]["internship_offer_id"]).first()
        else:
            self.errors_count += 1
            return self.find_offer_in_default_organization_for_internship(internship)

    def get_available_period_places_for_periods(self, offers, periods):
        available_offer_ids                 = offers.values_list("id", flat=True)
        period_ids                          = map_period_ids(periods)
        offers_period_places                = get_period_places_for_offer_ids(available_offer_ids, self.available_places)
        period_places_for_periods           = get_period_places_for_period_ids(period_ids, offers_period_places)
        return sort_period_places(period_places_for_periods)

    def find_available_periods_for_internship(self, internship):
        offers = self.find_offers_for_available_organizations(internship)
        return self.find_available_periods_for_offers(offers)

    def find_available_periods_for_internship_choice(self, internship, choice):
        offers = self.find_offers_for_internship_choice(internship, choice)
        return self.find_available_periods_for_offers(offers)

    def find_available_periods_for_offers(self, offers):
        offer_ids                    = offers.values_list("id", flat=True)
        period_places_for_offers     = get_period_places_for_offer_ids(offer_ids, self.available_places)
        available_period_places      = sort_period_places(period_places_for_offers)
        period_ids                   = get_period_ids_from_period_places(available_period_places)
        return self.periods.filter(pk__in=period_ids).order_by("id")

    def update_period_places_for_affectation(self, affectation):
        period           = affectation.period
        offer            = self.find_offer_for_affectation(affectation)
        period_place     = get_period_place_for_offer_and_period(offer, period, self.available_places)
        new_places_count = period_place["number_places"] - 1
        replace_period_place_in_dictionnary(period_place, self.available_places, new_places_count)

    def build_affectation_for_periods(self, student, organization, periods, speciality, choice, priority):
        affectations = []
        for period in periods:
            affectation = self.build_student_affectation(organization, student, period, speciality, choice, priority)
            self.update_period_places_for_affectation(affectation)
            affectations.append(affectation)
        return affectations

    def build_student_affectation(self, organization, student, period, speciality, choice, priority):
        if priority:
            type_of_internship = "S"
        else:
            type_of_internship = "N"

        if organization.reference == self.default_organization.reference:
            type_of_internship = "X"
            choice = "X"

        return InternshipStudentAffectationStat(
                organization = organization,
                student = student,
                period = period,
                speciality = speciality,
                choice = choice,
                cost = self.costs[choice],
                type_of_internship = type_of_internship
        )

    def get_student_affectations(self, student, affectations):
        return list(filter(lambda affectation: affectation.student_id == student.id, affectations))

    def student_has_no_current_affectation_to_internship(self, student, internship, affectations):
        student_affectations = self.get_student_affectations(student, affectations)
        student_affectations_for_internship = \
            filter(lambda affectation: affectation.speciality_id == internship.speciality_id, student_affectations)
        return len(list(student_affectations_for_internship)) == 0

    def student_has_empty_periods(self, student, affectations):
        student_affectations = self.get_student_affectations(student, affectations)
        unavailable_periods = self.get_periods_from_affectations(student_affectations)
        return len(unavailable_periods) != len(self.periods)

    def get_periods_from_affectations(self, affectations):
        return list(map(lambda affectation: affectation.period, affectations))

    def find_offers_for_available_organizations(self, internship, unavailable_organizations=[]):
        return self.offers.filter(internship = internship). \
                exclude(organization__in = unavailable_organizations). \
                exclude(organization__in = self.forbidden_organizations)

    def find_offers_for_speciality(self, speciality):
        return self.offers.filter(speciality = speciality). \
                exclude(organization__in = self.forbidden_organizations)

    def find_offer_for_affectation(self, affectation):
        return self.offers.filter(organization = affectation.organization, \
                speciality = affectation.speciality).first()

    def find_offer_in_default_organization_for_internship(self, internship):
        return self.offers.filter(internship = internship, \
                organization = self.default_organization).first()

    def find_offers_for_internship_choice(self, internship, choice):
        if internship.speciality:
            return self.offers.filter(internship = internship, \
                    speciality   = choice.speciality, \
                    organization = choice.organization)
        else:
            return self.offers.filter(internship = None, \
                    speciality = choice.speciality, \
                    organization = choice.organization)

