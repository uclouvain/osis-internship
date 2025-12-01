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
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from internship import models
from internship.forms.organization_form import OrganizationForm
from internship.models.organization import Organization
from internship.utils.exporting import organization_affectation_hospital
from internship.utils.exporting import organization_affectation_master
from internship.views.common import display_report_errors
from internship.views.internship import get_all_specialities, set_tabs_name
from osis_common.decorators.download import set_download_cookie
from reference.models.country import Country


@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_places(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)

    if cohort.is_parent:
        organizations = models.organization.Organization.objects.filter(
            cohort__in=cohort.subcohorts.all()
        ).order_by('reference').distinct('reference')
    else:
        organizations = models.organization.Organization.objects.filter(cohort=cohort).order_by('reference')

    context = {'all_organizations': organizations, 'cohort': cohort}
    return render(request, "places.html", context)



@permission_required('internship.is_internship_manager', raise_exception=True)
def place_save(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    errors = []

    if organization_id:
        organization = models.organization.get_by_id(organization_id)
    else:
        organization = models.organization.Organization()

    organization.cohort = cohort

    form = OrganizationForm(data=request.POST, instance=organization)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "{} : {} - {}".format(
            _("Hospital saved"), form.cleaned_data["reference"], form.cleaned_data["name"]), "alert-success")
    else:
        errors.append(form.errors)
        display_report_errors(request, errors)

    countries = Country.objects.order_by('name')

    return render(request, "place_form.html", locals())



@permission_required('internship.is_internship_manager', raise_exception=True)
def place_remove(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    organization = models.organization.get_by_id(organization_id)
    organization.delete()
    return internships_places(request, cohort_id)



@permission_required('internship.is_internship_manager', raise_exception=True)
def organization_new(request, cohort_id):
    return place_save(request, cohort_id, None)



@permission_required('internship.is_internship_manager', raise_exception=True)
def organization_edit(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    organization = models.organization.get_by_id(organization_id)
    countries = Country.objects.order_by('name')
    form = OrganizationForm(request.POST or None, instance=organization)
    return render(request, "place_form.html", locals())



@permission_required('internship.is_internship_manager', raise_exception=True)
def organization_create(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    countries = Country.objects.order_by('name')
    form = OrganizationForm(request.POST or None)
    return render(request, "place_form.html", locals())



@permission_required('internship.is_internship_manager', raise_exception=True)
def student_choice(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    organization = get_object_or_404(models.organization.Organization, pk=organization_id)
    organization_choice = models.internship_choice.search(organization=organization)

    all_offers = models.internship_offer.search(organization=organization, cohort=cohort)
    all_speciality = models.internship_speciality.find_all(cohort)
    set_tabs_name(all_speciality)
    for al in all_offers:
        number_first_choice = len(models.internship_choice.search(organization=al.organization,
                                                                  speciality=al.speciality,
                                                                  choice=1))
        number_all_choice = len(models.internship_choice.search(organization=al.organization,
                                                                speciality=al.speciality))
        al.number_first_choice = number_first_choice
        al.number_all_choice = number_all_choice

    context = {
        'organization': organization,
        'organization_choice': organization_choice,
        'offers': all_offers,
        'specialities': all_speciality,
        'cohort': cohort,
    }
    return render(request, "place_detail.html", context)



@permission_required('internship.is_internship_manager', raise_exception=True)
def student_affectation(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    organization = get_object_or_404(models.organization.Organization, pk=organization_id)

    if cohort.is_parent:
        organizations = models.organization.Organization.objects.filter(
            cohort__in=cohort.subcohorts.all(), reference=organization.reference
        )
    else:
        organizations = [organization]

    affectations = models.internship_student_affectation_stat.search(organization__in=organizations)\
                                                             .order_by("student__person__last_name",
                                                                       "student__person__first_name")
    for a in affectations:
        a.email = ""
        a.adress = ""
        a.phone_mobile = ""
        internship_student_information = models.internship_student_information.search(
            person=a.student.person,
            cohort__in=[org.cohort for org in organizations]
        )
        _add_student_information(a, internship_student_information)
    periods = models.period.search(cohort=cohort)

    if cohort.is_parent:
        internships = models.internship_offer.search(
            organization__reference=organization.reference, cohort__in=cohort.subcohorts.all()
        )
    else:
        internships = models.internship_offer.search(organization__reference=organization.reference, cohort=cohort)

    all_speciality = get_all_specialities(internships)
    all_speciality = models.internship_speciality.set_speciality_unique(all_speciality)
    set_tabs_name(all_speciality)
    context = {
        'organization': organization,
        'affectations': affectations,
        'specialities': all_speciality,
        'periods': periods,
        'cohort': cohort,
    }
    return render(request, "place_detail_affectation.html", context)



@permission_required('internship.is_internship_manager', raise_exception=True)
def export_organisation_affectation_master(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    cohorts = cohort.subcohorts.all() if cohort.is_parent else [cohort]
    affec_by_specialties, organization = _get_affec_by_specialties_for_cohorts(cohorts, organization_id)
    return _export_xls_master(cohort, organization, affec_by_specialties)


def _get_affec_by_specialties_for_cohorts(cohorts, organization_id):
    organization = models.organization.get_by_id(organization_id)
    organizations = Organization.objects.filter(
        cohort__in=cohorts, reference=organization.reference
    )
    internships = models.internship_offer.search(organization__in=organizations)
    specialities = list({offer.speciality.name for offer in internships})
    specialities = sorted(specialities, key=lambda spec_name: spec_name)
    affec_by_specialties = [
        (internship_speciality, list(models.internship_student_affectation_stat.search(
            organization__in=organizations, speciality__name=internship_speciality)))
        for internship_speciality in specialities
    ]
    for speciality, affectations in affec_by_specialties:
        for affectation in affectations:
            affectation.email = ""
            affectation.adress = ""
            affectation.phone_mobile = ""
            affectation.master = ""
            internship_student_info = models.internship_student_information.search(person=affectation.student.person)
            master_allocation = models.master_allocation.search(
                cohort=affectation.organization.cohort,
                hospital=affectation.organization,
                specialty=affectation.speciality
            )
            _add_student_information(affectation, internship_student_info)
            if master_allocation:
                affectation.master = ", ".join(master_allocation.values_list('master_display_name', flat=True))
    return affec_by_specialties, organization



@permission_required('internship.is_internship_manager', raise_exception=True)
def export_hospital_affectation(request, cohort_id, organization_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    organization = models.organization.get_by_id(organization_id)
    return _export_xls_hospital(cohort, organization)


def _export_xls_master(cohort, organization, affections_by_specialities):
    if not affections_by_specialities:
        redirect_url = reverse('place_detail_student_affectation', kwargs={
            'cohort_id': cohort.id,
            'organization_id': organization.id,
        })
        return HttpResponseRedirect(redirect_url)
    else:
        virtual_workbook = organization_affectation_master.export_master_xls(cohort, organization,
                                                                             affections_by_specialities)
        return _export_xls(organization, virtual_workbook)


def _export_xls_hospital(cohort, organization):
    virtual_workbook = organization_affectation_hospital.export_hospital_xls(cohort, organization)
    return _export_xls(organization, virtual_workbook)


@set_download_cookie
def _export_xls(organization, virtual_workbook):
    response = HttpResponse(virtual_workbook,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name_parts = organization.name.strip().replace(' ', '_')
    file_name = "affectation_{}_{}.xlsx".format(str(organization.reference), file_name_parts)
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


def _format_address(person_address):
    return "{} - {} {} ({})".format(
        person_address.location,
        person_address.postal_code,
        person_address.city,
        person_address.country
    )


def _add_student_information(affectation, internship_student_information):
    if internship_student_information:
        informations = internship_student_information.first()
        person_address = informations.person.personaddress_set.first()
        affectation.email = informations.email
        affectation.adress = _format_address(person_address)
        affectation.phone_mobile = informations.phone_mobile
