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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from base import models as mdl
from internship import models as mdl_internship


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def specialities(request, cohort_id):
    cohort = get_object_or_404(mdl_internship.Cohort, pk=cohort_id)
    specialties = mdl_internship.internship_speciality.find_all(cohort=cohort)
    context = {
        'section': 'internship',
        'specialities': specialties,
        'cohort': cohort,
    }
    return render(request, "specialities.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_create(request, cohort_id):
    cohort = get_object_or_404(mdl_internship.Cohort, pk=cohort_id)
    learning_unit = mdl.learning_unit.search(acronym='WMDS2333')
    return render(request, "speciality_form.html", {'section': 'internship',
                                                    'learning_unit': learning_unit.first(),
                                                    'cohort': cohort})


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_save(request, cohort_id, speciality_id):
    cohort = get_object_or_404(mdl_internship.Cohort, pk=cohort_id)
    if speciality_id:
        speciality = mdl_internship.internship_speciality.find_by_id(speciality_id)
    else:
        speciality = mdl_internship.internship_speciality.InternshipSpeciality(cohort=cohort)

    mandatory = False
    if request.POST.get('mandatory'):
        mandatory = True

    learning_unit_id = int(request.POST.get('learning_unit'))
    learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
    speciality.learning_unit = learning_unit.first()
    speciality.name = request.POST.get('name')
    speciality.acronym = request.POST.get('acronym')
    speciality.mandatory = mandatory
    speciality.save()
    return HttpResponseRedirect(reverse('internships_specialities', kwargs={'cohort_id': cohort.id,}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_new(request, cohort_id):
    return speciality_save(request, cohort_id, None)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_modification(request, cohort_id, speciality_id):
    cohort = get_object_or_404(mdl_internship.Cohort, pk=cohort_id)
    speciality = get_object_or_404(mdl_internship.InternshipSpeciality, pk=speciality_id, cohort=cohort)
    learning_unit = mdl.learning_unit.search(acronym='WMDS2333')
    context = {
        'section': 'internship',
        'learning_unit': learning_unit.first(),
        'speciality': speciality,
        'cohort': cohort,
    }
    return render(request, "speciality_form.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_delete(request, cohort_id, speciality_id):
    cohort = get_object_or_404(mdl_internship.Cohort, pk=cohort_id)
    mdl_internship.internship_speciality.InternshipSpeciality.objects.filter(pk=speciality_id, cohort_id=cohort_id).delete()
    return HttpResponseRedirect(reverse('internships_specialities', kwargs={'cohort_id': cohort.id,}))
