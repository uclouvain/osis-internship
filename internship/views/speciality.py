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
from base import models as mdl
from internship.models import InternshipSpeciality
from internship.forms import InternshipSpecialityForm


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def specialities(request):
    specialities = InternshipSpeciality.find_all()
    return render(request, "specialities.html", {'section': 'internship',
                                            'specialities' : specialities})


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_create(request):
    f = InternshipSpecialityForm(data=request.POST)
    learning_unit = mdl.learning_unit.search(acronym='WMDS2333')
    return render(request, "speciality_create.html", {'section': 'internship',
                                                    'learning_unit' : learning_unit[0],
                                                    'form' : f
                                                    })

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_save(request, speciality_id):
    form = InternshipSpecialityForm(data=request.POST)
    check_speciality = InternshipSpeciality.find_by(id=speciality_id)
    if check_speciality :
        speciality = check_speciality[0]
    else :
        speciality = InternshipSpeciality()

    mandatory = False
    if request.POST.get('mandatory') :
        mandatory = True

    learning_unit = mdl.learning_unit.search(acronym=request.POST.get('learning_unit'))
    speciality.learning_unit = learning_unit[0]
    speciality.name = request.POST.get('name')
    speciality.mandatory = mandatory

    speciality.save()
    return render(request, "speciality_create.html", {'section': 'internship',
                                                    'learning_unit' : learning_unit[0],
                                                    })

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_new(request):
    return speciality_save(request, None)

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_modification(request, speciality_id):

    spec = InternshipSpeciality.find_by(id = speciality_id)
    speciality = spec[0]
    learning_unit = mdl.learning_unit.search(acronym='WMDS2333')
    return render(request, "speciality_create.html", {'section': 'internship',
                                                    'learning_unit' : learning_unit[0],
                                                    'speciality' : speciality
                                                    })
