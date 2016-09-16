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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from internship.models import Organization, InternshipSpeciality

import os
import sys
import copy
import random
from collections import OrderedDict

from random import randint, choice
from internship.models import *
from statistics import mean, stdev
from internship.views.internship import calc_dist
from internship.views.place import sort_organizations

################################################# Global vars #################################################
errors = []
solution = {}
internship_table = {}
organizations = {}
distance_students = {}
distance_mean = []
current_distance = None
total_maps_requests = 0
################################################# Constants #################################################
emergency = 8
hospital_error = 999
hospital_to_edit = 888
periods_dict = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: False, 10: False, 11: False,
                12: False}
costs = {1: 0, 2: 1, 3: 2, 4: 3, 'I': 10, 'C': 5, 'X': 1000}


################################################# Classes #################################################

class SolutionsLine:
    def __init__(self, student, organization, speciality, period, choice, type_of_internship='N', cost=0,
                 consecutive_month=0):
        self.student = student
        self.organization = organization
        self.speciality = speciality
        self.period = period
        self.choice = choice
        self.cost = cost
        self.consecutive_month = consecutive_month
        self.type_of_internship = type_of_internship

    def __repr__(self):
        return "[P:" + str(self.period).zfill(2) + "|H:" + str(self.organization.id).zfill(3) + "|S:" + str(
            self.speciality.id).zfill(2) + "|C:" + str(self.cost).zfill(2) + "(" + str(self.choice) + ")|T:" + str(
            self.type_of_internship) + "]"


class StudentChoice:
    def __init__(self, student, organization, speciality, choice, priority):
        self.student = student
        self.organization = organization
        self.speciality = speciality
        self.choice = choice
        self.priority = priority


################################################# Utils #################################################

def compute_stats(sol):
    """
    Compute the statistics of the solution
    """
    stats = {}
    total_cost, first, second, third, fourth, consecutive_month, imposed_choices, erasmus, hospital_error_count = 0, 0, 0, 0, 0, 0, 0, 0, 0
    mean_array = []
    others_students = set()
    others_specialities = {}
    others_specialities_students = {}
    specialities = InternshipSpeciality.objects.all()
    for speciality in specialities:
        others_specialities[speciality] = 0
        others_specialities_students[speciality] = set()

    first_n, second_n, third_n, fourth_n = 0, 0, 0, 0
    first_s, second_s, third_s, fourth_s = 0, 0, 0, 0
    first_e, second_e, third_e, fourth_e = 0, 0, 0, 0
    for studentId, periods in sol.items():
        cost = periods['score']
        total_cost += cost
        mean_array.append(cost)
        for period, internship in periods.items():
            if period is not 'score':
                if internship is not None:
                    if internship.choice == "1":
                        first += 1
                        if internship.type_of_internship == "N":
                            first_n += 1
                        if internship.type_of_internship == "S":
                            first_s += 1
                        if internship.type_of_internship == "E":
                            first_e += 1
                    elif internship.choice == "2":
                        second += 1
                        if internship.type_of_internship == "N":
                            second_n += 1
                        if internship.type_of_internship == "S":
                            second_s += 1
                        if internship.type_of_internship == "E":
                            second_e += 1
                    elif internship.choice == "3":
                        third += 1
                        if internship.type_of_internship == "N":
                            third_n += 1
                        if internship.type_of_internship == "S":
                            third_s += 1
                        if internship.type_of_internship == "E":
                            third_e += 1
                    elif internship.choice == "4":
                        fourth += 1
                        if internship.type_of_internship == "N":
                            fourth_n += 1
                        if internship.type_of_internship == "S":
                            fourth_s += 1
                        if internship.type_of_internship == "E":
                            fourth_e += 1
                    elif internship.choice == 'E':  # Erasmus
                        erasmus += 1
                    elif internship.choice == 'I':  # Imposed hospital
                        imposed_choices += 1
                        others_students.add(studentId)
                        others_specialities[internship.speciality] += 1
                        others_specialities_students[internship.speciality].add(studentId)
                    if internship.organization.reference == hospital_error:
                        hospital_error_count += 1
                    consecutive_month += internship.consecutive_month
    number_of_students = len(sol)
    total_internships = number_of_students * 8

    students_socio = set()
    for speciality, students in get_student_mandatory_choices(True).items():
        for choices in students:
            students_socio.add(choices[0].student.id)

    socio = len(InternshipChoice.objects.filter(priority=True).distinct('student').values('student'))

    stats['tot_stud'] = len(sol)
    stats['erasmus'] = erasmus
    stats['erasmus_pc'] = round(erasmus / total_internships * 100, 2)
    stats['erasmus_students'] = len(InternshipEnrollment.objects.distinct('student').values('student'))
    stats['erasmus_students_pc'] = round(stats['erasmus_students'] / stats['tot_stud'] * 100, 2)
    stats['socio'] = socio
    stats['socio_pc'] = round(socio / total_internships * 100, 2)
    stats['socio_students'] = len(students_socio)
    stats['socio_students_pc'] = round(stats['socio_students'] / stats['tot_stud'] * 100, 2)

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
    stats['std_dev_stud'] = round(stdev(mean_array), 2)
    stats['mean_noncons'] = round(consecutive_month / number_of_students, 2)
    stats['sol_cost'] = total_cost
    stats['total_internships'] = total_internships

    stats['distance_mean'] = 0
    stats['hospital_error'] = hospital_error_count
    stats['total_maps_requests'] = total_maps_requests

    stats['first_n'] = first_n
    stats['second_n'] = second_n
    stats['third_n'] = third_n
    stats['fourth_n'] = fourth_n
    stats['first_n_pc'] = round(first_n / total_internships * 100, 2)
    stats['second_n_pc'] = round(second_n / total_internships * 100, 2)
    stats['third_n_pc'] = round(third_n / total_internships * 100, 2)
    stats['fourth_n_pc'] = round(fourth_n / total_internships * 100, 2)

    stats['first_s'] = first_s
    stats['second_s'] = second_s
    stats['third_s'] = third_s
    stats['fourth_s'] = fourth_s
    stats['first_s_pc'] = round(first_s / total_internships * 100, 2)
    stats['second_s_pc'] = round(second_s / total_internships * 100, 2)
    stats['third_s_pc'] = round(third_s / total_internships * 100, 2)
    stats['fourth_s_pc'] = round(fourth_s / total_internships * 100, 2)
    return stats

def shift_array(array):
    """ Shift array at random index """
    position = randint(0, len(array) - 1)
    return array[position:] + array[:position]

def create_solution_line(student, organization, speciality, period, choice, type_of_internship='N', cost=0,
                         consecutive_month=0):
    solution_line = InternshipStudentAffectationStat()
    solution_line.student = student
    solution_line.organization = organization
    solution_line.speciality = speciality
    solution_line.period = period
    solution_line.choice = choice
    solution_line.cost = cost
    solution_line.consecutive_month = consecutive_month
    solution_line.type_of_internship = type_of_internship
    return solution_line

def init_internship_table():
    """
    Initialise the table of internships.
    This object store the number of available places for given organization, speciality, period
    :return: a dict : internshipTable[organization][speciality][period]
    """
    period_internship_places = PeriodInternshipPlaces.objects.all()
    temp_internship_table = {}
    for pid in period_internship_places:
        if pid.internship.organization not in temp_internship_table:
            temp_internship_table[pid.internship.organization] = {}
        if pid.internship.speciality not in temp_internship_table[pid.internship.organization]:
            temp_internship_table[pid.internship.organization][pid.internship.speciality] = {}
        temp_internship_table[pid.internship.organization][pid.internship.speciality][pid.period.id] = pid.number_places
    return temp_internship_table

def init_solution():
    """
    Initialize the empty solution, the soslution is represented by a dictionary of students.
    Each student will have a dict with 12 periods and each period will have an 'InternshipEnrollment'
    :return: Empty solution represented by solution[student][Period] = InternshipEnrollment
    """
    # Retrieve all students
    students = InternshipChoice.find_by_all_student()
    data = {}
    # For each student create an empty dict
    for student in students:
        data[student] = {}
    return data

def init_organizations():
    global organizations
    organizations[hospital_error] = Organization.objects.filter(reference=hospital_error)[0]
    organizations[hospital_to_edit] = Organization.objects.filter(reference=hospital_to_edit)[0]

def is_internship_available(organization, speciality, period):
    """
    Check if an internship is available for given organization, speciality, period.
    An internship is available if we have at least 1 place left
    :param organization: id of the organisation
    :param speciality: id of the speciality
    :param period: id of the period
    :return: True if the internship is available False otherwise
    """
    global internship_table
    return internship_table[organization][speciality][period] > 0

def decrease_available_places(organization, speciality, period):
    """
    Decrease the number of available places for given organization, speciality, period
    :param organization: id of the organisation
    :param speciality: id of the speciality
    :param period: id of the period
    """
    internship_table[organization][speciality][period] -= 1

def get_available_periods_of_student(student_solution, mandatory):
    """
    Get available periods of students. Return all periods that does not exists in the solution of the student.
    :param student_solution: solution of the student(a dict where the key represent the id of the period and
    the value represents an InternshipEnrollment )
    :param mandatory: Specify the type of periods to check
    :return: the set of available periods of the student
    """
    available_periods = set()
    for period, type in periods_dict.items():
        # Check if the student have already an internship assigned for period 'period' and if the period is mandatory
        if period not in student_solution and type == mandatory:
            available_periods.add(period)
        pass
    return available_periods

def get_available_periods_of_internship(organization, speciality):
    """
    Get available periods of internship for given organization, speciality.
    The internship is available if it have at least 1 place available
    :param organization: id of the organization
    :param speciality: id of the speciality
    :return: the set of available periods of the internship
    """
    available_periods = set()
    if speciality in internship_table[organization]:
        for key, value in internship_table[organization][speciality].items():
            if value > 0:
                available_periods.add(key)
    return available_periods

def get_double_available_periods_of_student(student_solution, mandatory):
    """
    This method is used to find suitable periods of the student for the speciality 'Emergency'.
    We need to find all consecutive periods of the students that are still free.
    :param student_solution: solution of the student(a dict where the key represent the id of the period and
    the value represents an InternshipEnrollment )
    :param mandatory: Specify the type of periods to check
    :return: the set of available double periods of the student
    """
    available_periods = set()
    for period, type in periods_dict.items():
        if mandatory == type:
            # Check if period is not present in the solution
            if period not in student_solution:
                next_period = period + 1
                # Check if period + 1 is not present in the solution and if the types of periods are the same
                if next_period <= len(periods_dict) and period + 1 not in student_solution and periods_dict[
                    next_period] == mandatory:
                    available_periods.add((period, period + 1))
    return available_periods

def is_same(student_solution, organization, period):
    """
    Check if 'studentSolution[period].organization' and 'organization' are the same.
    :param student_solution: solution of the student(a dict where the key represent the id of the period and
    the value represents an InternshipEnrollment )
    :param organization: organisation to compare
    :param period: id of the period
    :return: True if 2 organisation are the same, False otherwise
    """
    if period < 0 or period > len(periods_dict):
        return False
    elif period not in student_solution or student_solution[period].organization != organization:
        return False
    else:
        return True

def get_solution_cost(data):
    """
    Compute the cost of the student's solution.
    """
    student_score = 0
    for period, internship in data.items():
        if internship is not None:
            if isinstance(internship.choice, int):
                student_score = student_score + costs[internship.choice]
            if not is_same(data, data[period].organization, period - 1) and not is_same(data, data[period].organization,
                                                                                        period + 1):  # Nonconsecutive organization
                student_score = student_score + costs['C']
            if data[period].choice == 'I':  # Imposed organization
                student_score = student_score + costs['I']
    return student_score

def update_scores(student):
    """
    Update the cost of each internship for given student solution.
    """
    data = solution[student]
    for period, internship in data.items():
        score = 0
        solution[student][period].consecutive_month = 0
        if isinstance(internship.choice, int):
            score = score + costs[internship.choice]
        if not is_same(data, data[period].organization, period - 1) and not is_same(data, data[period].organization,
                                                                                    period + 1):  # Nonconsecutive organization
            score = score + costs['C']
            solution[student][period].consecutive_month = 1
        if data[period].choice == 'I':
            score = score + costs['I']
        solution[student][period].cost = score

def valid_distance():
    """
    Ig the organization is imposed, add the distance to distance_mean list
    """
    global current_distance
    if current_distance is not None:
        distance_mean.append(current_distance)
        current_distance = None

def compute_distance(addr1, addr2):
    """
    Compute the distance between 2 addresses
    :param addr1:  Student address
    :param addr2:  Organization Address
    :return: Distance in km between the organization and the student address
    """

    distance = calc_dist(addr1.latitude, addr1.longitude, addr2.latitude, addr2.longitude)
    return distance

    # For the moment we use the random distance
    #global total_maps_requests
    #distance = random.randint(1, 200)
    #global current_distance
    #current_distance = distance
    #total_maps_requests += 1
    #return random.randint(1, 200)

def get_student_mandatory_choices(priority):
    """
    Return all student's choices of given type.
    :param priority: True if we have to return the choices of priority student, false if we have to return the choices of normal students
    :return: A dict of dict : <speciality, <student, [choices]>>.
    """
    specialities = {}
    choices = InternshipChoice.objects.filter(priority=priority)
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
        for enrollment in InternshipEnrollment.objects.all():
            if enrollment.internship_offer.speciality.id in specialities and enrollment.student in specialities[
                enrollment.internship_offer.speciality.id]:
                del specialities[enrollment.internship_offer.speciality.id][enrollment.student]
    else:
        for choice in InternshipChoice.objects.filter(priority=True):
            if choice.student in specialities[choice.speciality.id]:
                del specialities[choice.speciality.id][choice.student]

    # Convert the dict of students into list of students
    for speciality, students in specialities.items():
        specialities[speciality] = [v for v in students.values()]
    # Remove empty keys
    return dict((k, v) for k, v in specialities.items() if v)

def find_nearest_hopital(student, speciality, exclude):
    """
    Find the nearest available hospital. The start point is the address of the student and the end point the address of the hospital.
    :param student: Student object
    :param speciality: Speciality of the internship
    :param exclude: Set of all hospital that we already tried for this student
    :return: the nearest available hospital
    """
    # Check if the student has already computed the distances.
    if student not in distance_students:
        internships = InternshipOffer.search(speciality=speciality)
        addr_student = InternshipStudentInformation.search(person=student.person)[0]
        data = {}
        for internship in internships:
            # Ignore erasmus organizations
            if int(internship.organization.reference) < 500:
                if student not in distance_students:
                    distance_students[student] = {}
                addr_organization = OrganizationAddress.search(organization=internship.organization)[0]
                # Compute the distance between 2 addresses and store it in the dict
                if addr_organization.latitude is not None and addr_student.latitude is not None:
                    data[internship.organization] = compute_distance(addr_student, addr_organization)

        # Sort organizations by distance
        ordered_data = OrderedDict(sorted(data.items(), key=lambda t: t[1]))
        distance_students[student] = ordered_data

    for organization, distance in distance_students[student].items():
        # Return lowest not excluded organization
        if organization not in exclude:
            return organization

def iterate_choices(choices, priority):
    """
    For each choice we generate a solution and compute the score of this solution
    :param choices: List of the choices
    :param priority: True if the student is a social student false otherwise
    :return: List of bests solutions (will contain multiples choices if the score is the same)
    """
    best_solutions = []
    current_score = sys.maxsize
    student = choices[0].student
    # Get all still available periods of the students
    available_periods_of_student = get_available_periods_of_student(solution[student], True)
    # Iterate over all choices
    for choice in choices:
        # Get all available periods for given organization / speciality
        available_periods_of_internship = get_available_periods_of_internship(choice.organization, choice.speciality)
        # Iterate over all available periods of the student
        for available_period in available_periods_of_student:
            # Check if the internship have an available_period
            if available_period in available_periods_of_internship:
                if priority:
                    type_of_internship = "S"
                else:
                    type_of_internship = "N"
                # Copy the original solution of the student
                temp_solution = copy.copy(solution[student])
                # And create the new solution with the new internship
                temp_solution[available_period] = SolutionsLine(student, choice.organization, choice.speciality,
                                                                available_period, choice.choice, type_of_internship)
                # Compute the score of the new solution
                temp_score = get_solution_cost(temp_solution)
                temp_solution[available_period].cost = temp_score
                # Check if the new solution is better than old
                if temp_score < current_score:
                    current_score = temp_score
                    del best_solutions[:]  # Clean the list
                    best_solutions.append(temp_solution[available_period])
                elif temp_score == current_score:
                    best_solutions.append(temp_solution[available_period])
    return best_solutions

def iterate_choices_emergency(choices, priority):
    """
    For each choice we generate a solution and compute the score of this solution.
    This method is a bit different from the previous method because we have to place 2 internship consecutive (Emergency)
    :param choices: List of the choices
    :param priority: True if the student is a social student false otherwise
    :return: List of bests solutions (will contain multiples choices if the score is the same)
    """
    best_solutions = []
    current_score = sys.maxsize
    student = choices[0].student
    # Get a list of tuples of all double available periods of the students
    available_periods_of_student = get_double_available_periods_of_student(solution[student], True)
    # Iterate over all choices
    for choice in choices:
        # Get all available periods for given organization / speciality
        available_periods_of_internship = get_available_periods_of_internship(choice.organization, choice.speciality)
        # Iterate over all available periods of the student
        for available_period in available_periods_of_student:
            # Check if the internship have an available_period[0] and available_period[1]
            if available_periods_of_internship is not None and available_period[
                0] in available_periods_of_internship and available_period[1] in available_periods_of_internship:
                if priority:
                    type_of_internship = "S"
                else:
                    type_of_internship = "N"
                # Copy the original solution of the student
                temp_solution = copy.copy(solution[student])
                # And create the new solution with the 2 new internships
                temp_solution[available_period[0]] = SolutionsLine(student, choice.organization,
                                                                   choice.speciality,
                                                                   available_period[0], choice.choice,
                                                                   type_of_internship)
                temp_solution[available_period[1]] = SolutionsLine(student, choice.organization,
                                                                   choice.speciality,
                                                                   available_period[1], choice.choice,
                                                                   type_of_internship)
                # Compute the score of the new solution
                temp_score = get_solution_cost(temp_solution)
                # In order to optimise the solution, we prefer to start with an odd period, if it not the case we add 15 points to the solution.
                # This operation helps to better use of available places
                if available_period[0] in [2, 4, 6, 8, 10, 12]:
                    temp_score += 15
                # Compute the score of the new solution
                temp_solution[available_period[0]].cost = temp_score
                temp_solution[available_period[1]].cost = temp_score
                # Check if the new solution is better than old
                if temp_score < current_score:
                    current_score = temp_score
                    del best_solutions[:]  # Clean the list
                    best_solutions.append((temp_solution[available_period[0]], temp_solution[available_period[1]]))
                elif temp_score == current_score:
                    best_solutions.append((temp_solution[available_period[0]], temp_solution[available_period[1]]))
    return best_solutions

def get_best_choice_emergency(choices, priority):
    """
    This method iterate over the choices of the student, if no choice is available a new organization is imposed to the student.
    If many choices have the same score we will chose the choice witch have more available places.
    :param choices: List of the choices of the student
    :param priority: True if the student is a social student, false otherwise
    :return: Best choice
    """

    # Iterate over student choices
    best_solutions = iterate_choices_emergency(choices, priority)
    # If no choice is available, we impose a new choice
    if len(best_solutions) == 0:
        # If the student's internship is marked as a social internship
        if priority:
            # Add directly the hospital error
            imposed_choice = [StudentChoice(choices[0].student, organizations[hospital_to_edit], choices[0].speciality, 'X', choices[0].priority)]
            best_solutions = iterate_choices_emergency(imposed_choice, priority)
        else:
            # If the student is a normal student, we will try to find the nearest available hospital
            exclude = set()
            while True:
                organization = find_nearest_hopital(choices[0].student, choices[0].speciality, exclude)
                # If we tried all hospital and none is available, we impose the hospital "error"
                if organization is None:
                    imposed_choice = [StudentChoice(choices[0].student, organizations[hospital_error], choices[0].speciality, 'X', choices[0].priority)]
                else:
                    imposed_choice = [StudentChoice(choices[0].student, organization, choices[0].speciality, 'I', choices[0].priority)]

                # Iterate over new hospital
                best_solutions = iterate_choices_emergency(imposed_choice, priority)
                # If all places are already taken, the hospital is added to exclude list.
                if len(best_solutions) > 0 or organization is None:
                    break
                else:
                    exclude.add(organization)
            valid_distance()

    # If only one solution exists, we return it directly
    if len(best_solutions) == 1:
        return best_solutions[0]
    # Otherwise check which solution has more available places
    elif len(best_solutions) > 1:
        max_places = -sys.maxsize - 1
        best_solutions_filtered = []
        for sol in best_solutions:
            c0 = sol[0]
            c1 = sol[1]
            available_places = internship_table[c0.organization][c0.speciality][c0.period]
            available_places += internship_table[c1.organization][c1.speciality][c1.period]
            if available_places > max_places:
                max_places = available_places
                del best_solutions_filtered[:]  # Clean the list
                best_solutions_filtered.append(sol)
            elif available_places == max_places:
                best_solutions_filtered.append(sol)
        return choice(best_solutions_filtered)
        # return random.choice(best_solutions_filtered)

def get_best_choice(choices, priority):
    """
    This method iterate over the choices of the student, if no choice is available a new organization is imposed to the student.
    If many choices have the same score we will chose the choice witch have more available places.
    :param choices: List of the choices of the student
    :param priority: True if the student is a social student, false otherwise
    :return: Best choice
    """
    best_solutions = iterate_choices(choices, priority)
    # All 4 choices are unavailable
    if len(best_solutions) == 0:
        # If the student's internship is marked as a social internship
        if priority:
            # Add directly the hospital error
            imposed_choice = [
                StudentChoice(choices[0].student, organizations[hospital_to_edit], choices[0].speciality, 'X',
                              choices[0].priority)]
            best_solutions = iterate_choices(imposed_choice, priority)
        else:
            # If the student is a normal student, we will try to find the nearest available hospital
            exclude = set()
            while True:
                organization = find_nearest_hopital(choices[0].student, choices[0].speciality, exclude)
                # If we tried all hospital and none is available, we impose the hospital "error"
                if organization is None:
                    organization = organizations[hospital_error]
                    imposed_choice = [
                        StudentChoice(choices[0].student, organization, choices[0].speciality, 'X',
                                      choices[0].priority)]
                else:
                    imposed_choice = [
                        StudentChoice(choices[0].student, organization, choices[0].speciality, 'I',
                                      choices[0].priority)]

                best_solutions = iterate_choices(imposed_choice, priority)
                if len(best_solutions) > 0 or organization is None:
                    break
                else:
                    exclude.add(organization)
            valid_distance()
    # If only one solution exists, we return it directly
    if len(best_solutions) == 1:
        return best_solutions[0]
    # Otherwise check which solution has more avaiable places
    elif len(best_solutions) > 1:
        max_places = -sys.maxsize - 1
        best_solutions_filtered = []
        for sol in best_solutions:
            available_places = internship_table[sol.organization][sol.speciality][sol.period]
            if available_places > max_places:
                max_places = available_places
                del best_solutions_filtered[:]  # Clean the list
                best_solutions_filtered.append(sol)
            elif available_places == max_places:
                best_solutions_filtered.append(sol)
        return choice(best_solutions_filtered)
        # return random.choice(best_solutions_filtered)


def fill_erasmus_choices():
    """
    Fill the solution with all erasmus internships
    :return:
    """
    # Retrieve all students
    erasmus_enrollments = InternshipEnrollment.objects.all()
    for enrol in erasmus_enrollments:
        if is_internship_available(enrol.place, enrol.internship_offer.speciality, enrol.period.id):
            solution[enrol.student][enrol.period.id] = SolutionsLine(enrol.student,
                                                                     enrol.internship_offer.organization,
                                                                     enrol.internship_offer.speciality,
                                                                     enrol.period.id, "E", "E")
            # Decrease the number of available places
            decrease_available_places(enrol.place, enrol.internship_offer.speciality, enrol.period.id)
        else:
            pass
            # TODO Handle it
            # print("ERROR: Try to add erasmus student | Student : " + str(enrol.student.id) + " SP : " + str(
            #     enrol.internship_offer.speciality.id) + " H : " + str(enrol.place.id) + " P: " + str(enrol.period.id))

def fill_emergency_choices(priority):
    """
    Fill the solution with emergency choices.
    :param priority: True if the student is a social student, false otherwise
    """
    data = get_student_mandatory_choices(priority)
    if emergency in data:
        # Start with "Emergency"
        emergency_students = data.pop(emergency)
        # Shift the students
        shifted_students = shift_array(emergency_students)
        for choices in shifted_students:
            # Get the best choice
            choice = get_best_choice_emergency(choices, priority)
            if choice is not None:
                choice0 = choice[0]
                choice1 = choice[1]
                # Add choice to the solution
                solution[choice0.student][choice0.period] = choice0
                solution[choice1.student][choice1.period] = choice1
                # Decrease the available places
                decrease_available_places(choice0.organization, choice0.speciality, choice0.period)
                decrease_available_places(choice1.organization, choice1.speciality, choice1.period)
                # Update the score of the solution
                update_scores(choice0.student)

def fill_normal_choices(priority):
    """
    Fill the solution with the choices of all specialities except emergency
    :param priority: True if the student is a social student, false otherwise
    """
    data = get_student_mandatory_choices(priority)
    # Remove emergency from the dict
    if emergency in data:
        data.pop(emergency)
    # Then do others specialities
    for speciality, students in data.items():
        # Shift the students
        shifted_students = shift_array(students)
        for choices in shifted_students:
            # Get the best choice
            choice = get_best_choice(choices, priority)
            if choice is not None:
                # Add choice to the solution
                solution[choice.student][choice.period] = choice
                # Decrease the available places
                decrease_available_places(choice.organization, choice.speciality, choice.period)
                # Update the score of the solution
                update_scores(choice.student)

def generate_and_save():
    """
    Generate the new solution and save it in the database
    :return:
    """
    global solution, internship_table
    solution = init_solution()
    internship_table = init_internship_table()
    init_organizations()
    fill_erasmus_choices()
    fill_emergency_choices(True)
    fill_emergency_choices(False)
    fill_normal_choices(True)
    fill_normal_choices(False)

    InternshipStudentAffectationStat.objects.all().delete()
    periods = Period.search().order_by('id')

    for student, internships in solution.items():
        for period, internship in internships.items():
            internship.period = periods[internship.period - 1]
            sol_line = create_solution_line(internship.student, internship.organization, internship.speciality,
                                            internship.period, internship.choice, internship.type_of_internship,
                                            internship.cost, internship.consecutive_month)
            sol_line.save()

def load_solution(data):
    """ Create the solution and internship table from db data """
    # Initialise the table of internships.
    period_internship_places = PeriodInternshipPlaces.objects.all()
    # This object store the number of available places for given organization, speciality, period
    temp_internship_table = {}
    for pid in period_internship_places:
        if pid.internship.organization not in temp_internship_table:
            temp_internship_table[pid.internship.organization] = {}
        if pid.internship.speciality not in temp_internship_table[pid.internship.organization]:
            temp_internship_table[pid.internship.organization][pid.internship.speciality] = {}
        temp_internship_table[pid.internship.organization][pid.internship.speciality][pid.period.id] = {}
        temp_internship_table[pid.internship.organization][pid.internship.speciality][pid.period.id][
            'before'] = pid.number_places
        temp_internship_table[pid.internship.organization][pid.internship.speciality][pid.period.id][
            'after'] = pid.number_places
    sol = {}
    keys = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12]
    for item in data:
        # Initialize 12 empty period of each student
        if item.student not in sol:
            sol[item.student] = {key: None for key in keys}
            sol[item.student]['score'] = 0
        # Put the internship in the solution
        sol[item.student][item.period.id] = item
        # store the cose of each student
        sol[item.student]['score'] += item.cost
        # Update the number of available places for given organization, speciality, period
        temp_internship_table[item.organization][item.speciality][item.period.id]['after'] -= 1
        # Update the % of takes places
        temp_internship_table[item.organization][item.speciality][item.period.id]['pc'] = \
            temp_internship_table[item.organization][item.speciality][item.period.id]['after'] / \
            temp_internship_table[item.organization][item.speciality][item.period.id]['before'] * 100
    # Sort all student by the score (descending order)
    temp_internship_table = OrderedDict(sorted(temp_internship_table.items(), key=lambda t: int(t[0].reference)))
    return (sol, temp_internship_table)

@login_required
def internship_affectation_statistics_generate(request):
    """ Generate new solution, save it in the database, redirect back to the page 'internship_affectation_statistics'"""
    if request.method == 'POST':
        generate_and_save()
        return HttpResponseRedirect(reverse('internship_affectation_statistics'))

@login_required
def internship_affectation_statistics(request):
    init_organizations()
    sol, table, stats, errors = None, None, None, None
    data = InternshipStudentAffectationStat.search()

    if len(data) > 0:
        sol, table = load_solution(data)
        stats = compute_stats(sol)
        sol = OrderedDict(sorted(sol.items(), key=lambda t: t[1]['score'], reverse=True))
        errors = InternshipStudentAffectationStat.objects.filter(organization=organizations[hospital_error])

    return render(request, "internship_affectation_statics.html",
                  {'section': 'internship', 'recap_sol': sol, 'stats': stats, 'organizations': table, 'errors': errors,
                   'has_data': False})

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_affectation_sumup(request):
    all_speciality = InternshipSpeciality.search(mandatory=True)
    periods = Period.search()
    organizations = Organization.search()
    organizations = sort_organizations(organizations)
    offers = InternshipOffer.search()
    informations = []
    for organization in organizations:
        for offer in offers:
            if offer.organization.reference == organization.reference:
                informations.append(offer)
    affectations = InternshipStudentAffectationStat.search().order_by("student__person__last_name", "student__person__first_name", "period__date_start")

    return render(request, "internship_affectation_sumup.html",
                  {'section': 'internship',
                   'specialities':        all_speciality,
                   'periods':             periods,
                   'organizations':       organizations,
                   'affectations':        affectations,
                   })
