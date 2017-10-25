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
from collections import OrderedDict
from operator import itemgetter
from statistics import mean, stdev
from collections import defaultdict
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from internship.utils.student_assignment.solver import AssignmentSolver

from internship import models
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.views.internship import set_tabs_name
from internship.views.place import sort_organizations, set_speciality_unique

# ****************** Global vars ******************
errors = []  # List of all internship added to hospital error, as tuple (student, speciality, period)
solution = {}  # Dict with the solution => solution[student][period] = SolutionLine
internship_table = {}  # List of all available internship. Organization, speciality, period
internship_table_mi = {}  # List of available internship for "MI"
organizations = {}  # Dict of all organizations
specialities_dict = {}  # Dict of all specialities
distance_students = {}  # Dict of distances between students and hospitals
internship_offer_dic = {}  # Dict of all internship offers
organization_addresses_dic = {}  # Dict of all organization addresses
internship_table_original = {}  # Copy of internship_table, is used to know if an internship is empty

# ****************** Constants ******************
emergency = 15  # Id of the speciality "Urgences"
hospital_error = 999  # Reference of the hospital "erreur"
hospital_to_edit = 888  # Reference of the hospital "a_modifier"
# List of the periods => (name, priority)
periods_dict = {'P1': True, 'P2': True, 'P3': True, 'P4': True, 'P5': True, 'P6': True, 'P7': True, 'P8': True,
                'P9': False, 'P10': False, 'P11': False, 'P12': False}
# The costs used to compute the score of the solution
# First choice = cost 0, second choice = cost 1, etc
# I = impose internship, C = non-consecutive internship and X = hospital error
costs = {1: 0, 2: 1, 3: 2, 4: 3, 'I': 10, 'C': 5, 'X': 1000}


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
    specialities = models.internship_speciality.InternshipSpeciality.objects.filter(cohort=cohort).select_related()

    # Initialize the others_specialities and others_specialities_students
    for speciality in specialities:
        others_specialities[speciality] = 0
        others_specialities_students[speciality] = set()

    # Total number of internships
    first, second, third, fourth = 0, 0, 0, 0

    # Number of internships for each category
    # n = normal, s = social
    first_n, second_n, third_n, fourth_n = 0, 0, 0, 0
    first_s, second_s, third_s, fourth_s = 0, 0, 0, 0

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
        for period, internship in periods.items():
            if period is not 'score':
                if internship is not None:
                    # First choice
                    if internship.choice == "1":
                        # Increment the number of total first choices
                        first += 1
                        # Increment the number of total normal first choices
                        if internship.type_of_internship == "N":
                            first_n += 1
                        # Increment the number of total social first choices
                        if internship.type_of_internship == "S":
                            first_s += 1
                    # Second choice
                    elif internship.choice == "2":
                        second += 1
                        if internship.type_of_internship == "N":
                            second_n += 1
                        if internship.type_of_internship == "S":
                            second_s += 1
                    # Third choice
                    elif internship.choice == "3":
                        third += 1
                        if internship.type_of_internship == "N":
                            third_n += 1
                        if internship.type_of_internship == "S":
                            third_s += 1
                    # Fourth choice
                    elif internship.choice == "4":
                        fourth += 1
                        if internship.type_of_internship == "N":
                            fourth_n += 1
                        if internship.type_of_internship == "S":
                            fourth_s += 1
                    # Erasmus
                    elif internship.choice == 'E':  # Erasmus
                        erasmus += 1
                    # Imposed choice
                    elif internship.choice == 'I':  # Imposed hospital
                        # Retrieve the addresses of the hospital and the student
                        addr_student = models.internship_student_information.search(person=student.person)[0]
                        addr_organization = models.organization_address.search(organization=internship.organization)[0]
                        # Increment total of imposed choices
                        imposed_choices += 1
                        # Add the student to the set "others_students",
                        # we will use this set to find the number of students
                        # with imposed choices
                        others_students.add(student)
                        others_specialities[internship.speciality] += 1
                        others_specialities_students[internship.speciality].add(student)
                    # Hostpital error
                    if int(internship.organization.reference) == hospital_error:
                        hospital_error_count += 1
                    consecutive_month += internship.consecutive_month
    # Total number of students
    number_of_students = len(sol)
    # Total number of internships
    total_internships = number_of_students * 8

    # Get number of students socio
    students_socio = set()
    for speciality, students in get_student_mandatory_choices(cohort, True).items():
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
    period_ids = models.period.Period.objects.filter(cohort=cohort).values_list("id", flat=True)
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


def init_organizations(cohort):
    """
    Retrieve addresses of all organisation and init the hospital "error".
    """
    # Save data directly in global variables
    global organizations, organization_addresses_dic
    organizations[hospital_error] = models.organization.Organization.objects.filter(reference=hospital_error, cohort=cohort).first()
    organizations[hospital_to_edit] = \
        models.organization.Organization.objects.filter(reference=hospital_to_edit, cohort=cohort).first()

    for organization_address in models.organization_address.OrganizationAddress.objects.filter(organization__cohort=cohort):
        organization_addresses_dic[organization_address.organization] = organization_address


def init_specialities(cohort):
    """
    Retrieve all internship offers and the id of the speciality "emergency"
    """
    # Save data directly in global variables
    global specialities_dict, emergency, internship_offer_dic
    for speciality in models.internship_speciality.find_all(cohort=cohort):
        internship_offer_dic[speciality] = models.internship_offer.search(cohort=cohort, speciality=speciality)
        specialities_dict[speciality.name] = speciality.id
        if speciality.acronym.strip() == 'UR':
            emergency = speciality.id


def get_student_mandatory_choices(cohort, priority):
    """
    Return all student's choices of given type.
    :param priority: True if we have to return the choices of priority student,
    false if we have to return the choices of normal students
    :return: A dict of dict : <speciality, <student, [choices]>>.
    """
    specialities = {}
    internships = models.internship.Internship.objects.filter(cohort=cohort)
    choices = models.internship_choice.InternshipChoice.objects.filter(priority=priority, internship__in=internships).\
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
        periods = models.period.Period.objects.filter(cohort=cohort)
        for enrollment in models.internship_enrollment.InternshipEnrollment.objects.filter(period__in=periods):
            if enrollment.internship_offer.speciality.id in specialities:
                if enrollment.student in specialities[enrollment.internship_offer.speciality.id]:
                    del specialities[enrollment.internship_offer.speciality.id][enrollment.student]
    else:
        for choice in models.internship_choice.InternshipChoice.objects.filter(priority=True, internship__in=internships).\
                select_related("speciality", "student"):
            if choice.student in specialities[choice.speciality.id]:
                del specialities[choice.speciality.id][choice.student]

    # Convert the dict of students into list of students
    for speciality, students in specialities.items():
        specialities[speciality] = [v for v in students.values()]

    # Remove empty keys
    data = OrderedDict((k, v) for k, v in specialities.items() if v)

    # Sort he dict of student (this optimize the final result)
    global specialities_dict

    all_specialities = models.internship_speciality.search(cohort=cohort, mandatory=True)
    orders = []

    for speciality in all_specialities:
        orders.append(speciality.name)

    for key in orders:
        if specialities_dict[key] in data:
            v = data[specialities_dict[key]]
            del data[specialities_dict[key]]
            data[specialities_dict[key]] = v

    return data


def load_solution(data, cohort):
    """ Create the solution and internship_table from db data """
    # Initialise the table of internships.
    periods = models.period.Period.objects.filter(cohort=cohort)
    period_ids = periods.values_list("id", flat=True)
    period_internship_places = models.period_internship_places.PeriodInternshipPlaces.objects.filter(period_id__in=period_ids).\
        order_by("period_id").select_related()
    # This object store the number of available places for given organization, speciality, period
    temp_internship_table = defaultdict(dict)

    keys = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12']

    for pid in period_internship_places:
        organization = pid.internship_offer.organization
        acronym = pid.internship_offer.speciality.acronym
        period_name = pid.period.name
        if acronym not in temp_internship_table[organization]:
            temp_internship_table[organization][acronym] = OrderedDict()
            fill_periods_default_values(acronym, keys, organization, temp_internship_table)

        temp_internship_table[organization][acronym][period_name]['before'] += pid.number_places
        temp_internship_table[organization][acronym][period_name]['after'] += pid.number_places

    sol = {}
    for item in data:
        # Initialize 12 empty period of each student
        if item.student not in sol:
            sol[item.student] = OrderedDict()
            sol[item.student] = {key: None for key in keys}
            # Sort the periods by name P1, P2, ...
            sol[item.student] = OrderedDict(sorted(sol[item.student].items(), key=lambda t: int(t[0][1:])))
            sol[item.student]['score'] = 0
        # Put the internship in the solution
        sol[item.student][item.period.name] = item
        # store the cost of each student
        sol[item.student]['score'] += item.cost
        # Update the number of available places for given organization, speciality, period
        if item.organization not in temp_internship_table or \
                        item.speciality.acronym not in temp_internship_table[item.organization]:
            continue
        temp_internship_table[item.organization][item.speciality.acronym][item.period.name]['after'] -= 1
        # Update the % of takes places
        if temp_internship_table[item.organization][item.speciality.acronym][item.period.name]['before'] > 0:
            temp_internship_table[item.organization][item.speciality.acronym][item.period.name]['pc'] = \
                temp_internship_table[item.organization][item.speciality.acronym][item.period.name]['after'] / \
                temp_internship_table[item.organization][item.speciality.acronym][item.period.name]['before'] * 100
        else:
            temp_internship_table[item.organization][item.speciality.acronym][item.period.name]['pc'] = 0
    # Sort all student by the score (descending order)
    sorted_internship_table = []
    for organization, specialities in temp_internship_table.items():
        for speciality, periods in specialities.items():
            sorted_internship_table.append((int(organization.reference), speciality, periods))
    sorted_internship_table.sort(key=itemgetter(0))

    return sol, sorted_internship_table


def fill_periods_default_values(acronym, keys, organization, temp_internship_table):
    for key in keys:
        temp_internship_table[organization][acronym][key] = {
            'before': 0,
            'after': 0,
        }


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def assign_automatically_internships(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    if request.method == 'POST':
            start_date_time = datetime.now()
            period_ids = models.period.Period.objects.filter(cohort=cohort).values_list("id", flat=True)
            current_affectations = models.internship_student_affectation_stat.find_non_mandatory_affectations(period_ids=period_ids)
            current_affectations._raw_delete(current_affectations.db)
            solver = AssignmentSolver(cohort)
            solver.solve()
            solver.persist_solution()
            end_date_time = datetime.now()
            affectation_generation_time = models.affectation_generation_time.AffectationGenerationTime()
            affectation_generation_time.cohort = cohort
            affectation_generation_time.start_date_time = start_date_time
            affectation_generation_time.end_date_time = end_date_time
            affectation_generation_time.generated_by = request.user.username
            affectation_generation_time.save()
    return redirect(reverse('internship_affectation_statistics',  kwargs={'cohort_id': cohort.id}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_affectation_statistics(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    init_organizations(cohort)
    init_specialities(cohort)
    sol, table, stats, internship_errors = None, None, None, None
    periods = models.period.Period.objects.filter(cohort=cohort)
    period_ids = periods.values_list("id", flat=True)

    student_affectations = InternshipStudentAffectationStat.objects\
        .filter(period_id__in=period_ids)\
        .select_related("student", "organization", "speciality", "period")

    if student_affectations.count() > 0:
        sol, table = load_solution(student_affectations, cohort)
        stats = compute_stats(cohort, sol)
        # Mange sort of the students
        sol = OrderedDict(sorted(sol.items(), key=lambda t: t[0].person.last_name))
        # Mange sort of the organizations
        table.sort(key=itemgetter(0))

        internship_errors = InternshipStudentAffectationStat.objects \
            .filter(organization=organizations[hospital_error],
                    period_id__in=period_ids)

    latest_generation = models.affectation_generation_time.get_latest()

    context = {
        'section': 'internship',
        'cohort': cohort,
        'recap_sol': sol,
        'stats': stats,
        'organizations': table,
        'errors': internship_errors,
        'latest_generation': latest_generation
    }

    return render(request, "internship_affectation_statics.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_affectation_sumup(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    all_speciality = list(models.internship_speciality.find_all(cohort=cohort))
    all_speciality = set_speciality_unique(all_speciality)
    set_tabs_name(all_speciality)
    periods = models.period.search(cohort=cohort)
    organizations = models.organization.search(cohort=cohort)
    organizations = sort_organizations(organizations)
    offers = models.internship_offer.search(cohort=cohort)
    informations = []
    for organization in organizations:
        for offer in offers:
            if offer.organization.reference == organization.reference:
                informations.append(offer)

    for x in range (0,len(informations)):
        if informations[x] != 0:
            if informations[x].speciality.acronym == "MI":
                informations[x+1] = 0
                informations[x+2] = 0

    informations = [x for x in informations if x != 0]

    all_affectations = list(models.internship_student_affectation_stat.search())
    affectations = {}
    for speciality in all_speciality:
        temp_affectations = {}
        for period in periods:
            temp_temp_affectations = []
            for aff in all_affectations:
                if aff.speciality.acronym == speciality.acronym and aff.period == period:
                    temp_temp_affectations.append(aff)
            temp_affectations[period.name] = temp_temp_affectations
        affectations[speciality.name] = temp_affectations

    context = {
        'section': 'internship',
        'specialities': all_speciality,
        'periods': periods,
        'organizations': informations,
        'affectations': affectations,
        'cohort': cohort
    }
    return render(request, "internship_affectation_sumup.html", context)
