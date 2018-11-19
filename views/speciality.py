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
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from base.views.layout import render


from internship import models as mdl
from internship.forms.specialty import SpecialtyForm


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def specialities(request, cohort_id):
    cohort = get_object_or_404(mdl.cohort.Cohort, pk=cohort_id)
    specialties = mdl.internship_speciality.find_all(cohort=cohort)
    context = {'specialities': specialties, 'cohort': cohort}
    return render(request, "specialities.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_create(request, cohort_id, speciality=None):
    cohort = get_object_or_404(mdl.cohort.Cohort, pk=cohort_id)
    form = SpecialtyForm(request.POST or None)
    return render(request, "speciality_form.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_save(request, cohort_id, speciality_id):
    cohort = get_object_or_404(mdl.cohort.Cohort, pk=cohort_id)

    if speciality_id:
        check_speciality = mdl.internship_speciality.InternshipSpeciality.objects.filter(pk=speciality_id,
                                                                                         cohort=cohort).exists()
        if check_speciality:
            speciality = mdl.internship_speciality.InternshipSpeciality.objects.get(pk=speciality_id)
        else:
            speciality = mdl.internship_speciality.InternshipSpeciality(cohort=cohort)
    else:
        speciality = mdl.internship_speciality.InternshipSpeciality(cohort=cohort)

    speciality.name = request.POST.get('name')

    check_acronym = False
    if speciality.acronym != request.POST.get('acronym'):
        speciality.acronym = request.POST.get('acronym')
        check_acronym = mdl.internship_speciality.acronym_exists(cohort, speciality.acronym)

    if request.POST.get('sequence').strip():
        speciality.sequence = int(request.POST.get('sequence'))
    else:
        speciality.sequence = None

    mandatory = False
    if request.POST.get('mandatory'):
        mandatory = True
    speciality.mandatory = mandatory

    selectable = False
    if request.POST.get('selectable'):
        selectable = True
    speciality.selectable = selectable

    if check_acronym:
        messages.add_message(request, messages.ERROR, "{} : {}".format(_('Acronym already exists'),
                                                                       speciality.acronym), "alert-danger")
        return speciality_create(request, cohort.id, speciality)

    speciality.save()
    messages.add_message(request, messages.SUCCESS, "{} : {}".format(_('Specialty successfully saved'),
                                                                     speciality.name), "alert-success")
    return HttpResponseRedirect(reverse('internships_specialities', kwargs={'cohort_id': cohort.id,}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_new(request, cohort_id):
    return speciality_save(request, cohort_id, None)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def modify(request, cohort_id, speciality_id):
    cohort = get_object_or_404(mdl.cohort.Cohort, pk=cohort_id)
    speciality = get_object_or_404(mdl.internship_speciality.InternshipSpeciality,
                                   pk=speciality_id, cohort=cohort)
    form = SpecialtyForm(request.POST or None, instance=speciality)

    return render(request, "speciality_form.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def speciality_delete(request, cohort_id, speciality_id):
    cohort = get_object_or_404(mdl.cohort.Cohort, pk=cohort_id)
    speciality = get_object_or_404(mdl.internship_speciality.InternshipSpeciality, pk=speciality_id)
    mdl.internship_speciality.InternshipSpeciality.objects.filter(pk=speciality_id, cohort_id=cohort_id).delete()
    messages.add_message(request, messages.SUCCESS, "{} : {}".format(_('Specialty deleted'), speciality.name), "alert-success")
    return HttpResponseRedirect(reverse('internships_specialities', kwargs={'cohort_id': cohort.id,}))
