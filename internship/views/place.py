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
from django.contrib.auth.decorators import login_required
from internship.models import Organization, OrganizationAddress


@login_required
def internships_places(request):
    # First get the value of the option for the sort
    if request.method == 'GET':
        city_sort_get = request.GET.get('city_sort')

    # Second, import all the organizations with their address(es if they have more than one)
    organizations = Organization.find_by_type("service partner", order_by=['reference'])
    if organizations:
        for organization in organizations:
            organization.address = ""
            address = OrganizationAddress.find_by_organization(organization)
            if address:
                organization.address = address

    # Next, if there is a value for the sort, browse all the organizations and put which have the same city
    # in the address than the sort option
    l_organizations = []
    if city_sort_get and city_sort_get != "0":
        index = 0
        for orga in organizations:
            flag_del = 1
            if orga.address:
                for a in orga.address:
                    if a.city == city_sort_get:
                        flag_del = 0
                        break
            if flag_del == 0:
                l_organizations.append(orga)
            index += 1
    else:
        l_organizations = organizations

    # Create the options for the selected list, delete dubblons
    organization_addresses = []
    for orga in organizations:
        for a in orga.address:
            organization_addresses.append(a.city)
    organization_addresses = list(set(organization_addresses))
    organization_addresses.sort()

    return render(request, "places.html", {'section': 'internship',
                                           'all_organizations': l_organizations,
                                           'all_addresses': organization_addresses,
                                           'city_sort_get': city_sort_get})

def organizations_search(request):
    organizations = mdl.organization.search(acronym=request.GET['acronym'],
                                            name=request.GET['name'],
                                            type=request.GET['type_choices'])

    return layout.render(request, "organizations.html", {'organizations': organizations,
                                                         'types': mdl.organization.ORGANIZATION_TYPE})


def organization_read(request, organization_id):
    organization = mdl.organization.find_by_id(organization_id)
    structures = mdl.structure.find_by_organization(organization)
    organization_addresses = mdl.organization_address.find_by_organization(organization)
    return layout.render(request, "organization.html", {'organization': organization,
                                                        'organization_addresses': organization_addresses,
                                                        'structures': structures})


def organization_new(request):
    return organization_save(request, None)


def organization_save(request, organization_id):
    form = OrganizationForm(data=request.POST)
    if organization_id:
        organization = mdl.organization.find_by_id(organization_id)
    else:
        organization = mdl.organization.Organization()

    # get the screen modifications
    if request.POST['acronym']:
        organization.acronym = request.POST['acronym']
    else:
        organization.acronym = None

    if request.POST['name']:
        organization.name = request.POST['name']
    else:
        organization.name = None

    if request.POST['website']:
        organization.website = request.POST['website']
    else:
        organization.website = None

    if request.POST['reference']:
        organization.reference = request.POST['reference']
    else:
        organization.reference = None

    if request.POST['type_choices']:
        organization.type = request.POST['type_choices']
    else:
        organization.type = None

    if form.is_valid():
        organization.save()
        return organization_read(request, organization.id)
    else:

        return layout.render(request, "organization_form.html", {'organization': organization,
                                                                 'form': form})


def organization_edit(request, organization_id):
    organization = mdl.organization.find_by_id(organization_id)
    return layout.render(request, "organization_form.html", {'organization': organization,
                                                             'types': mdl.organization.ORGANIZATION_TYPE})


def organization_create(request):
    organization = mdl.organization.Organization()
    return layout.render(request, "organization_form.html", {'organization': organization,
                                                             'types': mdl.organization.ORGANIZATION_TYPE})
