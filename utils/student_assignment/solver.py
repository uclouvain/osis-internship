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

import random

from django.db import transaction
from django.db.models.functions import Length

from base.models.student import Student
from internship.models.internship import Internship
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_enrollment import InternshipEnrollment
from internship.models.internship_offer import InternshipOffer
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.organization import Organization
from internship.models.period import Period
from internship.models.period_internship_places import PeriodInternshipPlaces
from internship.utils.student_assignment.list_utils import difference, flatten
from internship.utils.student_assignment.period_place_utils import *
from internship.utils.student_assignment.period_utils import *
from internship.utils.student_assignment.student_utils import *


class AssignmentSolver:
    def __init__(self, cohort):
        self.cohort = cohort
        self.costs = {1: 0, 2: 1, 3: 2, 4: 3, 'E': 0, 'I': 10, 'X': 1000}
        self.affectations = []
        self.student_informations = InternshipStudentInformation.objects.filter(cohort=self.cohort).order_by("?")
        self.person_ids = self.student_informations.values_list("person_id", flat=True)
        self.students = Student.objects.filter(person_id__in=self.person_ids)
        self.internships = Internship.objects.filter(cohort=self.cohort).order_by("position", "name")
        self.mandatory_internships = self.internships.exclude(speciality__isnull=True)
        self.non_mandatory_internships = Internship.objects.filter(cohort=self.cohort, speciality__isnull=True)
        self.specialities = InternshipSpeciality.objects.filter(cohort=self.cohort)
        self.default_organization = Organization.objects.filter(cohort=self.cohort, reference="999").first()
        self.forbidden_organizations = Organization.objects.annotate(reference_length=Length('reference')) \
                .exclude(reference="00").filter(cohort=self.cohort, reference_length=3)
        self.default_speciality = InternshipSpeciality.objects.filter(cohort=self.cohort, acronym="MO").first()
        self.pending_organization = Organization.objects.filter(cohort=self.cohort, reference="604").first()
        self.offers = InternshipOffer.objects.filter(cohort=self.cohort)
        self.periods = Period.objects.extra(select={"period_number": "CAST(substr(name, 2) AS INTEGER)"}) \
                .exclude(name="P12").filter(cohort=self.cohort).order_by("period_number")
        self.offer_ids = self.offers.values_list("id", flat=True)
        self.available_places = PeriodInternshipPlaces.objects.filter(internship_offer_id__in=self.offer_ids).values()
        self.errors_count = 0

    def solve(self):
        self.assign_enrollments_to_students(self.internships)  # 1.
        for internship in self.internships:
            # randomize students for each internship cycle to make sure equity of luck is respected
            self.student_informations = self.student_informations.order_by("?")
            self.assign_priority_choices_to_students(internship)  # 2.
            self.assign_best_offer_for_student_choices(self.student_informations, internship)  # 3.
        self.assign_default_speciality_and_organization_for_students_with_empty_periods(self.default_speciality, self.pending_organization, self.students, self.periods)  # 4.

    @transaction.atomic
    def persist_solution(self):
        InternshipStudentAffectationStat.objects.bulk_create(self.affectations)

    def assign_enrollments_to_students(self, internships):
        """1. Secretaries submit mandatory enrollments for some students, we start by saving all those in the
           solution."""
        enrollments = InternshipEnrollment.objects.filter(internship__in=internships)
        for enrollment in enrollments:
            affectation = self.build_student_affectation(enrollment.place, enrollment.student, enrollment.period,
                                                         enrollment.internship_offer.speciality, "E", True)
            self.update_period_places_for_affectation(affectation)
            self.affectations.append(affectation)

    def assign_priority_choices_to_students(self, internship):
        """2. Some students are priority students, their choices need to be taken into account before the others."""
        priority_student_ids = InternshipChoice.objects.filter(internship=internship, priority=True).values("student").distinct()
        for student_id in priority_student_ids:
            student = Student.objects.get(pk=student_id["student"])
            self.assign_offer_to_student_for_internship(student, internship)

    def assign_best_offer_for_student_choices(self, student_informations, internship):
        """3. Assign the best possible choice to other non-priority students."""
        for student_information in student_informations:
            student = Student.objects.filter(person_id=student_information.person_id).first()
            self.assign_offer_to_student_for_internship(student, internship)

    def assign_default_speciality_and_organization_for_students_with_empty_periods(self, speciality, organization, students, periods):
        """4. When student has empty periods at the end, affect default speciality and organisation. It has to be handled manually."""
        for student in students:
            if self.student_has_empty_periods(student, self.affectations):
                empty_periods = self.student_empty_periods(student, self.affectations)
                affectations = self.build_affectation_for_periods(student, organization, empty_periods, speciality, "I", False)
                self.affectations.extend(affectations)

    def assign_offer_to_student_for_internship(self, student, internship):
        """Assign offer to student for specific internship."""
        choices = InternshipChoice.objects.filter(student=student, internship=internship).order_by("choice")
        affectation = None
        # Mandatory internship
        if internship.speciality and self.student_has_empty_periods(student, self.affectations) and \
                self.student_has_no_current_affectations_for_internship(student, self.affectations, internship):
            affectation = self.assign_choices_to_student(student, choices, internship)
        # Non-mandatory internship
        else:
            if (not internship.speciality) and self.student_has_empty_periods(student, self.affectations):
                affectation = self.assign_choices_to_student(student, choices, internship)

        if affectation:
            self.affectations.extend(affectation)

    def assign_choices_to_student(self, student, choices, internship):
        affectations = []

        # Try to assign choices, from 1 to 4
        for choice in choices:
            periods = self.find_first_student_available_periods_for_internship_choice(student, internship, choice)
            if len(periods) > 0:
                affectations.extend(self.build_affectation_for_periods(student, choice.organization, periods,
                                                                       choice.speciality, choice.choice,
                                                                       choice.priority))
                break

        # None of student choices available? Try to affect outside of choices
        if len(affectations) == 0:
            affectations.extend(self.find_best_affectation_outside_of_choices(student, internship, choices))

        return affectations

    def find_best_affectation_outside_of_choices(self, student, internship, choices):
        student_periods = self.find_student_available_periods_regardless_of_internship(student, internship)

        for grouped_periods in student_periods:
            offer = self.find_best_available_offer_for_internship_periods(internship, choices, grouped_periods)
            if offer:
                return self.build_affectation_for_periods(student, offer.organization, grouped_periods, offer.speciality, "I", False)

        if internship.speciality and student_periods:
            offer = self.find_offer_in_default_organization_for_internship(internship)
            return self.build_affectation_for_periods(student, offer.organization, random.choice(student_periods), offer.speciality, "I", False)
        else:
            return []

    def find_first_student_available_periods_for_internship_choice(self, student, internship, choice):
        """Look for available periods for specific choice."""
        periods_with_places = self.find_available_periods_for_internship_choice(choice)
        return self.first_relevant_periods(student, internship.length_in_periods, periods_with_places)

    def find_available_periods_for_internship_choice(self, choice):
        offers = self.find_offers_for_internship_choice(choice)
        return self.find_available_periods_for_offers(offers)

    def find_available_periods_for_internship(self, internship):
        offers = self.find_offers_for_speciality(internship.speciality)
        return self.find_available_periods_for_offers(offers)

    def all_available_periods(self, student, internship_length, periods):
        """Difference between the authorized periods and the already affected periods from the student."""
        student_affectations = get_student_affectations(student, self.affectations)
        unavailable_periods = get_periods_from_affectations(student_affectations)
        available_periods = difference(periods, unavailable_periods)
        grouped_periods = list(group_periods_by_consecutives(available_periods, length=internship_length))

        return grouped_periods

    def first_relevant_periods(self, student, internship_length, periods):
        """Return relevant period groups for student for internship. Can be groups of 1 or 2 periods."""
        available_periods = self.all_available_periods(student, internship_length, periods)

        if len(available_periods) > 0:
            return random.choice(available_periods)
        else:
            return available_periods

    def find_student_available_periods_regardless_of_internship(self, student, internship):
        periods = []
        if internship.speciality:
            internship_periods = self.periods
            periods = self.all_available_periods(student, internship.length_in_periods, internship_periods)

        if len(periods) == 0:
            internship_periods = self.periods
            periods = self.all_available_periods(student, internship.length_in_periods, internship_periods)
        return periods

    def find_best_available_offer_for_internship_periods(self, internship, choices, periods):
        unavailable_organizations = list(map(lambda choice: choice.organization, choices))
        available_offers = self.find_offers_for_available_organizations(internship.speciality, unavailable_organizations)
        period_places = self.get_available_period_places_for_periods(available_offers, periods)

        if len(period_places) > 0:
            return available_offers.get(pk=period_places[0]["internship_offer_id"])

    def get_available_period_places_for_periods(self, offers, periods):
        available_offer_ids = offers.values_list("id", flat=True)
        period_ids = map_period_ids(periods)
        offers_period_places = get_period_places_for_offer_ids(available_offer_ids, self.available_places)

        if len(periods) == 1:
            period_places_for_period = get_period_places_for_period_ids(period_ids, offers_period_places)
            return sort_period_places(period_places_for_period)
        else:
            for offer_id in available_offer_ids:
                period_places_for_periods = list(map(lambda period: get_period_places_for_offer_id_and_period_id(offer_id, period.id, offers_period_places), periods))
                if all(period_place[0]["number_places"] > 0 for period_place in period_places_for_periods):
                    return flatten(period_places_for_periods)
                else:
                    return []

    def find_available_periods_for_offers(self, offers):
        offer_ids = offers.values_list("id", flat=True)
        period_places_for_offers = get_period_places_for_offer_ids(offer_ids, self.available_places)
        available_period_places = sort_period_places(period_places_for_offers)
        period_ids = get_period_ids_from_period_places(available_period_places)
        return self.periods.filter(pk__in=period_ids).order_by("id")

    def student_has_no_current_affectations_for_internship(self, student, affectations, internship):
        student_affectations = get_student_affectations(student, affectations)
        acronym = internship.speciality.acronym
        internships_with_speciality = self.internships.filter(speciality__acronym=acronym)
        length = internship.length_in_periods
        affectations_with_speciality = list(filter(lambda affectation: affectation.speciality.acronym == acronym, student_affectations))
        periods_affected_to_speciality = list(map(lambda affectation: affectation.period, affectations_with_speciality))
        total_number_of_periods_with_speciality_expected = sum(internship.length_in_periods for internship in internships_with_speciality)
        return len(affectations_with_speciality) + length <= total_number_of_periods_with_speciality_expected

    def student_has_empty_periods(self, student, affectations):
        student_affectations = get_student_affectations(student, affectations)
        return len(student_affectations) < len(self.periods)

    def student_empty_periods(self, student, affectations):
        student_affectations = get_student_affectations(student, affectations)
        unavailable_periods = get_periods_from_affectations(student_affectations)
        return difference(list(self.periods), unavailable_periods)

    #################################################################################################################
    # Affectation factory functions                                                                                 #
    #################################################################################################################

    def build_affectation_for_periods(self, student, organization, periods, speciality, choice, priority):
        affectations = []
        for period in periods:
            affectation = self.build_student_affectation(organization, student, period, speciality, choice, priority)
            self.update_period_places_for_affectation(affectation)
            affectations.append(affectation)
        return affectations

    def update_period_places_for_affectation(self, affectation):
        period = affectation.period
        offer = self.find_offer_for_affectation(affectation)
        period_place = get_period_place_for_offer_and_period(offer, period, self.available_places)
        period_place["number_places"] -= 1
        replace_period_place_in_dictionnary(period_place, self.available_places, period_place["number_places"])

    def build_student_affectation(self, organization, student, period, speciality, choice, priority):
        if priority:
            type_of_internship = "S"  # Social priority student
        else:
            type_of_internship = "N"  # Normal

        if organization.reference == self.default_organization.reference:
            type_of_internship = "X"  # Error
            choice = "X"

        return InternshipStudentAffectationStat(
                organization=organization,
                student=student,
                period=period,
                speciality=speciality,
                choice=choice,
                cost=self.costs[choice],
                type_of_internship=type_of_internship
        )

    #################################################################################################################
    # Finders                                                                                                       #
    #################################################################################################################

    def find_offer_for_affectation(self, affectation):
        return self.offers.filter(organization=affectation.organization,
                speciality__acronym=affectation.speciality.acronym).first()

    def find_offer_in_default_organization_for_internship(self, internship):
        if internship.speciality:
            return self.offers.filter(organization=self.default_organization,
                    speciality__acronym=internship.speciality.acronym).first()
        else:
            return self.offers.filter(organization=self.default_organization,
                    speciality__in=self.specialities).first()

    def find_offers_for_available_organizations(self, speciality, unavailable_organizations):
        if speciality:
            return self.offers.exclude(organization__in=unavailable_organizations). \
                filter(speciality__acronym=speciality.acronym). \
                exclude(organization__in=self.forbidden_organizations)
        else:
            return self.offers.filter(speciality__in=self.specialities). \
                exclude(organization__in=self.forbidden_organizations)

    def find_offers_for_speciality(self, speciality):
        return self.offers.filter(speciality__acronym=speciality.acronym). \
                exclude(organization__in=self.forbidden_organizations)

    def find_offers_for_internship_choice(self, choice):
        return self.offers.filter(speciality__acronym=choice.speciality.acronym, organization=choice.organization)
