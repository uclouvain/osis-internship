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
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from internship.forms.cohort import CohortForm
from internship.models.cohort import Cohort


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def new(request):
    form = CohortForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(reverse('internship'))

    context = {
        'form': form,
        'page_title': _('create_cohort'),
    }
    return render(request, 'cohort/cohort_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def edit(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)

    form = CohortForm(data=request.POST or None, instance=cohort)

    if form.is_valid():
        form.save()
        return redirect(reverse('internship'))

    context = {
        'form': form,
        'page_title': _('edit_cohort'),
    }

    return render(request, 'cohort/cohort_form.html', context)