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
from django import shortcuts
from reference.models import country
from internship.models import master_allocation, internship_speciality, organization, cohort
from internship.forms.master import MasterForm


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def masters(request, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    filter_specialty = int(request.GET.get('specialty', 0))
    filter_hospital = int(request.GET.get('hospital', 0))

    allocations = master_allocation.search(current_cohort, filter_specialty, filter_hospital)
    specialties = internship_speciality.find_by_cohort(current_cohort)
    hospitals = organization.find_by_cohort(current_cohort)

    return shortcuts.render(request, "masters.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master(request, cohort_id, allocation_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocation = master_allocation.find_by_id(allocation_id)

    allocated_master = allocation.master
    allocations = master_allocation.find_by_master(allocated_master)

    return shortcuts.render(request, "master.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_form(request, cohort_id, allocation_id=None):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    if allocation_id:
        allocated_master = master_allocation.find_by_id(allocation_id).master
        form = MasterForm(request.POST, instance=allocated_master)
    else:
        form = MasterForm(request.POST)

    countries = country.find_all()
    specialties = internship_speciality.find_by_cohort(current_cohort)
    hospitals = organization.find_by_cohort(current_cohort)
    return shortcuts.render(request, "master_form.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_save(request, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    form = MasterForm(request.POST)
    errors = []
    if form.is_valid():
        form.save()
    else:
        errors.append(form.errors)

    return shortcuts.render(request, "master_form.html", locals())
