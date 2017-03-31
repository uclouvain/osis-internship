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
from internship import models as mdl_internship


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_home(request, cohort_id):
    blockable = mdl_internship.internship_offer.get_number_selectable() > 0
    from internship.models.cohort import Cohort
    cohort = Cohort.objects.get(pk=cohort_id)
    context = {
        'section': 'internship',
        'blockable': blockable,
        'cohort': cohort,
    }
    return render(request, "internships_home.html", context=context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def view_cohort_selection(request):
    from internship.models.cohort import Cohort

    cohorts = Cohort.objects.all()
    return render(request, 'cohort/selection.html', {'cohorts': cohorts})
