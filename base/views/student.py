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
from django.contrib.auth.decorators import login_required, permission_required

from base import models as mdl
from . import layout


@login_required
@permission_required('base.can_access_student_path', raise_exception=True)
def students(request):
    if mdl.program_manager.is_program_manager(request.user):
        return layout.render(request, "student/students.html", {'students': None})
    response = layout.render(request, 'access_denied.html', {})
    response.status_code = 401
    return response


@login_required
@permission_required('base.can_access_student_path', raise_exception=True)
def student_search(request):
    students_list = name = None
    registration_id = request.GET.get('registration_id')
    if registration_id:
        student = mdl.student.find_by_registration_id(registration_id)
        if student:
            students_list = [student]
    else:
        name = request.GET.get('name')
        students_list = mdl.student.search(name)
    return layout.render(request, "student/students.html", {'students': students_list,
                                                            'registration_id': registration_id,
                                                            'name': name})


@login_required
@permission_required('base.can_access_student_path', raise_exception=True)
def student_read(request, registration_id):
    if mdl.program_manager.is_program_manager(request.user):
        student = mdl.student.find_by_id(registration_id)
        if student:
            offers_enrollments = mdl.offer_enrollment.find_by_student(student)
            exams_enrollments = mdl.exam_enrollment.find_by_student(student)
            lu_enrollments = mdl.learning_unit_enrollment.find_by_student(student)
        return layout.render(request, "student/student.html", locals())
    response = layout.render(request, 'access_denied.html', {})
    response.status_code = 401
    return response

