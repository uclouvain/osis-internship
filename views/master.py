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
from django import shortcuts
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from internship.forms.internship_person_form import InternshipPersonForm
from internship.forms.master import MasterForm
from internship.models import master_allocation, internship_master, internship_speciality, organization, cohort
from internship.utils.exporting.masters import export_xls
from internship.views.common import display_errors, get_object_list


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def masters(request, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    filter_specialty = int(request.GET.get('specialty', 0))
    filter_hospital = int(request.GET.get('hospital', 0))
    filter_name = request.GET.get('name', '')

    allocations = master_allocation.search(current_cohort, filter_specialty, filter_hospital)
    if filter_name:
        allocations = allocations.filter(master__person__last_name__unaccent__icontains=filter_name) | \
                      allocations.filter(master__person__first_name__unaccent__icontains=filter_name)
    specialties = internship_speciality.find_by_cohort(current_cohort)
    hospitals = organization.find_by_cohort(current_cohort)
    allocations = get_object_list(request, allocations)
    return render(request, "masters.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master(request, cohort_id, master_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocated_master = internship_master.get_by_id(master_id)
    allocations = master_allocation.find_by_master(current_cohort, allocated_master)
    return render(request, "master.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_form(request, cohort_id, master_id=None, allocated_master=None):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    if master_id:
        allocated_master = internship_master.get_by_id(master_id)
        allocations = master_allocation.find_by_master(current_cohort, allocated_master)

    master_form = MasterForm(request.POST or None, instance=allocated_master)
    person = allocated_master.person if allocated_master else None
    person_form = InternshipPersonForm(request.POST or None, instance=person)
    specialties = internship_speciality.find_by_cohort(current_cohort)
    hospitals = organization.find_by_cohort(current_cohort)
    return render(request, "master_form.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_delete(request, master_id, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocated_master = internship_master.get_by_id(master_id)
    allocations = master_allocation.find_by_master(current_cohort, allocated_master)
    current_allocation = allocations.first()
    current_allocation.delete()
    allocated_master.person.delete()
    allocated_master.delete()
    messages.add_message(
        request,
        messages.SUCCESS,
        "{} : {} {}".format(_('Master deleted'), allocated_master.person.last_name, allocated_master.person.first_name),
        "alert-success"
    )
    return HttpResponseRedirect(reverse('internships_masters', kwargs={'cohort_id': cohort_id,}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_save(request, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocated_master = internship_master.get_by_id(request.POST.get("id")) if request.POST.get("id") else None
    form_master = MasterForm(request.POST, instance=allocated_master)
    person = allocated_master.person if allocated_master else None
    form_person = InternshipPersonForm(request.POST, instance=person)
    errors = []
    hospital = ""
    if form_master.is_valid() and form_person.is_valid():
        allocated_master = form_master.instance
        if _validate_allocations(request):
            person = form_person.save()
            master = form_master.save()
            master.person = person
            master.save()
            master_allocation.clean_allocations(current_cohort, allocated_master)
            allocations = _build_allocations(request, allocated_master)
            _save_allocations(allocations)
            hospital = _extract_hospital_id(allocations)
        else:
            errors.append(form_master.errors)
            messages.add_message(
                request,
                messages.ERROR,
                _('A master must be affected to at least one hospital or one specialty.'),
                "alert-danger"
            )
    else:
        errors.append(form_master.errors)
        display_errors(request, errors)

    if errors:
        return master_form(request=request, cohort_id=current_cohort.id, allocated_master=allocated_master)

    return HttpResponseRedirect("{}?hospital={}".format(reverse("internships_masters", args=[current_cohort.id]),
                                                        hospital))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def export_masters(request, cohort_id):
    workbook = export_xls()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=masters.xlsx'
    return response


def _build_allocations(request, allocated_master):
    hospitals = []
    if 'hospital' in request.POST:
        hospitals = request.POST.getlist('hospital')
        hospitals = _clean_empty_strings(hospitals)

    specialties = []
    if 'specialty' in request.POST:
        specialties = request.POST.getlist('specialty')
        specialties = _clean_empty_strings(specialties)

    allocations_ids = list(zip(hospitals, specialties))

    allocations = []

    for hospital_id, specialty_id in allocations_ids:
        hospital = organization.get_by_id(hospital_id) if hospital_id else None
        specialty = internship_speciality.get_by_id(specialty_id) if specialty_id else None
        allocation = master_allocation.MasterAllocation(master=allocated_master,
                                                        organization=hospital,
                                                        specialty=specialty)
        allocations.append(allocation)

    return allocations


def _clean_empty_strings(a_list):
    return [x if x is not '' else None for x in a_list]


def _save_allocations(allocations):
    for allocation in allocations:
        allocation.save()
        

def _extract_hospital_id(allocations):
    if allocations and allocations[0].organization:
        return allocations[0].organization.id
    else:
        return 0


def _validate_allocations(request):
    hospitals, specialties = request.POST.getlist('hospital'), request.POST.getlist('specialty')
    return hospitals[0] is not '' or specialties[0] is not ''
