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
    student_choices = mdl_internship.internship_choice.get_non_mandatory_internship_choices()

    for student_choice in student_choices:
        student_registration_id = student_choice.student.registration_id
        student_obj = solver.get_student(student_registration_id)
        if not student_obj:
            student_obj = affect_student.Student(student_registration_id)
            solver.add_student(student_obj)

        choice_obj = affect_student.Choice(student_choice.internship_choice, student_choice.organization.id,
                                           student_choice.speciality.id, student_choice.choice, student_choice.priority)
        student_obj.add_choice(choice_obj)

    internship_period_places = mdl_internship.period_internship_places.PeriodInternshipPlaces.objects.all()  # TODO limit period to P9 - P12


    return solver
