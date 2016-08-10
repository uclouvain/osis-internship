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
from internship.models import Period
from internship.forms import PeriodForm


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_periods(request):
    periods = Period.search()
    return render(request, "periods.html", {'section': 'internship',
                                            'periods' : periods})


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_create(request):
    f = PeriodForm(data=request.POST)
    return render(request, "period_create.html", {'section': 'internship',
                                                    'form' : f
                                                    })
@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_save(request, period_id):
    period = Period.find_by_id(period_id)
    form = PeriodForm(data=request.POST, instance=period)
    form.save()

    return HttpResponseRedirect(reverse('internships_periods'))

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_new(request):
    return period_save(request, None)

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_delete(request, period_id):
    period = Period.find_by_id(period_id)
    period.delete()
    return HttpResponseRedirect(reverse('internships_periods'))

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def period_modification(request, period_id):
    period = Period.find_by_id(period_id)
    period.date_start = period.date_start.strftime("%Y-%m-%d")
    period.date_end = period.date_end.strftime("%Y-%m-%d")

    return render(request, "period_create.html", {'section': 'internship',
                                                    'period' : period
                                                    })
