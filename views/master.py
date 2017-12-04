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
from django import shortcuts

from internship import models as mdl_internship
from internship.models.cohort import Cohort
from internship.utils import integer


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_masters(request, cohort_id):
    cohort = shortcuts.get_object_or_404(Cohort, pk=cohort_id)
    filter_specialty = request.GET.get('specialty')
    filter_hospital = request.GET.get('hospital')

    masters = mdl_internship.internship_master.search(cohort, filter_specialty, filter_hospital)
    specialties = mdl_internship.internship_speciality.find_by_cohort(cohort)
    hospitals = mdl_internship.organization.find_by_cohort(cohort)

    filter_specialty = integer.to_int(filter_specialty)
    filter_hospital = integer.to_int(filter_hospital)

    return shortcuts.render(request, "internships_masters.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def delete_internships_masters(request, cohort_id):
    master_id = request.POST.get("id")
    master = mdl_internship.internship_master.find_by_id(master_id)
    master.delete()
    return HttpResponseRedirect(reverse('internships_masters', kwargs={'cohort_id': cohort_id, }))
