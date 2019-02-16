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
import logging
import random
import time
import timeit

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.functions import Length

from base.models.student import Student
from internship import models as mdl
from internship.models.enums import costs
from internship.models.enums.affectation_type import AffectationType
from internship.models.enums.choice_type import ChoiceType
from internship.models.internship import Internship
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_enrollment import InternshipEnrollment
from internship.models.internship_offer import InternshipOffer
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.organization import Organization
from internship.models.period_internship_places import PeriodInternshipPlaces
from internship.utils.assignment.period_place_utils import *
from internship.utils.assignment.period_utils import group_periods_by_consecutives, map_period_ids

logger = logging.getLogger(settings.DEFAULT_LOGGER)

TIMEOUT = 30

class Assignment:
    def __init__(self, cohort):
        self.cohort = cohort
        self.count = 0
        self.total_count = 0
        self.start = 0
        self.stop = 0

        self.students_information = InternshipStudentInformation.objects.filter(cohort=self.cohort)
        self.person_ids = self.students_information.values_list("person_id", flat=True)
        self.students = Student.objects.filter(person_id__in=self.person_ids)

        self.internships = Internship.objects.filter(cohort=self.cohort).order_by("position", "name")
        # self.mandatory_internships = self.internships.exclude(speciality__isnull=True).filter(speciality__acronym__in=["UR", "PE"])
        self.mandatory_internships = self.internships.exclude(speciality__isnull=True)
        self.non_mandatory_internships = self.internships.filter(speciality__isnull=True)

        self.specialities = InternshipSpeciality.objects.filter(cohort=self.cohort)
        self.default_speciality = InternshipSpeciality.objects.filter(cohort=self.cohort, acronym="MO").first()

        self.organization_error = mdl.organization.get_hospital_error(self.cohort)
        self.pending_organization = Organization.objects.filter(cohort=self.cohort, reference="604").first()
        self.forbidden_organizations = Organization.objects.annotate(reference_length=Length('reference')) \
                                                           .exclude(reference="00") \
                                                           .filter(cohort=self.cohort, reference_length=3)

        self.offers = InternshipOffer.objects.filter(cohort=self.cohort)
        self.offer_ids = self.offers.values_list("id", flat=True)
        self.available_places = PeriodInternshipPlaces.objects.filter(internship_offer_id__in=self.offer_ids).values()
        last_period = mdl.period.Period.objects.filter(cohort=self.cohort).order_by('date_end').last()
        self.periods = mdl.period.Period.objects.extra(select={"period_number": "CAST(substr(name, 2) AS INTEGER)"}) \
                                                .exclude(name=last_period.name)\
                                                .filter(cohort=self.cohort).order_by("period_number")

        self.choices = InternshipChoice.objects.filter(internship__cohort=self.cohort).select_related(
            'student', 'internship'
        )

        # As the algorithm progresses, these variables are updated with partial results.
        self.affectations = []
        self.errors_count = 0

    def is_not_published(function):
        def wrapper(self):
            if not self.cohort.is_published:
                return function
            else:
                logger.warning("{} blocked due to execution after publication date.".format(function.__name__))
        return wrapper

    @transaction.atomic
    def persist_solution(self):
        """ All the generated affectations are stored in the database. """
        InternshipStudentAffectationStat.objects.bulk_create(self.affectations)

    def shuffle_students_list(self):
        """ Students are shuffled to make sure equity of luck is respected and then ordered by cost."""
        students_list = list(self.students_information)
        random.shuffle(students_list)
        for student in students_list:
            student.cost = get_student_cost(self.affectations, student)
        return sorted(students_list, key=lambda x: x.cost, reverse=True)

    def solve(self):
        self.start = timeit.default_timer()
        print("Started assignment algorithm.")
        _clean_previous_solution(self.cohort)
        print("Cleaned previous solution.")
        _assign_priority_students(self)
        print("Assigned priority students.")

        for internship in self.mandatory_internships:
            self.students_information = self.shuffle_students_list()
            print("")
            print("Shuffled students for {}.".format(internship.name))
            _assign_students_with_priority_choices(self, internship)
            print("")
            print("Assigned students with priority choices to {}.".format(internship.name))
            _assign_regular_students(self, internship)
            print("")
            print("Assigned regular students to {}.".format(internship.name))

        _assign_non_mandatory_internships(self)
        _balance_assignments(self)
        self.stop = timeit.default_timer()
        print('Time: ', self.stop - self.start)


def _assign_non_mandatory_internships(self):
    self.students_information = self.shuffle_students_list()
    self.total_count = len(self.students_information)
    print("")
    print("Shuffled students for stages au choix.")
    _assign_students_with_priority_choices(self, self.non_mandatory_internships)
    print("")
    print("Assigned students with priority choices to stages au choix.")
    _assign_regular_students(self, self.non_mandatory_internships)
    print("")
    print("Assigned regular students to stages au choix")


def _balance_assignments(self):
    print("Balancing assignments...")
    self.students_information = self.shuffle_students_list()
    favored_students, disadvantaged_students = _update_distinction_between_students(self)

    timeout_start = time.time()

    while len(disadvantaged_students) > 0 and time.time() < timeout_start + TIMEOUT:
        for disadvantaged_student in disadvantaged_students:
            for f_student in favored_students:
                switch = False
                disadvantaged_student_affectations = []
                favored_student_affectations = []

                disadvantaged_student_id = None

                for affectation in self.affectations:
                    if affectation.student.person_id == disadvantaged_student.person_id:
                        disadvantaged_student_affectations.append(affectation)
                        disadvantaged_student_id = affectation.student.id
                    if affectation.student.person_id == f_student.person_id:
                        favored_student_affectations.append(affectation)

                disadvantaged_student_choices = self.choices.filter(student_id=disadvantaged_student_id)

                for d_affectation in disadvantaged_student_affectations:
                    if d_affectation.cost == 10 and d_affectation.choice == "I":
                        d_organization_choices = disadvantaged_student_choices.filter(speciality=d_affectation.speciality).values_list('organization_id', flat=True)
                        for f_affectation in favored_student_affectations:
                            if f_affectation.organization.id in d_organization_choices and f_affectation.period == d_affectation.period and f_affectation.type != AffectationType.PRIORITY:
                                print('switch affectations')
                                timeout_start = time.time()
                                switch = True
                                count = 0
                                for a in self.affectations:
                                    if a.uuid == d_affectation.uuid:
                                        print(vars(a))
                                        a.cost = 0
                                        a.organization_id = f_affectation.organization_id
                                        a.choice = 1
                                        a.type = "1"
                                    if a.uuid == f_affectation.uuid:
                                        print("switch with")
                                        print(vars(a))
                                        a.cost = 10
                                        a.organization_id = d_affectation.organization_id
                                        a.choice = "I"
                                break
                        break
                if switch:
                    break
            if get_student_cost(self.affectations, disadvantaged_student) < 20:
                favored_students, disadvantaged_students = _update_distinction_between_students(self)


def _update_distinction_between_students(self):
    self.students_information = self.shuffle_students_list()
    disadvantaged_students = []
    favored_students = []
    for student in self.students_information:
        if student.cost >= 0 and student.cost < 10:
            favored_students.append(student)
        if student.cost >= 20:
            if student.cost >= 1020:
                student.cost = student.cost - 1000
            disadvantaged_students.append(student)
    return favored_students, disadvantaged_students


def _clean_previous_solution(cohort):
    period_ids = mdl.period.find_by_cohort(cohort).values_list("id", flat=True)
    curr_affectations = mdl.internship_student_affectation_stat.find_non_mandatory_affectations(period_ids=period_ids)
    curr_affectations._raw_delete(curr_affectations.db)


def _assign_priority_students(assignment):
    """ Secretaries submit mandatory enrollments for some students, we start by saving all those in the solution."""
    enrollments = InternshipEnrollment.objects.filter(internship__in=assignment.internships)
    for enrollment in enrollments:
        affectation = _build_prioritary_affectation(enrollment)
        decrement_places_available(assignment, affectation)
        assignment.affectations.append(affectation)


def _assign_students_with_priority_choices(assignment, internship):
    assignment.count = 0
    """ Some students are priority students, their choices need to be taken into account before the others."""
    students = mdl.internship_choice.find_students_with_priority_choices(internship)
    assignment.total_count = len(students)
    for student in students:
        _assign_student(assignment, student, internship)


def _assign_regular_students(assignment, internship):
    assignment.count = 0
    """ Assign the best possible choice to other non-priority students."""
    students = mdl.internship_choice.find_students_with_regular_choices(internship)
    assignment.total_count = len(students)
    for student in students:
        _assign_student(assignment, student, internship)


def assign_students_with_empty_periods(assignment):
    """ When student has empty periods at the end, affect default speciality and organisation. It has to be
        handled manually."""
    for student in assignment.students:
        if student_not_fully_assigned(assignment, student):
            empty_periods = student_empty_periods(assignment, student)
            affectations = build_affectation_for_periods(assignment, student, assignment.pending_organization,
                                                         empty_periods, assignment.default_speciality,
                                                         ChoiceType.IMPOSED.value,
                                                         False, None)
            assignment.affectations.extend(affectations)


def _assign_student(assignment, student, internship):
    assignment.count += 1
    print("\rStudent " + str(assignment.count) + " of " + str(assignment.total_count), end="", flush=True)
    """ Assign offer to student for specific internship."""
    choices = assignment.choices.filter(student=student, internship=internship).order_by("choice")

    affectations = None

    if student_not_fully_assigned(assignment, student):
        if hasattr(internship, 'speciality'):
            # Deal with mandatory internship
            if internship.speciality and student_has_no_affectations_for_internship(assignment, student, internship):
                affectations = assign_choices_to_student(assignment, student, choices, internship)
        # Deal with internship at choice
        else:
            choices = assignment.choices.filter(student=student, internship__in=internship).order_by(
                "internship__name",
                "choice"
            )
            affectations = assign_choices_to_student(assignment, student, choices, internship)

        if affectations:
            assignment.affectations.extend(affectations)
        # print("Student {} affected to {}".format(student, internship))


def assign_choices_to_student(assignment, student, choices, internship):
    affectations = []

    # Try to assign choices, from 1 to 4
    for choice in choices:
        if not hasattr(internship, 'speciality'):
            affecs = assignment.affectations
            affecs = [a for a in affecs if a.organization.reference == choice.organization.reference and
                                           a.speciality == choice.speciality and
                                           a.student == student and
                                           a.choice == ChoiceType.PRIORITY.value]
            if len(affecs) > 0:
                continue

        periods = find_first_student_available_periods_for_internship_choice(assignment, student, internship, choice)
        if len(periods) > 0:
            affectations.extend(build_affectation_for_periods(assignment, student, choice.organization, periods,
                                                              choice.speciality, choice.choice, choice.priority,
                                                              choice.internship))
            break

    # None of student choices available? Try to affect outside of choices
    if len(affectations) == 0:
        affectations.extend(find_best_affectation_outside_of_choices(assignment, student, internship, choices))

    return affectations


def find_best_affectation_outside_of_choices(assignment, student, internship, choices):
    if hasattr(internship, 'speciality'):
        student_periods = all_available_periods(assignment, student, internship.length_in_periods, assignment.periods)
    else:
        student_periods = all_available_periods(assignment, student, 1, assignment.periods)

    for grouped_periods in student_periods:
        offer = find_best_available_offer_for_internship_periods(assignment, internship, choices, grouped_periods)
        if offer:
            if hasattr(internship, 'speciality'):
                return build_affectation_for_periods(assignment, student, offer.organization, grouped_periods,
                                                     offer.speciality, ChoiceType.IMPOSED.value, False, internship)
            else:
                return build_affectation_for_periods(assignment, student, offer.organization, grouped_periods,
                                                     offer.speciality, ChoiceType.IMPOSED.value, False, None)

    if hasattr(internship, 'speciality') and student_periods:
        offer = find_offer_in_organization_error(assignment, internship)
        print("\rError: {}".format(offer))
        return build_affectation_for_periods(assignment, student, offer.organization, random.choice(student_periods),
                                             offer.speciality, ChoiceType.IMPOSED.value, False, internship)
    else:
        return []


def find_first_student_available_periods_for_internship_choice(assignment, student, internship, choice):
    """ Look for available periods for specific choice."""
    periods_with_places = find_available_periods_for_internship_choice(assignment, choice)
    if hasattr(internship, 'speciality'):
        return first_relevant_periods(assignment, student, internship.length_in_periods, periods_with_places)
    else:
        return first_relevant_periods(assignment, student, 1, periods_with_places)


def find_available_periods_for_internship_choice(assignment, choice):
    offers = find_offers_for_internship_choice(assignment, choice)
    return find_available_periods_for_offers(assignment, offers)


def first_relevant_periods(assignment, student, internship_length, periods):
    """ Return relevant period groups for student for internship. Can be groups of 1 or 2 periods."""
    available_periods = all_available_periods(assignment, student, internship_length, periods)

    if len(available_periods) > 0:
        return random.choice(available_periods)
    else:
        return available_periods


def all_available_periods(assignment, student, internship_length, periods):
    """ Difference between the authorized periods and the already affected periods from the student."""
    student_affectations = get_student_affectations(student, assignment.affectations)
    unavailable_periods = get_periods_from_affectations(student_affectations)
    available_periods = difference(periods, unavailable_periods)
    return list(group_periods_by_consecutives(available_periods, length=internship_length))


def find_best_available_offer_for_internship_periods(assignment, internship, choices, periods):
    unavailable_organizations = list(map(lambda choice: choice.organization, choices))
    if hasattr(internship, 'speciality'):
        speciality = internship.speciality
    else:
        speciality = None
    available_offers = offers_for_available_organizations(assignment, speciality, unavailable_organizations)
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
            if all(period_place and period_place[0]["number_places"] > 0 for period_place in period_places_for_periods):
                return flatten(period_places_for_periods)
            else:
                return []


def find_available_periods_for_offers(assignment, offers):
    offer_ids = offers.values_list("id", flat=True)
    period_places_for_offers = get_period_places_for_offer_ids(offer_ids, assignment.available_places)
    available_period_places = sort_period_places(period_places_for_offers)
    period_ids = get_period_ids_from_period_places(available_period_places)
    return assignment.periods.filter(pk__in=period_ids).order_by("id")


def student_has_no_affectations_for_internship(assignment, student, internship):
    # Take all affectations of the student.
    student_affectations = get_student_affectations(student, assignment.affectations)
    # Take only the affectations with the same specialty of the internship.
    affectations_with_speciality = list(filter(lambda affectation: affectation.speciality == internship.speciality,
                                               student_affectations))
    # Take only the affectations whose internship does have a specialty.
    affectations_with_speciality = list(filter(lambda affectation: affectation.internship.speciality is not None,
                                               affectations_with_speciality))
    # Take other internships with the same specialty.
    internships_with_speciality = assignment.internships.filter(speciality=internship.speciality)
    length = internship.length_in_periods
    total_number_of_periods_with_speciality_expected = sum(internship.length_in_periods for internship in
                                                           internships_with_speciality)
    return len(affectations_with_speciality) + length <= total_number_of_periods_with_speciality_expected


def student_not_fully_assigned(assignment, student):
    # student_affectations = get_student_affectations(student, assignment.affectations)
    # return len(student_affectations) < len(assignment.periods)
    return True


def student_empty_periods(assignment, student):
    student_affectations = get_student_affectations(student, assignment.affectations)
    unavailable_periods = get_periods_from_affectations(student_affectations)
    return difference(list(assignment.periods), unavailable_periods)


def build_affectation_for_periods(assignment, student, organization, periods, speciality, choice, priority, internship):
    affectations = []
    for period in periods:
        affectation = _build_regular_affectation(assignment, organization, student, period, speciality, choice,
                                                 priority, internship)
        decrement_places_available(assignment, affectation)
        affectations.append(affectation)
    return affectations


def decrement_places_available(assignment, affectation):
    try:
        offer = assignment.offers.get(organization=affectation.organization, speciality=affectation.speciality)
        period_place = get_period_place_for_offer_and_period(offer, affectation.period, assignment.available_places)
        if period_place:
            period_place['number_places'] -= 1
            assignment.available_places = replace_period_place_in_dictionnary(period_place, assignment.available_places)
    except ObjectDoesNotExist:
        return


def _build_prioritary_affectation(enrollment):
    return InternshipStudentAffectationStat(organization=enrollment.place, student=enrollment.student,
                                            period=enrollment.period, speciality=enrollment.internship_offer.speciality,
                                            internship=enrollment.internship, choice=ChoiceType.PRIORITY.value,
                                            cost=costs.COSTS[ChoiceType.PRIORITY.value],
                                            type=AffectationType.PRIORITY.value)


def _build_regular_affectation(assignment, organization, student, period, speciality, choice, priority, internship):
    type_affectation = AffectationType.PRIORITY.value if priority else AffectationType.NORMAL.value

    if organization.reference == assignment.organization_error.reference:
        type_affectation = AffectationType.ERROR.value
        choice = ChoiceType.ERROR.value
    else:
        choice = str(choice)

    return InternshipStudentAffectationStat(organization=organization, student=student, period=period,
                                            speciality=speciality, internship=internship, choice=choice,
                                            cost=costs.COSTS[choice], type=type_affectation)


def find_offer_in_organization_error(assignment, internship):
    # Mandatory internship
    if internship.speciality:
        return assignment.offers.get(organization=assignment.organization_error,
                                     speciality=internship.speciality)
    # Chosen internship
    else:
        return assignment.offers.get(organization=assignment.organization_error,
                                     speciality__in=assignment.specialities)


def offers_for_available_organizations(assignment, speciality, unavailable_organizations):
    if speciality:
        return assignment.offers.exclude(organization__in=unavailable_organizations)\
                                .filter(speciality=speciality)\
                                .exclude(organization__in=assignment.forbidden_organizations)
    else:
        return assignment.offers.filter(speciality__in=assignment.specialities)\
                                .exclude(organization__in=assignment.forbidden_organizations)


def find_offers_for_speciality(assignment, speciality):
    return assignment.offers.filter(speciality=speciality).exclude(organization__in=assignment.forbidden_organizations)


def find_offers_for_internship_choice(assignment, choice):
    return assignment.offers.filter(speciality=choice.speciality, organization=choice.organization)


def get_student_affectations(student, affectations):
    """ From a list of affectations, it returns a new list containing only the affectations related to the student. """
    return list(filter(lambda affectation: affectation.student == student, affectations))


def difference(first_list, second_list):
    return [item for item in first_list if item not in second_list]


def flatten(list_of_lists):
    return [y for x in list_of_lists for y in x]


def get_periods_from_affectations(affectations):
    return list(map(lambda affectation: affectation.period, affectations))


def get_student_cost(affectations, student):
    student_affectations_cost = [a.cost for a in affectations if a.student.person_id == student.person_id]
    return sum(student_affectations_cost)
