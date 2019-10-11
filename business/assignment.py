##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from copy import copy

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.functions import Length

from base.models.student import Student
from internship import models as mdl
from internship.models.enums import costs
from internship.models.enums.affectation_type import AffectationType
from internship.models.enums.choice_type import ChoiceType
from internship.models.enums.costs import Costs
from internship.models.internship import Internship
from internship.models.internship_choice import InternshipChoice, find_students_with_priority_choices
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


class Assignment:
    TIMEOUT = 60
    MAX_ALLOWED_IMPOSED = 2

    def __init__(self, cohort):
        self.cohort = cohort
        self.count = 0
        self.total_count = 0
        self.start = 0
        self.stop = 0
        self.last_switch = []
        self.internship_count = 0

        self.students_information = InternshipStudentInformation.objects.filter(cohort=self.cohort)
        self.person_ids = self.students_information.values_list("person_id", flat=True)
        self.students = Student.objects.filter(person_id__in=self.person_ids)

        self.internships = Internship.objects.filter(cohort=self.cohort).order_by("position", "name")
        self.prioritary_students_person_ids = find_students_with_priority_choices(
            self.internships
        ).values_list('person__id', flat=True)

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

    @transaction.atomic
    def persist_solution(self):
        """ All the generated affectations are stored in the database. """
        InternshipStudentAffectationStat.objects.bulk_create(self.affectations)

    def shuffle_students_list(self):
        """ Students are shuffled to make sure equity of luck is respected and then ordered by cost after first iter."""
        students_list = list(self.students_information)
        random.shuffle(students_list)
        for student in students_list:
            student.cost = get_student_cost(self.affectations, student)
        if self.internship_count > 0:
            return sorted(students_list, key=lambda x: x.cost, reverse=True)
        else:
            return students_list

    def solve(self):
        self.start = timeit.default_timer()
        logger.info("Started assignment algorithm.")
        _clean_previous_solution(self.cohort)
        logger.info("Cleaned previous solution.")
        _assign_priority_students(self)
        logger.info("Assigned priority students.")

        for internship in self.mandatory_internships:
            self.students_information = self.shuffle_students_list()
            logger.info("Shuffled students for {}.".format(internship.name))
            _assign_students_with_priority_choices(self, internship)
            logger.info("Assigned students with priority choices to {}.".format(internship.name))
            _assign_regular_students(self, internship)
            logger.info("Assigned regular students to {}.".format(internship.name))
            self.internship_count += 1

        _assign_non_mandatory_internships(self)
        _balance_assignments(self)
        self.stop = timeit.default_timer()
        total_time = self.stop - self.start
        logger.info('Time: {} seconds'.format(total_time))


def _assign_non_mandatory_internships(self):
    self.students_information = self.shuffle_students_list()
    self.total_count = len(self.students_information)
    logger.info("Shuffled students for stages au choix.")
    _assign_students_with_priority_choices(self, self.non_mandatory_internships)
    logger.info("Assigned students with priority choices to stages au choix.")
    _assign_regular_students(self, self.non_mandatory_internships)
    logger.info("Assigned regular students to stages au choix")


def _balance_assignments(self):
    logger.info("Balancing assignments...")
    self.students_information = self.shuffle_students_list()
    favored_students, disadvantaged_students = _update_distinction_between_students(self)
    self.timeout_start = time.time()
    while len(disadvantaged_students) > 0 and time.time() < self.timeout_start + self.TIMEOUT:
        _process_affectations_comparisons(self, favored_students, disadvantaged_students)


def _update_distinction_between_students(self):
    self.students_information = self.shuffle_students_list()
    disadvantaged_students = []
    favored_students = []
    for student in self.students_information:
            if student.cost >= Costs.PRIORITY.value and student.cost < Costs.IMPOSED.value:
                if student.person_id not in self.prioritary_students_person_ids:
                    favored_students.append(student)
            if student.cost >= self.MAX_ALLOWED_IMPOSED * Costs.IMPOSED.value:
                if student.cost >= Costs.ERROR.value + self.MAX_ALLOWED_IMPOSED * Costs.IMPOSED.value:
                    student.cost = student.cost - Costs.ERROR.value
                disadvantaged_students.append(student)
    return favored_students, disadvantaged_students


def _process_affectations_comparisons(self, favored_students, disadvantaged_students):
    for d_student in disadvantaged_students:
        for f_student in favored_students:
            self.switch = False
            disadvantaged_student_affectations = []
            favored_student_affectations = []
            disadvantaged_student_id = _append_affectations(
                self,
                disadvantaged_student_affectations,
                favored_student_affectations,
                d_student,
                f_student
            )
            disadvantaged_student_choices = self.choices.filter(student_id=disadvantaged_student_id)
            _permute_affectations(
                self,
                disadvantaged_student_affectations,
                favored_student_affectations,
                disadvantaged_student_choices,
            )
            if self.switch:
                break
        favored_students, disadvantaged_students = _update_distinction_between_students(self)


def _append_affectations(self, d_student_affectations, f_student_affectations, d_student, f_student):
    disadvantaged_student_id = None
    for affectation in self.affectations:
        if affectation.student.person_id == d_student.person_id and is_mandatory_internship(affectation.internship):
            d_student_affectations.append(affectation)
            disadvantaged_student_id = affectation.student.id
        if affectation.student.person_id == f_student.person_id and is_mandatory_internship(affectation.internship):
            f_student_affectations.append(affectation)
    return disadvantaged_student_id


def _permute_affectations(self, d_student_affectations, f_student_affectations, d_student_choices):
    for d_affectation in d_student_affectations:
        temp_d = copy(d_affectation)
        if _disadvantaged_affectation_is_switchable(d_affectation):
            d_organization_choices = _get_hospital_choices_by_speciality(d_student_choices, d_affectation)
            for f_affectation in f_student_affectations:
                temp_f = copy(f_affectation)
                if _favored_affectation_is_switchable(f_affectation, d_affectation, d_organization_choices):
                    _store_exchanged_affectation_information(self, d_organization_choices, d_affectation, f_affectation,
                                                             temp_f, temp_d)
                    break
            break


def _disadvantaged_affectation_is_switchable(d_affectation):
    return d_affectation.cost == 10 and d_affectation.choice == "I" and d_affectation.type != AffectationType.PRIORITY


def _favored_affectation_is_switchable(f_affectation, d_affectation, d_organization_choices):
    return f_affectation.organization.id in d_organization_choices and f_affectation.period == d_affectation.period\
           and f_affectation.speciality == d_affectation.speciality and f_affectation.type != AffectationType.PRIORITY


def _get_hospital_choices_by_speciality(d_student_choices, d_affectation):
    return list(d_student_choices.filter(speciality=d_affectation.speciality).order_by('choice').values_list(
        'organization_id', flat=True)
    )


def _store_exchanged_affectation_information(self, d_organization_choices, d_aff, f_aff, temp_f, temp_d):
    if temp_d.uuid not in self.last_switch:
        self.timeout_start = time.time()
        self.switch = True
    for a in self.affectations:
        if a.uuid == d_aff.uuid:
            a.organization_id = temp_f.organization_id
            a.organization = temp_f.organization
            a.choice = _get_hospital_choice_type(d_organization_choices, a.organization_id)
            a.cost = a.choice - 1
        if a.uuid == f_aff.uuid:
            a.cost = 10
            a.organization_id = temp_d.organization_id
            a.organization = temp_d.organization
            a.choice = "I"
    self.last_switch.append(temp_f.uuid)


def _get_hospital_choice_type(d_organization_choices, selected_organization_id):
    return d_organization_choices.index(selected_organization_id)+1


def _clean_previous_solution(cohort):
    period_ids = mdl.period.find_by_cohort(cohort).values_list("id", flat=True)
    curr_affectations = InternshipStudentAffectationStat.objects.filter(period__id__in=period_ids). \
        select_related("student", "organization", "speciality")
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


def _assign_student(assignment, student, internship):
    assignment.count += 1
    # print("\rStudent " + str(assignment.count) + " of " + str(assignment.total_count), end="", flush=True)
    """ Assign offer to student for specific internship."""
    choices = assignment.choices.filter(student=student, internship=internship).order_by("choice")

    affectations = None

    if student_not_fully_assigned(assignment, student):
        if is_mandatory_internship(internship):
            # Deal with mandatory internship
            if internship.speciality and student_has_no_affectations_for_internship(assignment, student, internship):
                affectations = assign_choices_to_student(assignment, student, choices, internship)
        # Deal with internship at choice
        else:
            for chosen_internship in internship:
                if affectations is None or affectations == []:
                    last = chosen_internship == list(internship)[:-1]
                    setattr(chosen_internship, 'first', chosen_internship == list(internship)[0])
                    choices = assignment.choices.filter(student=student, internship=chosen_internship).order_by(
                        "choice"
                    )
                    affectations = assign_choices_to_student(assignment, student, choices, chosen_internship, last)
                    # logger.info("{} -- {}".format(student, chosen_internship))

        if affectations:
            assignment.affectations.extend(affectations)
        # logger.info("Student {} affected to {} in period {}".format(student, internship, affectations))


def assign_choices_to_student(assignment, student, choices, internship, last=False):
    affectations = []

    # Try to assign choices, from 1 to 4
    for choice in choices:
        if is_non_mandatory_internship(internship):
            affecs = assignment.affectations
            affecs = [a for a in affecs if a.organization.reference == choice.organization.reference and
                                           a.speciality == choice.speciality and
                                           a.student == student and
                                           a.choice == ChoiceType.PRIORITY.value]
            if len(affecs) > 0:
                continue

        periods = find_first_student_available_periods_for_internship_choice(assignment, student, internship, choice)
        if len(periods) > 0:
            if is_non_mandatory_internship(internship) and not internship.first:
                if not choice.priority and not is_prior_internship(internship, choices):
                    choice.choice = ChoiceType.IMPOSED.value
            affectations.extend(build_affectation_for_periods(assignment, student, choice.organization, periods,
                                                              choice.speciality, choice.choice, choice.priority,
                                                              choice.internship))
            break

    # None of student choices available? Try to affect outside of choices
    if len(affectations) == 0:
        affectations.extend(
            find_best_affectation_outside_of_choices(assignment, student, internship, choices, last)
        )

    return affectations


def find_best_affectation_outside_of_choices(assignment, student, internship, choices, last):
    if not is_prior_internship(internship, choices):
        student_periods = get_student_periods(assignment, student, internship)
        for grouped_periods in student_periods:
            offer = find_best_available_offer_for_internship_periods(assignment, internship, choices,
                                                                     grouped_periods, last)
            if offer:
                return build_affectation_for_periods(assignment, student, offer.organization, grouped_periods,
                                                     offer.speciality, ChoiceType.IMPOSED.value, False, internship)
        if is_mandatory_internship(internship) and student_periods:
            return affect_hospital_error(assignment, student, internship, student_periods)
        else:
            return []
    else:
        student_periods = get_student_periods(assignment, student, internship)
        speciality = choices.first().speciality
        return affect_hospital_error(assignment, student, internship, student_periods, speciality)


def affect_hospital_error(assignment, student, internship, periods, speciality=None):
    offer = find_offer_in_organization_error(assignment, internship)
    if speciality is None:
        speciality = offer.speciality
    logger.info("\rError: {}".format(speciality))
    return build_affectation_for_periods(assignment, student, offer.organization, random.choice(periods),
                                         speciality, ChoiceType.IMPOSED.value, False, internship)


def get_student_periods(assignment, student, internship):
    if is_mandatory_internship(internship):
        student_periods = all_available_periods(assignment, student, internship.length_in_periods, assignment.periods)
    else:
        student_periods = all_available_periods(assignment, student, 1, assignment.periods)
    random.shuffle(student_periods)
    return student_periods


def find_first_student_available_periods_for_internship_choice(assignment, student, internship, choice):
    """ Look for available periods for specific choice."""
    periods_with_places = find_available_periods_for_internship_choice(assignment, choice)
    if is_mandatory_internship(internship):
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
    return list(group_periods_by_consecutives(available_periods, leng=internship_length))


def find_best_available_offer_for_internship_periods(assignment, internship, choices, periods, last=False):
    unavailable_organizations = list(map(lambda choice: choice.organization, choices))
    if is_mandatory_internship(internship):
        speciality = internship.speciality
    else:
        if hasattr(choices.first(), 'speciality'):
            speciality = choices.first().speciality
        else:
            speciality = None
    if speciality is not None or last:
        available_offers = offers_for_available_organizations(assignment, speciality, unavailable_organizations)
        period_places = get_available_period_places_for_periods(assignment, available_offers, periods)

        if len(period_places) > 0:
            return available_offers.get(
                pk=period_places[random.randint(0, len(period_places)-1)]["internship_offer_id"]
            )


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
    return assignment.periods.filter(pk__in=period_ids).order_by("?")


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
    student_affectations = get_student_affectations(student, assignment.affectations)
    return len(student_affectations) < len(assignment.periods)


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
        return assignment.offers.filter(organization=assignment.organization_error, cohort=assignment.cohort).first()


def offers_for_available_organizations(assignment, speciality, unavailable_organizations):
    if speciality:
        return assignment.offers.exclude(organization__in=unavailable_organizations)\
                                .filter(speciality=speciality)\
                                .exclude(organization__in=assignment.forbidden_organizations)
    else:
        return assignment.offers.filter(speciality__in=assignment.specialities)\
                                .exclude(organization__in=assignment.forbidden_organizations)


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


def is_mandatory_internship(internship):
    return not is_non_mandatory_internship(internship)


def is_non_mandatory_internship(internship):
    return not hasattr(internship, 'speciality') or internship.speciality is None


def is_prior_internship(internship, choices):
    for choice in choices:
        if choice.internship == internship and choice.priority:
            return True
