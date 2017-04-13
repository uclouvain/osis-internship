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
from django.shortcuts import get_object_or_404, render

from internship import models as mdl_internship
from internship.forms.period_form import PeriodForm
from internship.models.cohort import Cohort
from internship.models.period import Period


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_periods(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = mdl_internship.period.Period.objects.filter(cohort_id=cohort_id)
    context = {
        'section': 'internship',
        'periods': periods,
        'cohort': cohort,
    }
    return render(request, "periods.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_create(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    period_form = PeriodForm()
    context = {
        'section': 'internship',
        'form': period_form,
        'cohort': cohort,
        'url_form': reverse('period_new', kwargs={'cohort_id': cohort.id}),
    }
    return render(request, "period_create.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_save(request, cohort_id, period_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    period = get_object_or_404(Period, pk=period_id, cohort_id=cohort_id)
    form = PeriodForm(data=request.POST, instance=period)
    form.save()

    kwargs = {
        'cohort_id': cohort.id
    }
    return HttpResponseRedirect(reverse('internships_periods', kwargs=kwargs))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_new(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    period = mdl_internship.period.Period()
    period.cohort = cohort
    form = PeriodForm(data=request.POST, instance=period)
    form.save()
    kwargs = {
        'cohort_id': cohort.id
    }
    return HttpResponseRedirect(reverse('internships_periods', kwargs=kwargs))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_delete(request, cohort_id, period_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    period = get_object_or_404(Period, pk=period_id, cohort__id=cohort_id)
    period.delete()
    kwargs = {
        'cohort_id': cohort.id
    }
    return HttpResponseRedirect(reverse('internships_periods', kwargs=kwargs))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_get(request, cohort_id, period_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    period = get_object_or_404(Period, pk=period_id, cohort__id=cohort_id)

    kwargs = {
        'cohort_id': cohort.id,
        'period_id': period.id,
    }
    context = {
        'section': 'internship',
        'period': period,
        'cohort': cohort,
        'url_form': reverse('period_save', kwargs=kwargs)
    }

    return render(request, "period_create.html", context=context)
