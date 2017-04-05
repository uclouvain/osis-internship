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
import operator

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render

from internship import models as mdl_internship
from internship.forms.organization_address_form import OrganizationAddressForm
from internship.forms.organization_form import OrganizationForm
from internship.models.cohort import Cohort
from internship.models.organization import Organization
from internship.models.organization_address import OrganizationAddress
from internship.utils import export_utils, export_utils_pdf
from internship.views.internship import get_all_specialities, set_tabs_name


def sort_organizations(sort_organizations):
    """
        Function to sort the organization by the reference
        Param:
            sort_organizations : list of organizations to sort
        Get the reference of the organization, transform and sort by the int key
        Recreate the list with the reference research
    """
    tab = []
    number_ref = []
    for sort_organization in sort_organizations:
        if sort_organization is not None:
            number_ref.append(sort_organization.reference)
    number_ref=sorted(number_ref, key=int)
    for i in number_ref:
        organization = mdl_internship.organization.search(reference=i)
        tab.append(organization[0])
    return tab


def set_organization_address(organizations):
    """
        Function to set the organization address to the organization
        Param:
            organizations : list of organizations to get the address
        Get the address in the OrganizationAddress table and put it
        Get also the number of student of choose this organization for their internship
    """
    for organization in organizations:
        organization.address = ""
        organization.student_choice = 0
        address = mdl_internship.organization_address.search(organization = organization)
        if address:
            organization.address = address
        organization.student_choice = len(mdl_internship.internship_choice.search(organization=organization))


def sorted_organization(sort_organizations, sort_city):
    """
        Function to sort the organization by the city sent by the POST form
        Param:
            sort_organizations : list of organizations to sort
            sort_city : city send
        Check in the list of organization if the city have the same that the sort_city
        if yes, keep it in a list and return this list
    """
    tab=[]
    index = 0
    for sort_organization in sort_organizations:
        flag_del = 1
        if sort_organization.address:
            for a in sort_organization.address:
                if a.city == sort_city:
                    flag_del = 0
                    break
        if flag_del == 0:
            tab.append(sort_organization)
        index += 1
    return tab


def get_cities(organizations):
    """
        Function to get the cities of organizations
        Param:
            organizations : list of organizations to extract the city
        Put in an array the city of the organizations.
        Sort and delete dublons in this array and return it
    """
    tab = []
    for organization in organizations:
        for a in organization.address:
            tab.append(a.city)
    tab = list(set(tab))
    tab.sort()
    return tab


def set_speciality_unique(specialities):
    specialities_size = len(specialities)
    for element in specialities:
        name = element.name.split()
        size = len(name)
        if name[size - 1].isdigit():
            temp_name = ""
            for x in range(0, size - 1):
                temp_name += name[x] + " "
            element.name = temp_name

    item_deleted = 0
    for x in range(1, specialities_size):
        if specialities[x - 1 - item_deleted] != 0:
            if specialities[x].name == specialities[x - 1 - item_deleted].name:
                specialities[x] = 0
                item_deleted += 1

    specialities = [x for x in specialities if x != 0]
    return specialities

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_places(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    # Get the value of the option for the sort
    city_sort_get = "0"
    if request.method == 'GET':
        city_sort_get = request.GET.get('city_sort')

    organizations = Organization.objects.prefetch_related('addresses') \
        .filter(type='service partner', cohort=cohort) \
        .order_by('reference')

    if city_sort_get and city_sort_get != '0':
        organizations = organizations.filter(address__city=city_sort_get)

    addresses = OrganizationAddress.objects.filter(organization__type='service partner') \
                .distinct('city').order_by('city')

    cities = map(operator.attrgetter('city'), addresses)

    context = {
        'section': 'internship',
        'all_organizations': organizations,
        'all_addresses': cities,
        'city_sort_get': city_sort_get,
        'cohort': cohort,
    }
    return render(request, "places.html", context)

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def place_save(request, cohort_id, organization_id, organization_address_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    if organization_id:
        organization = mdl_internship.organization.find_by_id(organization_id)
    else :
        mdl_internship.organization.Organization.objects.filter(reference=request.POST.get('reference')).delete()
        mdl_internship.organization_address.OrganizationAddress.objects.filter(organization__reference=request.POST.get('reference')).delete()
        organization = mdl_internship.organization.Organization()

    form = OrganizationForm(data=request.POST, instance=organization)
    if form.is_valid():
        form.save()

    if organization_address_id:
        organization_address = mdl_internship.organization_address.find_by_id(organization_address_id)
    else:
        organization_address = mdl_internship.organization_address.OrganizationAddress()

    form_address = OrganizationAddressForm(data=request.POST, instance=organization_address)
    if form_address.is_valid():
        form_address.save()

    context = {
        'organization': organization,
        'organization_address': organization_address,
        'form': form,
        'cohort': cohort,
    }
    return render(request, "place_form.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def organization_new(request, cohort_id):
    return place_save(request, cohort_id, None, None)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def organization_edit(request, cohort_id, organization_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    organization = mdl_internship.organization.find_by_id(organization_id)
    organization_address = mdl_internship.organization_address.search(organization = organization)
    context = {
        'organization': organization,
        'organization_address': organization_address.first(),
        'cohort': cohort,
    }
    return render(request, "place_form.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def organization_create(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    organization = mdl_internship.organization.Organization(cohort=cohort)
    context = {
        'organization': organization,
        'cohort': cohort
    }
    return render(request, "place_form.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_choice(request, cohort_id, organization_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    organization = get_object_or_404(Organization, pk=organization_id)
    organization_choice = mdl_internship.internship_choice.search(organization__reference=organization.reference)

    all_offers = mdl_internship.internship_offer.search(organization=organization)
    all_speciality = mdl_internship.internship_speciality.find_all()
    set_tabs_name(all_speciality)
    for al in all_offers:
        number_first_choice = len(mdl_internship.internship_choice.search(organization=al.organization,
                                                          speciality=al.speciality,
                                                          choice=1))
        number_all_choice = len(mdl_internship.internship_choice.search(organization=al.organization,
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


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_affectation(request, cohort_id, organization_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    # TODO: get_object_or_404(Organization, pk=organization_id, cohort__id=cohort_id)
    organization = get_object_or_404(Organization, pk=organization_id)

    affectations = mdl_internship.internship_student_affectation_stat.search(organization=organization).order_by("student__person__last_name","student__person__first_name")

    for a in affectations:
        a.email = ""
        a.adress = ""
        a.phone_mobile = ""
        internship_student_information= mdl_internship.internship_student_information.search(person=a.student.person)
        if internship_student_information:
            informations = internship_student_information.first()
            a.email = informations.email
            a.adress = informations.location + " " + informations.postal_code + " " + informations.city
            a.phone_mobile = informations.phone_mobile
    periods = mdl_internship.period.search()

    internships = mdl_internship.internship_offer.search(organization = organization)
    all_speciality = get_all_specialities(internships)
    all_speciality = set_speciality_unique(all_speciality)
    set_tabs_name(all_speciality)
    context = {
        'organization': organization,
        'affectations': affectations,
        'specialities': all_speciality,
        'periods': periods,
        'cohort': cohort,
    }
    return render(request, "place_detail_affectation.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def export_xls(request, cohort_id, organization_id, speciality_id):
    # FIXME: use the cohort and the organization, to be sure we use the right organization and the right cohort.
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    organization = mdl_internship.organization.find_by_id(organization_id)
    speciality = mdl_internship.internship_speciality.find_by_id(speciality_id)
    if speciality:
        speciality_groups = [group_member.group for group_member
                             in mdl_internship.internship_speciality_group_member.find_by_speciality(speciality)]
        specialities = [group_member.speciality for group_member in
                        mdl_internship.internship_speciality_group_member.find_distinct_specialities_by_groups(speciality_groups)]
        specialities = sorted(specialities, key=lambda spec: spec.order_postion)
        affection_by_specialities = [(internship_speciality,
                                      mdl_internship.internship_student_affectation_stat.search(organization=organization,
                                                                              speciality=internship_speciality))
                                     for internship_speciality in specialities]
    else:
        affection_by_specialities = []

    for speciality, affectations in affection_by_specialities:
        for affectation in affectations:
            affectation.email = ""
            affectation.adress = ""
            affectation.phone_mobile = ""
            affectation.master = ""
            internship_student_information = mdl_internship.internship_student_information.search(person=affectation.student.person)
            internship_offer = mdl_internship.internship_offer.search(organization=affectation.organization, speciality=affectation.speciality)
            if internship_student_information:
                informations = internship_student_information.first()
                affectation.email = informations.email
                affectation.adress = informations.location + " " + informations.postal_code + " " + informations.city
                affectation.phone_mobile = informations.phone_mobile
            if internship_offer:
                offer = internship_offer.first()
                affectation.master = offer.master
    file_name = speciality.acronym.strip().replace(' ', '_')
    return export_utils.export_xls(cohort, organization, affection_by_specialities, file_name)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def export_organisation_affectation_as_xls(request, cohort_id, organization_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    organization = mdl_internship.organization.find_by_id(organization_id)
    internships = mdl_internship.internship_offer.search(organization = organization)
    specialities = list({offer.speciality for offer in internships})
    specialities = sorted(specialities, key=lambda spec: spec.order_postion)
    affection_by_specialities = [(internship_speciality,
                                  list(mdl_internship.internship_student_affectation_stat.search(organization=organization,
                                                                          speciality=internship_speciality)))
                                 for internship_speciality in specialities]
    for speciality, affectations in affection_by_specialities:
        for affectation in affectations:
            affectation.email = ""
            affectation.adress = ""
            affectation.phone_mobile = ""
            affectation.master = ""
            internship_student_information = mdl_internship.internship_student_information.search(person=affectation.student.person)
            internship_offer = mdl_internship.internship_offer.search(organization=affectation.organization, speciality = affectation.speciality)
            if internship_student_information:
                informations = internship_student_information.first()
                affectation.email = informations.email
                affectation.adress = informations.location + " " + informations.postal_code + " " + informations.city
                affectation.phone_mobile = informations.phone_mobile
            if internship_offer:
                offer = internship_offer.first()
                affectation.master = offer.master
    file_name = organization.name.strip().replace(' ', '_')
    return export_utils.export_xls(cohort, organization, affection_by_specialities, file_name)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def export_pdf(request, organization_id, speciality_id):
    organization = mdl_internship.organization.find_by_id(organization_id)
    speciality = mdl_internship.internship_speciality.find_by_id(speciality_id)
    affectations = mdl_internship.internship_student_affectation_stat.search(organization=organization, speciality=speciality)
    for a in affectations:
        a.email = ""
        a.adress = ""
        a.phone_mobile = ""
        internship_student_information = mdl_internship.internship_student_information.search(person=a.student.person)
        if internship_student_information:
            informations = internship_student_information.first()
            a.email = informations.email
            a.adress = informations.location + " " + informations.postal_code + " " + informations.city
            a.phone_mobile = informations.phone_mobile
    return export_utils_pdf.print_affectations(organization_id, affectations)
