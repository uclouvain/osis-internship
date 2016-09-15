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


def set_number_choices(student_informations):
    for si in student_informations:
        student = mdl.student.find_by_person(si.person)
        choices = InternshipChoice.find_by_student(student)
        si.number_choices = len(choices)
        if student:
            si.registration_id = student.registration_id


def get_number_ok_student(students_list, number_selection):
    students_list = list(students_list)
    nbr_student = [0]*2
    # Set the number of the student who have their all selection of internships
    # who have a partial selection
    # who have no selection
    for sl in students_list:
        student = mdl.student.find_by_person(sl.person)
        choices = InternshipChoice.find_by_student(student)
        sl.number_choices = len(choices)
        if len(choices) == number_selection:
            nbr_student[0] += 1
        else :
            nbr_student[1] += 1
    return nbr_student


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_resume(request):
    # Get all stundents and the mandatory specialities
    students_list = InternshipChoice.find_by_all_student()
    specialities = InternshipSpeciality.search(mandatory=True)
    student_informations = InternshipStudentInformation.find_all()

    set_number_choices(student_informations)

    # Get the required number selection (4 for each speciality)
    # Get the number of student who have al least 4 corrects choice of internship
    # Get the number of student who can choose their internships
    number_selection = 4 * len (specialities)
    student_with_internships = len(students_list)
    students_can_have_internships = len(InternshipStudentInformation.find_all())

    students_ok = get_number_ok_student(students_list, number_selection)

    student_without_internship = students_can_have_internships - student_with_internships
    return render(request, "student_search.html", {'search_name': None,
                                                    'search_firstname': None,
                                                   'students': student_informations,
                                                   'number_selection': number_selection,
                                                   'students_ok': students_ok[0],
                                                   'students_not_ok': students_ok[1],
                                                   'student_with_internships': student_with_internships,
                                                   'students_can_have_internships': students_can_have_internships,
                                                   'student_without_internship': student_without_internship,
                                                   })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_search(request):
    search_name = request.GET['search_name']
    search_firstname = request.GET['search_firstname']
    criteria_present = False

    search_name = search_name.strip()
    search_name = search_name.title()
    if len(search_name) <= 0:
        search_name = None
    else:
        criteria_present=True

    search_firstname = search_firstname.strip()
    search_firstname = search_firstname.title()
    if len(search_firstname) <= 0:
        search_firstname = None
    else:
        criteria_present=True

    if criteria_present:
        student_informations = InternshipStudentInformation.search(person__last_name=search_name, person__first_name = search_firstname)
    else:
        student_informations = InternshipStudentInformation.find_all()

    # Get all stundents and the mandatory specialities
    students_list = InternshipChoice.find_by_all_student()
    specialities = InternshipSpeciality.search(mandatory=True)

    set_number_choices(student_informations)

    # Get the required number selection (4 for each speciality)
    # Get the number of student who have al least 4 corrects choice of internship
    # Get the number of student who can choose their internships
    number_selection = 4 * len (specialities)
    student_with_internships = len(students_list)
    students_can_have_internships = len(InternshipStudentInformation.find_all())

    students_ok = get_number_ok_student(students_list, number_selection)
    student_without_internship = students_can_have_internships - student_with_internships

    return render(request, "student_search.html",
                           {'search_name': search_name,
                            'search_firstname': search_firstname,
                            'students': student_informations,
                            'number_selection': number_selection,
                            'students_ok': students_ok[0],
                            'students_not_ok': students_ok[1],
                            'student_with_internships': student_with_internships,
                            'students_can_have_internships': students_can_have_internships,
                            'student_without_internship': student_without_internship,
                            })


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def internships_student_read(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.search(person = student[0].person)
    student = student[0]
    internship_choice = InternshipChoice.find_by_student(student)
    all_speciality = InternshipSpeciality.search(mandatory=True)

    return render(request, "student_resume.html",
                           {'student': student,
                            'information': information[0],
                            'internship_choice': internship_choice,
                            'specialities': all_speciality,
                            })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_information_modification(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.search(person = student[0].person)
    student = student[0]
    return render(request, "student_information_modification.html",
                           {'student': student,
                            'information': information[0], })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_save_information_modification(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.search(person = student[0].person)
    if not information:
        information = InternshipStudentInformation()
        information.person = student[0].person
    else:
        information = information[0]
    information.email = request.POST.get('student_email')
    information.phone_mobile = request.POST.get('student_phone')
    information.location = request.POST.get('student_location')
    information.postal_code = request.POST.get('student_postal_code')
    information.city = request.POST.get('student_city')
    information.country = request.POST.get('student_country')
    information.latitude = None
    information.longitude = None
    information.save()

    redirect_url = reverse('internships_student_read', args=[registration_id])
    return HttpResponseRedirect(redirect_url)
