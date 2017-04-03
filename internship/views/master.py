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
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from internship import models as mdl_internship
from internship.models.cohort import Cohort


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_masters(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    # First get the value of the 2 options for the sort
    if request.method == 'GET':
        speciality_sort_value = request.GET.get('speciality_sort')
        organization_sort_value = request.GET.get('organization_sort')

    # Then select Internship Master depending of the options
    # If both exist / if just speciality exist / if just organization exist / if none exist
    if speciality_sort_value and speciality_sort_value != "0":
        if organization_sort_value and organization_sort_value != "0":
            query = mdl_internship.internship_master.search(speciality = speciality_sort_value, organization__name = organization_sort_value)
        else:
            query = mdl_internship.internship_master.search(speciality = speciality_sort_value)
    else:
        if organization_sort_value and organization_sort_value != "0":
            query = mdl_internship.internship_master.search(organization__name = organization_sort_value)
        else:
            query = mdl_internship.internship_master.find_masters()

    # Create the options for the selected list, delete dubblons
    query_master = mdl_internship.internship_master.find_masters()
    master_specs = []
    master_organizations = []
    for master in query_master:
        master_specs.append(master.speciality)
        master_organizations.append(master.organization)
    master_specs = list(set(master_specs))
    master_specs = sorted(master_specs)
    master_organizations = list(set(master_organizations))
    number_ref = []
    for organization in master_organizations:
        if organization is not None:
            number_ref.append(organization.reference)
    number_ref=sorted(number_ref, key=int)
    master_organizations = []
    for i in number_ref:
        organization = mdl_internship.organization.search(reference=i)
        master_organizations.append(organization[0])
    context = {
        'section': 'internship',
        'all_masters': query,
        'all_spec': master_specs,
        'all_organizations': master_organizations,
        'speciality_sort_value': speciality_sort_value,
        'organization_sort_value': organization_sort_value,
        'cohort': cohort,
    }
    return render(request, "internships_masters.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def delete_internships_masters(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    first_name = request.POST.get("first_name").replace(" ", "")
    name = request.POST.get("name").replace(" ", "")
    # Get the first and last name of the master send by the button of deletion
    # Get the master in the DB and delete it
    mdl_internship.internship_master.search(first_name=first_name, last_name=name).delete()
    return HttpResponseRedirect(reverse('internships_masters', kwargs={
        'cohort_id': cohort_id,
    }))
