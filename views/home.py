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
from django.contrib.auth.decorators import permission_required
from django.db.models import Subquery, OuterRef
from django.shortcuts import render, get_object_or_404
from django.views.decorators import http

from internship.models.cohort import Cohort
from internship.models.enums.role import Role
from internship.models.enums.user_account_status import UserAccountStatus
from internship.models.internship_offer import find_internships
from internship.models.master_allocation import MasterAllocation


@permission_required('internship.is_internship_manager', raise_exception=True)
def cohort_home(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    blockable = find_internships(cohort).filter(selectable=True).count() > 0
    context = {'blockable': blockable, 'cohort': cohort, 'users_to_activate': _count_delegates_without_user(cohort)}
    return render(request, "internship/home.html", context=context)


@http.require_http_methods(['GET'])

@permission_required('internship.is_internship_manager', raise_exception=True)
def view_cohort_selection(request):
    subcohorts_query = Cohort.objects.filter(parent_cohort__pk=OuterRef('pk')).order_by('subscription_start_date')
    parent_cohorts = Cohort.objects.filter(is_parent=True).annotate(
        start_date=Subquery(subcohorts_query.values('subscription_start_date')[:1])
    ).order_by('-start_date')
    standalone_cohorts = Cohort.objects.filter(is_parent=False, parent_cohort=None)
    return render(request, 'cohort/selection.html', {
        'parent_cohorts': parent_cohorts,
        'standalone_cohorts': standalone_cohorts
    })


def _count_delegates_without_user(cohort):
    return MasterAllocation.objects.filter(
        organization__cohort=cohort,
        role=Role.DELEGATE.name,
        master__user_account_status=UserAccountStatus.INACTIVE.name
    ).count()
