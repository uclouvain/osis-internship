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
import sys
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from internship import models as mdl_internship
from datetime import datetime
from base import models as mdl_base


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_affectation_statistics_generate(request):
    """ Generate new solution, save it in the database, redirect back to the page 'internship_affectation_statistics'"""
    if request.method == 'POST':
        if request.POST['executions'] != "":
            start_date_time = datetime.now()
            cost = sys.maxsize
            for i in range(0, int(request.POST['executions'])):
                pass
        return redirect(reverse('internship_affectation_statistics'))


from internship.utils import affect_student


def init_solver():
    solver = affect_student.Solver()

    __init_students(solver)
    __init_offers(solver)

    return solver


def launch_solver(solver, times=1):
    best_assignments = None
    for _ in range(0, times):
        best_assignments = solver.solve()

    if best_assignments:
        __save_to_db(best_assignments)


def __save_to_db(assignments):
    for student_registration_id, assignment in assignments.items():
        period, offer_id = assignment
        student = mdl_base.student.find_by_registration_id(student_registration_id)
        offer = mdl_internship.internship_offer.find_intership_by_id(offer_id)

        period_obj = __convert_int_to_period(period)
        if not period_obj or not student or not offer:
            continue

        affectation = mdl_internship.internship_student_affectation_stat.\
            InternshipStudentAffectationStat(student=student, organization=offer.organization,
                                             speciality=offer.speciality, period=period_obj,
                                             choice=str(1), cost=1)
        affectation.save()


def __init_students(solver):
    student_choices = mdl_internship.internship_choice.get_non_mandatory_internship_choices()
    for student_choice in student_choices:
        student_registration_id = student_choice.student.registration_id
        student_obj = solver.get_student(student_registration_id)
        if not student_obj:
            student_obj = affect_student.StudentWrapper(student_registration_id)
            solver.add_student(student_obj)

        choice_obj = affect_student.Choice(student_choice.internship_choice, student_choice.organization.id,
                                           student_choice.speciality.id, student_choice.choice, student_choice.priority)
        student_obj.add_choice(choice_obj)


def __init_offers(solver):
    internship_period_places = mdl_internship.period_internship_places.PeriodInternshipPlaces.objects.all()
    for period_place in internship_period_places:
        period = __convert_period_to_int(period_place.period)
        if not __is_internval_period(period):
            continue
        places = period_place.number_places
        organization_id = period_place.internship.organization.id
        speciality_id = period_place.internship.speciality.id
        offer_id = period_place.internship.id
        offer_obj = solver.get_offer(organization_id, speciality_id)
        if not offer_obj:
            offer_obj = affect_student.Offer(offer_id, organization_id, speciality_id, [])
            solver.add_offer(offer_obj)

        offer_obj.add_places(period, places)


def __is_internval_period(period):
    MIN_PERIOD = 9
    MAX_PERIOD = 12
    return period > MIN_PERIOD or period < MAX_PERIOD


def __convert_period_to_int(period):
    period_name = period.name
    return int(period_name.lstrip("P"))

def __convert_int_to_period(period_int):
    period_name = "P" + str(period_int)
    return mdl_internship.period.find_by_name(period_name)
