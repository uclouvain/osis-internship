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
from internship.models import InternshipChoice, InternshipStudentInformation, \
                                InternshipSpeciality, InternshipOffer, InternshipStudentAffectationStat, \
                                Organization, InternshipSpeciality, Period
from internship.views.place import sort_organizations, set_organization_address

from django.utils.translation import ugettext_lazy as _


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_resume(request):
    # Get all stundents and the mandatory specialities
    students_list = InternshipChoice.find_by_all_student()
    specialities = InternshipSpeciality.search(mandatory=True)
    student_informations = InternshipStudentInformation.find_all()

    for si in student_informations:
        student = mdl.student.find_by_person(si.person)
        choices = InternshipChoice.find_by_student(student)
        si.number_choices = len(choices)
        if student:
            si.registration_id = student.registration_id

    # Get the required number selection (4 for each speciality)
    # Get the number of student who have al least 4 corrects choice of internship
    # Get the number of student who can choose their internships
    number_selection = 4 * len (specialities)
    student_with_internships = len(students_list)
    students_can_have_internships = len(InternshipStudentInformation.find_all())

    students_ok = 0
    students_not_ok = 0
    # Set the number of the student who have their all selection of internships
    # who have a partial selection
    # who have no selection
    for sl in students_list:
        student = mdl.student.find_by_person(sl.person)
        choices = InternshipChoice.find_by_student(student)
        sl.number_choices = len(choices)
        if len(choices) == number_selection:
            students_ok += 1
        else :
            students_not_ok += 1
    student_without_internship = students_can_have_internships - student_with_internships
    return render(request, "student_search.html", {'s_noma':    None,
                                                   's_name':    None,
                                                   'students':  student_informations,
                                                   'number_selection' : number_selection,
                                                   'students_ok' : students_ok,
                                                   'students_not_ok' : students_not_ok,
                                                   'student_with_internships' : student_with_internships,
                                                   'students_can_have_internships' : students_can_have_internships,
                                                   'student_without_internship' : student_without_internship,
                                                   })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_search(request):
    s_name = request.GET['s_name']
    s_firstname = request.GET['s_firstname']
    students_list = []
    students_list_creation = []
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
        students_list_check = InternshipStudentInformation.search(person__last_name=s_name, person__first_name = s_firstname)

        students_list_creation = InternshipChoice.find_by_all_student()

        for student_check in students_list_check :
            for student_creation in students_list_creation:
                    if student_check.person == student_creation.person:
                        students_list.append(student_creation)
    else:
        students_list = InternshipChoice.find_by_all_student()


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
    student = student[0]
    information = InternshipStudentInformation.search(person = student.person)
    internship_choice = InternshipChoice.find_by_student(student)
    all_speciality = InternshipSpeciality.find_all()

    affectations = InternshipStudentAffectationStat.search(student = student).order_by("period")
    periods = Period.search().order_by("date_start")
    organizations = Organization.search()
    set_organization_address(organizations)

    # Set the adress of the affactation
    for affectation in affectations:
        for organization in organizations:
            if affectation.organization == organization:
                affectation.organization.address = ""
                for o in organization.address:
                    affectation.organization.address = o

    internships = InternshipOffer.find_internships()
    #Check if there is a internship offers in data base. If not, the internships
    #can be block, but there is no effect
    if len(internships) > 0:
        if internships[0].selectable:
            selectable = True
        else:
            selectable = False
    else:
        selectable = True

    return render(request, "student_resume.html",
                           {'student':             student,
                            'information':         information[0],
                            'internship_choice':   internship_choice,
                            'specialities':        all_speciality,
                            'selectable':          selectable,
                            'affectations':        affectations,
                            'periods':              periods,

                            })

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_information_modification(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id)
    information = InternshipStudentInformation.search(person = student[0].person)
    student = student[0]
    return render(request, "student_information_modification.html",
                           {'student':             student,
                            'information':         information[0], })

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

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_affectation_modification(request, student_registration_id):
    informations = InternshipStudentAffectationStat.search(student__registration_id = student_registration_id)
    for i in informations:
        print (i.speciality)
    organizations = Organization.search()
    organizations = sort_organizations(organizations)

    specialities = InternshipSpeciality.find_all()
    periods = Period.search().order_by("date_start")
    return render(request, "student_affectation_modification.html",
                           {'information':         informations[0],
                           'informations':         informations,
                            'organizations':        organizations,
                            'specialities':         specialities,
                            'periods':              periods,
                                                      })
