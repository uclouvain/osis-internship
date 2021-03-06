##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from internship.business import copy_cohort
from internship.forms.cohort import CohortForm
from internship.models.cohort import Cohort
from internship.views.common import display_errors


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def new(request):
    form = CohortForm(request.POST or None)
    errors = []
    if form.is_valid():
        cohort = form.save()
        copy_cohort.copy_from_origin(cohort)
        return redirect(reverse('internship'))
    else:
        errors.append(form.errors)
        display_errors(request, errors)

    context = {
        'form': form,
        'page_title': _('Add cohort'),
        'form_new': True
    }
    return render(request, 'cohort/cohort_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def edit(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)

    form = CohortForm(data=request.POST or None, instance=cohort)
    errors = []

    if form.is_valid():
        form.save()
        return redirect(reverse('internship'))
    else:
        errors.append(form.errors)
        display_errors(request, errors)

    context = {
        'form': form,
        'page_title': _('Edit cohort'),
    }

    return render(request, 'cohort/cohort_form.html', context)
