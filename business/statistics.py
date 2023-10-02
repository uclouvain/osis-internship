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
import re
from collections import OrderedDict
from collections import defaultdict
from operator import itemgetter

from base.models.student import Student
from internship import models
from internship.models import period_internship_places
from internship.models.enums.affectation_type import AffectationType
from internship.models.enums.choice_type import ChoiceType
from internship.models.internship import Internship
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.period import get_assignable_periods, get_effective_periods, get_subcohorts_periods
from statistics import mean, stdev

HOSPITAL_ERROR = 999  # Reference of the hospital "erreur"


def compute_stats(cohort, sol):
    """
    Compute the statistics of the solution
    """
    stats = {}
    total_cost = 0
    consecutive_month = 0
    imposed_choices = 0
    erasmus = 0
    hospital_error_count = 0
    mean_array = []
    distance_mean = []
    others_students = set()
    others_specialities = {}
    others_specialities_students = {}

    # Retrieve all specialities
    specialities = InternshipSpeciality.objects.filter(cohort=cohort).select_related()
    if cohort.is_parent:
        specialities = InternshipSpeciality.objects.filter(cohort__in=cohort.subcohorts.all())
        for subcohort in cohort.subcohorts.all():
            others_specialities[subcohort.name] = {}
            others_specialities_students[subcohort.name] = {}
    else:
        others_specialities[cohort.name] = {}
        others_specialities_students[cohort.name] = {}

    # Initialize the others_specialities and others_specialities_students
    for speciality in specialities:
        others_specialities[speciality.cohort.name][speciality] = 0
        others_specialities_students[speciality.cohort.name][speciality] = set()

    # Total number of internships
    first, second, third, fourth = 0, 0, 0, 0

    # Number of internships for each category
    # n = normal, s = social
    first_n, second_n, third_n, fourth_n = 0, 0, 0, 0
    first_s, second_s, third_s, fourth_s = 0, 0, 0, 0

    non_mandatory_internships_stats = {
        'count': 0,
    }
    # Iterate all students
    for student, periods in sol.items():
        # Cost of the student solution
        cost = periods['score']
        # Add cost of the student to the total cost
        total_cost += cost
        # Add the cost of the student to the mean_array, this array is used
        # to find the standard deviation with command "stdev"
        mean_array.append(cost)
        # Iterate over all periods of the student
        for period, affectation in periods.items():
            if period != 'score' and affectation is not None:
                if affectation.internship is not None and affectation.internship.speciality is None:
                    if affectation.internship.name not in non_mandatory_internships_stats.keys():
                        non_mandatory_internships_stats.update({affectation.internship.name: {'count': 0, 'perc': 0}})
                    non_mandatory_internships_stats[affectation.internship.name]['count'] += 1
                    non_mandatory_internships_stats[affectation.internship.name]['perc'] += 1
                    non_mandatory_internships_stats['count'] += 1
                # First choice
                if affectation.choice == ChoiceType.FIRST_CHOICE.value:
                    # Increment the number of total first choices
                    first += 1
                    # Increment the number of total normal first choices
                    if affectation.type == AffectationType.NORMAL.value:
                        first_n += 1
                    # Increment the number of total social first choices
                    if affectation.type == AffectationType.PRIORITY.value:
                        first_s += 1
                # Second choice
                elif affectation.choice == ChoiceType.SECOND_CHOICE.value:
                    second += 1
                    if affectation.type == AffectationType.NORMAL.value:
                        second_n += 1
                    if affectation.type == AffectationType.PRIORITY.value:
                        second_s += 1
                # Third choice
                elif affectation.choice == ChoiceType.THIRD_CHOICE.value:
                    third += 1
                    if affectation.type == AffectationType.NORMAL.value:
                        third_n += 1
                    if affectation.type == AffectationType.PRIORITY.value:
                        third_s += 1
                # Fourth choice
                elif affectation.choice == ChoiceType.FORTH_CHOICE.value:
                    fourth += 1
                    if affectation.type == AffectationType.NORMAL.value:
                        fourth_n += 1
                    if affectation.type == AffectationType.PRIORITY.value:
                        fourth_s += 1
                # Erasmus
                elif affectation.choice == ChoiceType.PRIORITY.value:  # Erasmus
                    erasmus += 1
                # Imposed choice
                elif affectation.choice == ChoiceType.IMPOSED.value:  # Imposed hospital
                    # Retrieve the addresses of the hospital and the student
                    # Increment total of imposed choices
                    imposed_choices += 1
                    # Add the student to the set "others_students",
                    # we will use this set to find the number of students
                    # with imposed choices
                    others_students.add(student)
                    others_specialities[affectation.speciality.cohort.name][affectation.speciality] += 1
                    others_specialities_students[affectation.speciality.cohort.name][affectation.speciality].add(student)
                # Hostpital error
                if int(affectation.organization.reference) == HOSPITAL_ERROR:
                    hospital_error_count += 1
                consecutive_month += affectation.consecutive_month
    # Total number of students
    number_of_students = len(sol)
    # Total number of internships
    total_internships = number_of_students * 8

    # Get number of students socio
    students_socio = set()
    for speciality, students in _get_student_mandatory_choices(cohort, True).items():
        for choices in students:
            students_socio.add(choices[0].student.id)
    internships = models.internship.Internship.objects.filter(cohort=cohort)
    socio = len(models.internship_choice.InternshipChoice.
                objects.filter(internship__in=internships, priority=True).distinct('student').values('student'))

    total_n_internships = first_n + second_n + third_n + fourth_n + imposed_choices
    total_s_internships = first_s + second_s + third_s + fourth_s

    # Stats : Number of students
    stats['tot_stud'] = len(sol)
    stats['erasmus'] = erasmus
    stats['erasmus_pc'] = round(erasmus / total_internships * 100, 2)
    period_ids = models.period.Period.objects.filter(cohort=cohort).order_by('date_end').values_list("id", flat=True)
    stats['erasmus_students'] = len(models.internship_enrollment.InternshipEnrollment.objects.
                                    filter(period_id__in=period_ids).distinct('student').values('student'))
    stats['erasmus_students_pc'] = round(stats['erasmus_students'] / stats['tot_stud'] * 100, 2)
    stats['socio'] = socio
    stats['socio_pc'] = round(socio / total_internships * 100, 2)
    stats['socio_students'] = len(students_socio)
    stats['socio_students_pc'] = round(stats['socio_students'] / stats['tot_stud'] * 100, 2)

    # Stats: Internships per choice
    stats['first'] = first
    stats['first_pc'] = round(first / total_internships * 100, 2)
    stats['second'] = second
    stats['second_pc'] = round(second / total_internships * 100, 2)
    stats['third'] = third
    stats['third_pc'] = round(third / total_internships * 100, 2)
    stats['fourth'] = fourth
    stats['fourth_pc'] = round(fourth / total_internships * 100, 2)
    stats['others'] = imposed_choices
    stats['others_pc'] = round(imposed_choices / total_internships * 100, 2)
    stats['others_students'] = len(others_students)
    stats['others_specialities'] = others_specialities
    stats['others_specialities_students'] = others_specialities_students
    stats['mean_stud'] = round(mean(mean_array), 2)

    # Stats: non-mandatory internships
    for key in non_mandatory_internships_stats:
        if 'count' not in key:
            count = non_mandatory_internships_stats[key]['count']
            perc = count / non_mandatory_internships_stats['count']
            non_mandatory_internships_stats[key]['count'] = count
            non_mandatory_internships_stats[key]['perc'] = round(perc * 100, 2)
    stats['non_mandatory_internships'] = non_mandatory_internships_stats

    # Compute standard deviation of the score
    if len(mean_array) > 1:
        std_dev_stud = round(stdev(mean_array), 2)
    else:
        std_dev_stud = 0
    stats['std_dev_stud'] = std_dev_stud
    stats['mean_noncons'] = round(consecutive_month / number_of_students, 2)
    stats['sol_cost'] = total_cost
    stats['total_internships'] = total_internships

    if len(distance_mean) == 0:
        distance_mean.append(0)
    stats['distance_mean'] = round(mean(distance_mean), 2)
    stats['hospital_error'] = hospital_error_count

    # Stats: Internships of normal students
    if total_n_internships == 0:
        total_n_internships = 1
    stats['first_n'] = first_n
    stats['second_n'] = second_n
    stats['third_n'] = third_n
    stats['fourth_n'] = fourth_n
    stats['first_n_pc'] = round(first_n / total_n_internships * 100, 2)
    stats['second_n_pc'] = round(second_n / total_n_internships * 100, 2)
    stats['third_n_pc'] = round(third_n / total_n_internships * 100, 2)
    stats['fourth_n_pc'] = round(fourth_n / total_n_internships * 100, 2)
    stats['others_n_pc'] = round(imposed_choices / total_n_internships * 100, 2)

    # Stats: Internships of social students
    if total_s_internships == 0:
        total_s_internships = 1
    stats['first_s'] = first_s
    stats['second_s'] = second_s
    stats['third_s'] = third_s
    stats['fourth_s'] = fourth_s
    stats['first_s_pc'] = round(first_s / total_s_internships * 100, 2)
    stats['second_s_pc'] = round(second_s / total_s_internships * 100, 2)
    stats['third_s_pc'] = round(third_s / total_s_internships * 100, 2)
    stats['fourth_s_pc'] = round(fourth_s / total_s_internships * 100, 2)
    return stats


def load_solution_table(data, periods):
    period_ids = [period.id for period in periods]
    prd_internship_places = period_internship_places.PeriodInternshipPlaces.objects.filter(
        period_id__in=period_ids
    ).order_by("period_id").select_related(
        'internship_offer__organization',
        'internship_offer__speciality',
        'period'
    )
    # This object store the number of available places for given organization, speciality, period
    temp_internship_table = defaultdict(dict)

    keys = [period.name for period in periods]

    for pid in prd_internship_places:
        organization_ref = pid.internship_offer.organization.reference
        acronym = pid.internship_offer.speciality.acronym
        period_name = pid.period.name
        if acronym not in temp_internship_table[organization_ref]:
            temp_internship_table[organization_ref][acronym] = OrderedDict()
            _fill_periods_default_values(acronym, keys, organization_ref, temp_internship_table)

        temp_internship_table[organization_ref][acronym][period_name]['before'] += pid.number_places
        temp_internship_table[organization_ref][acronym][period_name]['after'] += pid.number_places

    for item in data:
        # Update the number of available places for given organization, speciality, period
        if item.organization.reference not in temp_internship_table or \
                item.speciality.acronym not in temp_internship_table[item.organization.reference]:
            continue
        temp_internship_table[item.organization.reference][item.speciality.acronym][item.period.name]['after'] -= 1
        # Update the % of takes places
        if temp_internship_table[item.organization.reference][item.speciality.acronym][item.period.name]['before'] > 0:
            temp_internship_table[item.organization.reference][item.speciality.acronym][item.period.name]['pc'] = \
                temp_internship_table[item.organization.reference][item.speciality.acronym][item.period.name]['after'] / \
                temp_internship_table[item.organization.reference][item.speciality.acronym][item.period.name]['before'] * 100
        else:
            temp_internship_table[item.organization.reference][item.speciality.acronym][item.period.name]['pc'] = 0
    # Sort all student by the score (descending order)
    sorted_internship_table = []
    for organization_ref, specialities in temp_internship_table.items():
        for speciality, periods in specialities.items():
            sorted_internship_table.append((int(organization_ref), speciality, periods))
    sorted_internship_table.sort(key=itemgetter(0))

    return sorted_internship_table


def load_solution_sol(cohort, student_affectations):
    periods = get_subcohorts_periods(cohort) if cohort.is_parent else get_assignable_periods(cohort_id=cohort.id)
    keys = [period.name for period in periods]
    internships = Internship.objects.filter(cohort=cohort)
    priority_choices = InternshipChoice.objects.filter(internship__in=internships, priority=True)
    students = Student.objects.filter(id__in=priority_choices.values("student").distinct())
    sol = {}
    for item in student_affectations:
        # Initialize empty periods of each student
        if item.student not in sol:
            sol[item.student] = {key: None for key in keys}
            # Sort the periods by name P1, P2, ...
            sol[item.student] = OrderedDict(sorted(sol[item.student].items(), key=_human_sort_key))
            sol[item.student]['score'] = 0
            item.student.priority = item.student in students
        # Put the internship in the solution
        sol[item.student][item.period.name] = item
        # store the cost of each student
        sol[item.student]['score'] += item.cost

    return sol


def _human_sort_key(object):
    key = object[0]
    return [int(t) if t.isdigit() else t for t in re.split('([0-9]+)', key)]


def _fill_periods_default_values(acronym, keys, organization, temp_internship_table):
    for key in keys:
        temp_internship_table[organization][acronym][key] = {
            'before': 0,
            'after': 0,
        }


def _get_student_mandatory_choices(cohort, priority):
    """
    Return all student's choices of given type.
    :param priority: True if we have to return the choices of priority student,
    false if we have to return the choices of normal students
    :return: A dict of dict : <speciality, <student, [choices]>>.
    """
    specialities = {}
    internships = models.internship.Internship.objects.filter(cohort=cohort)
    choices = models.internship_choice.InternshipChoice.objects.filter(priority=priority, internship__in=internships). \
        select_related("speciality", "student")

    if len(choices) == 0:
        return {}

    # Build dict with specialities[speciality][student] <- InternshipChoice
    for choice in choices:
        # Init the speciality if does not exists in 'specialities'
        if choice.speciality.id not in specialities:
            specialities[choice.speciality.id] = {}
        # Init the student if does not exists in 'specialities[choice.speciality]'
        if choice.student not in specialities[choice.speciality.id]:
            specialities[choice.speciality.id][choice.student] = []
        specialities[choice.speciality.id][choice.student].append(choice)

    # Remove erasmus choices
    if priority:
        periods = models.period.Period.objects.filter(cohort=cohort).order_by('date_end')
        for enrollment in models.internship_enrollment.InternshipEnrollment.objects.filter(period__in=periods):
            if enrollment.internship_offer.speciality.id in specialities:
                if enrollment.student in specialities[enrollment.internship_offer.speciality.id]:
                    del specialities[enrollment.internship_offer.speciality.id][enrollment.student]
    else:
        for choice in models.internship_choice.InternshipChoice.objects.filter(priority=True,
                                                                               internship__in=internships). \
                select_related("speciality", "student"):
            if choice.student in specialities[choice.speciality.id]:
                del specialities[choice.speciality.id][choice.student]

    # Convert the dict of students into list of students
    for speciality, students in specialities.items():
        specialities[speciality] = [v for v in students.values()]

    # Remove empty keys
    data = OrderedDict((k, v) for k, v in specialities.items() if v)

    # Sort he dict of student (this optimize the final result)

    all_specialities = models.internship_speciality.search(cohort=cohort, mandatory=True)
    orders = []

    for speciality in all_specialities:
        orders.append(speciality.name)

    specialities_dict = {}
    for speciality in models.internship_speciality.find_all(cohort=cohort):
        specialities_dict[speciality.name] = speciality.id

    for key in orders:
        if specialities_dict[key] in data:
            v = data[specialities_dict[key]]
            del data[specialities_dict[key]]
            data[specialities_dict[key]] = v

    return data
