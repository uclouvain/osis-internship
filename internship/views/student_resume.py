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
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from base import models as mdl
from internship.models import InternshipChoice, InternshipStudentInformation, InternshipSpeciality

from django.utils.translation import ugettext_lazy as _


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_resume(request):
    students_list = InternshipChoice.find_by_all_student()

    for si in students_list:
        student = mdl.student.find_by_person(si.person)
        choices = InternshipChoice.find_by_student(student)
        si.number_choices = len(choices)

    specialities = InternshipSpeciality.find_by(mandatory=True)
    number_selection = 4 * len (specialities)


    return render(request, "student_search.html", {'s_noma':    None,
                                                   's_name':    None,
                                                   'students':  students_list,
                                                   'number_selection' : number_selection,
                                                   })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_search(request):
    s_name = request.GET['s_name']
    s_firstname = request.GET['s_firstname']
    students_list = []
    criteria_present = False

    s_name = s_name.strip()
    if len(s_name) <= 0:
        s_name = None
    else:
        criteria_present=True

    s_firstname = s_firstname.strip()
    if len(s_firstname) <= 0:
        s_firstname = None
    else:
        criteria_present=True

    message = None
    if criteria_present:
        students_list = InternshipStudentInformation.find_by(person_name=s_name, person_first_name = s_firstname)
    else:
        students_list = InternshipChoice.find_by_all_student()
        # message = "%s" % _('You must choose at least one criteria!')

    return render(request, "student_search.html",
                           {'s_name':       s_name,
                            's_firstname':  s_firstname,
                            'students':     students_list,
                            'init':         "0",
                            'message':      message})


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def internships_student_read(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.find_by_person(student[0].person)
    student = student[0]
    internship_choice = InternshipChoice.find_by_student(student)

    return render(request, "student_resume.html",
                           {'student':             student,
                            'information':         information,
                            'internship_choice':   internship_choice, })

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_information_modification(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.find_by_person(student[0].person)
    student = student[0]
    return render(request, "student_information_modification.html",
                           {'student':             student,
                            'information':         information, })

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_save_information_modification(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.find_by_person(student[0].person)
    if not information:
        information = InternshipStudentInformation()
        information.person = student[0].person
    information.email = request.POST['student_email']
    information.phone_mobile = request.POST['student_phone']
    information.location = request.POST['student_location']
    information.postal_code = request.POST['student_postal_code']
    information.city = request.POST['student_city']
    information.country = request.POST['student_country']
    information.save()

    redirect_url = reverse('internships_student_read', args=[registration_id])
    return HttpResponseRedirect(redirect_url)
