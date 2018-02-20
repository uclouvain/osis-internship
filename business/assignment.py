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
from internship import models as mdl
from internship.models.enums.affectation_type import AffectationType
from internship.models.enums.choice_type import ChoiceType
from internship.models.period_internship_places import PeriodInternshipPlaces
from internship.utils.assignment.period_place_utils import *
from internship.utils.assignment.period_utils import group_periods_by_consecutives, map_period_ids


COSTS = {1: 0, 2: 1, 3: 2, 4: 3, 'E': 0, 'I': 10, 'X': 1000}


class Assignment:
    def __init__(self, cohort):
        self.cohort = cohort

        self.student_informations = InternshipStudentInformation.objects.filter(cohort=self.cohort)
        self.person_ids = self.student_informations.values_list("person_id", flat=True)
        self.students = Student.objects.filter(person_id__in=self.person_ids)

        self.internships = Internship.objects.filter(cohort=self.cohort).order_by("position", "name")
        self.mandatory_internships = self.internships.exclude(speciality__isnull=True)

        self.specialities = InternshipSpeciality.objects.filter(cohort=self.cohort)
        self.default_speciality = InternshipSpeciality.objects.filter(cohort=self.cohort, acronym="MO").first()

        self.organization_error = Organization.objects.filter(cohort=self.cohort, reference="999").first()
        self.pending_organization = Organization.objects.filter(cohort=self.cohort, reference="604").first()
        self.forbidden_organizations = Organization.objects.annotate(reference_length=Length('reference')) \
                                                           .exclude(reference="00") \
                                                           .filter(cohort=self.cohort, reference_length=3)

        self.offers = InternshipOffer.objects.filter(cohort=self.cohort)
        self.offer_ids = self.offers.values_list("id", flat=True)
        self.available_places = PeriodInternshipPlaces.objects.filter(internship_offer_id__in=self.offer_ids).values()

        self.periods = mdl.period.Period.objects.extra(select={"period_number": "CAST(substr(name, 2) AS INTEGER)"}) \
                                                .exclude(name="P12")\
                                                .filter(cohort=self.cohort).order_by("period_number")

        self.affectations = []
        self.errors_count = 0

    @transaction.atomic
    def persist_solution(self):
        InternshipStudentAffectationStat.objects.bulk_create(self.affectations)

    def solve(self):
        clean_previous_solution(self.cohort)
        assign_prioritary_students(self)

        for internship in self.internships:
            # randomize students for each internship cycle to make sure equity of luck is respected.
            self.student_informations = self.student_informations.order_by("?")
            assign_priority_choices_to_students(self, internship)
            assign_best_offer_for_student_choices(self, internship)
            print(internship.name)

        assign_students_with_empty_periods(self)


def clean_previous_solution(cohort):
    period_ids = mdl.period.find_by_cohort(cohort).values_list("id", flat=True)
    curr_affectations = mdl.internship_student_affectation_stat.find_non_mandatory_affectations(period_ids=period_ids)
    curr_affectations._raw_delete(curr_affectations.db)  # Is it really a lot better than .delete() ?


def assign_prioritary_students(assignment):
    """1. Secretaries submit mandatory enrollments for some students, we start by saving all those in the
       solution."""
    enrollments = InternshipEnrollment.objects.filter(internship__in=assignment.internships)
    for enrollment in enrollments:
        affectation = build_student_affectation(assignment, enrollment.place, enrollment.student, enrollment.period,
                                                enrollment.internship_offer.speciality, ChoiceType.PRIORITY.value, True)
        update_period_places_for_affectation(assignment, affectation)
        assignment.affectations.append(affectation)


def assign_priority_choices_to_students(assignment, internship):
    """2. Some students are priority students, their choices need to be taken into account before the others."""
    priority_student_ids = InternshipChoice.objects.filter(internship=internship,
                                                           priority=True).values("student").distinct()
    for student_id in priority_student_ids:
        student = Student.objects.get(pk=student_id["student"])
        assign_offer_to_student_for_internship(assignment, student, internship)


def assign_best_offer_for_student_choices(assignment, internship):
    """3. Assign the best possible choice to other non-priority students."""
    for student_information in assignment.student_informations:
        student = Student.objects.filter(person_id=student_information.person_id).first()
        assign_offer_to_student_for_internship(assignment, student, internship)


def assign_students_with_empty_periods(assignment):
    """4. When student has empty periods at the end, affect default speciality and organisation. It has to be
          handled manually."""
    for student in assignment.students:
        if student_has_empty_periods(assignment, student):
            empty_periods = student_empty_periods(assignment, student)
            affectations = build_affectation_for_periods(assignment, student, assignment.pending_organization,
                                                         empty_periods, assignment.speciality, ChoiceType.IMPOSED.value, False)
            assignment.affectations.extend(affectations)


def assign_offer_to_student_for_internship(assignment, student, internship):
    """Assign offer to student for specific internship."""
    choices = InternshipChoice.objects.filter(student=student, internship=internship).order_by("choice")
    affectation = None
    # Mandatory internship
    if internship.speciality and student_has_empty_periods(assignment, student) and \
            student_has_no_current_affectations_for_internship(assignment, student, internship):
        affectation = assign_choices_to_student(assignment, student, choices, internship)
    # Non-mandatory internship
    else:
        if (not internship.speciality) and student_has_empty_periods(assignment, student):
            affectation = assign_choices_to_student(assignment, student, choices, internship)

    if affectation:
        assignment.affectations.extend(affectation)


def assign_choices_to_student(assignment, student, choices, internship):
    affectations = []

    # Try to assign choices, from 1 to 4
    for choice in choices:
        periods = find_first_student_available_periods_for_internship_choice(assignment, student, internship, choice)
        if len(periods) > 0:
            affectations.extend(build_affectation_for_periods(assignment, student, choice.organization, periods,
                                                              choice.speciality, choice.choice, choice.priority))
            break

    # None of student choices available? Try to affect outside of choices
    if len(affectations) == 0:
        affectations.extend(find_best_affectation_outside_of_choices(assignment, student, internship, choices))

    return affectations


def find_best_affectation_outside_of_choices(assignment, student, internship, choices):
    student_periods = all_available_periods(assignment, student, internship.length_in_periods, assignment.periods)

    for grouped_periods in student_periods:
        offer = find_best_available_offer_for_internship_periods(assignment, internship, choices, grouped_periods)
        if offer:
            return build_affectation_for_periods(assignment, student, offer.organization, grouped_periods,
                                                 offer.speciality, ChoiceType.IMPOSED.value, False)

    if internship.speciality and student_periods:
        offer = find_offer_in_organization_error(assignment, internship)
        return build_affectation_for_periods(assignment, student, offer.organization, random.choice(student_periods),
                                             offer.speciality, ChoiceType.IMPOSED.value, False)
    else:
        return []


def find_first_student_available_periods_for_internship_choice(assignment, student, internship, choice):
    """Look for available periods for specific choice."""
    periods_with_places = find_available_periods_for_internship_choice(assignment, choice)
    return first_relevant_periods(assignment, student, internship.length_in_periods, periods_with_places)


def find_available_periods_for_internship_choice(assignment, choice):
    offers = find_offers_for_internship_choice(assignment, choice)
    return find_available_periods_for_offers(assignment, offers)


def first_relevant_periods(assignment, student, internship_length, periods):
    """Return relevant period groups for student for internship. Can be groups of 1 or 2 periods."""
    available_periods = all_available_periods(assignment, student, internship_length, periods)

    if len(available_periods) > 0:
        return random.choice(available_periods)
    else:
        return available_periods


def all_available_periods(assignment, student, internship_length, periods):
    """Difference between the authorized periods and the already affected periods from the student."""
    student_affectations = get_student_affectations(student, assignment.affectations)
    unavailable_periods = get_periods_from_affectations(student_affectations)
    available_periods = difference(periods, unavailable_periods)
    return list(group_periods_by_consecutives(available_periods, length=internship_length))


def find_best_available_offer_for_internship_periods(assignment, internship, choices, periods):
    unavailable_organizations = list(map(lambda choice: choice.organization, choices))
    available_offers = offers_for_available_organizations(assignment, internship.speciality, unavailable_organizations)
    period_places = get_available_period_places_for_periods(assignment, available_offers, periods)

    if len(period_places) > 0:
        return available_offers.get(pk=period_places[0]["internship_offer_id"])


def get_available_period_places_for_periods(assignment, offers, periods):
    available_offer_ids = offers.values_list("id", flat=True)
    period_ids = map_period_ids(periods)
    offers_period_places = get_period_places_for_offer_ids(available_offer_ids, assignment.available_places)

    if len(periods) == 1:
        period_places_for_period = get_period_places_for_period_ids(period_ids, offers_period_places)
        return sort_period_places(period_places_for_period)
    else:
        for offer_id in available_offer_ids:
            period_places_for_periods = list(map(lambda period: get_period_places_for_offer_id_and_period_id(
                offer_id, period.id, offers_period_places), periods))
            if all(period_place[0]["number_places"] > 0 for period_place in period_places_for_periods):
                return flatten(period_places_for_periods)
            else:
                return []


def find_available_periods_for_offers(assignment, offers):
    offer_ids = offers.values_list("id", flat=True)
    period_places_for_offers = get_period_places_for_offer_ids(offer_ids, assignment.available_places)
    available_period_places = sort_period_places(period_places_for_offers)
    period_ids = get_period_ids_from_period_places(available_period_places)
    return assignment.periods.filter(pk__in=period_ids).order_by("id")


def student_has_no_current_affectations_for_internship(assignment, student, internship):
    student_affectations = get_student_affectations(student, assignment.affectations)
    acronym = internship.speciality.acronym
    internships_with_speciality = assignment.internships.filter(speciality__acronym=acronym)
    length = internship.length_in_periods
    affectations_with_speciality = list(filter(lambda affectation: affectation.speciality.acronym == acronym,
                                               student_affectations))
    total_number_of_periods_with_speciality_expected = sum(internship.length_in_periods for internship in
                                                           internships_with_speciality)
    return len(affectations_with_speciality) + length <= total_number_of_periods_with_speciality_expected


def student_has_empty_periods(assignment, student):
    student_affectations = get_student_affectations(student, assignment.affectations)
    return len(student_affectations) < len(assignment.periods)


def student_empty_periods(assignment, student):
    student_affectations = get_student_affectations(student, assignment.affectations)
    unavailable_periods = get_periods_from_affectations(student_affectations)
    return difference(list(assignment.periods), unavailable_periods)

#################################################################################################################
# Affectation factory functions                                                                                 #
#################################################################################################################

def build_affectation_for_periods(assignment, student, organization, periods, speciality, choice, priority):
    affectations = []
    for period in periods:
        affectation = build_student_affectation(assignment, organization, student, period, speciality, choice, priority)
        update_period_places_for_affectation(assignment, affectation)
        affectations.append(affectation)
    return affectations


def update_period_places_for_affectation(assignment, affectation):
    period = affectation.period
    offer = find_offer_for_affectation(assignment, affectation)
    period_place = get_period_place_for_offer_and_period(offer, period, assignment.available_places)
    period_place["number_places"] -= 1
    assignment.available_places = replace_period_place_in_dictionnary(period_place, assignment.available_places,
                                                                      period_place["number_places"])


def build_student_affectation(assignment, organization, student, period, speciality, choice, priority):
    type_affectation = AffectationType.PRIORITY.value if priority else AffectationType.NORMAL.value

    if organization.reference == assignment.organization_error.reference:
        type_affectation = AffectationType.ERROR.value
        choice = ChoiceType.ERROR.value

    return InternshipStudentAffectationStat(organization=organization, student=student, period=period,
                                            speciality=speciality, choice=choice, cost=COSTS[choice],
                                            type_of_internship=type_affectation)

#################################################################################################################
# Finders                                                                                                       #
#################################################################################################################

def find_offer_for_affectation(assignment, affectation):
    return assignment.offers.get(organization=affectation.organization,
                                 speciality=affectation.speciality)


def find_offer_in_organization_error(assignment, internship):
    if internship.speciality:
        return assignment.offers.get(organization=assignment.organization_error,
                                     speciality__acronym=internship.speciality.acronym)
    else:
        return assignment.offers.get(organization=assignment.organization_error,
                                     speciality__in=assignment.specialities)


def offers_for_available_organizations(assignment, speciality, unavailable_organizations):
    if speciality:
        return assignment.offers.exclude(organization__in=unavailable_organizations)\
                                .filter(speciality__acronym=speciality.acronym)\
                                .exclude(organization__in=assignment.forbidden_organizations)
    else:
        return assignment.offers.filter(speciality__in=assignment.specialities)\
                                .exclude(organization__in=assignment.forbidden_organizations)


def find_offers_for_speciality(assignment, speciality):
    return assignment.offers.filter(speciality__acronym=speciality.acronym)\
                            .exclude(organization__in=assignment.forbidden_organizations)


def find_offers_for_internship_choice(assignment, choice):
    return assignment.offers.filter(speciality__acronym=choice.speciality.acronym, organization=choice.organization)


def get_student_affectations(student, affectations):
    return list(filter(lambda affectation: affectation.student_id == student.id, affectations))


def difference(first_list, second_list):
    return [item for item in first_list if item not in second_list]


def flatten(list_of_lists):
    return [y for x in list_of_lists for y in x]


def get_periods_from_affectations(affectations):
    return list(map(lambda affectation: affectation.period, affectations))
