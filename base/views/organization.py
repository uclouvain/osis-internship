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
from base.models import *
from base.forms import OrganizationForm


def organizations(request):
    organizations_list = Organization.find_all()
    return render(request, "organizations.html",
                          {'acronym' :      None,
                           'name'    :      None,
                           'organizations': organizations_list,
                           'init': "1"})


def organizations_search(request):
    acronym = request.GET['acronym']
    name = request.GET['name']
    if acronym is None and name is None:
        organizations_list = Organization.find_all()
    if acronym is None and not name is None:
        organizations_list = Organization.find_by_name(name)
    if not acronym is None and name is None:
        organizations_list = Organization.find_by_acronym(acronym)
    if not acronym is None and not name is None:
        organizations_list = Organization.find_by_acronym_name(acronym,name)

    return render(request, "organizations.html",
                          {'acronym' :      acronym,
                           'name' :         name,
                           'organizations': organizations_list,
                           'init': "0"})


def organization_read(request,id):
    organization = Organization.find_by_id(id)
    structures = organization.find_structure()
    return render(request, "organization.html", {'organization':  organization ,
                                                 'structures':    structures})


def organization_new(request):
    return organization_save(request,None)


def organization_save(request,id):
    form = OrganizationForm(data=request.POST)
    if id:
        organization = Organization.find_by_id(id)
    else:
        organization = Organization()

    #get the screen modifications
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

    organization_address = OrganizationAddress.find_by_organization(organization)
    organization_address_id  = None
    if organization_address is None:
        organization_address= OrganizationAddress()
        organization_address.organization = organization
    else:
        organization_address_id = organization_address.id

    if request.POST['address_label']:
        organization_address.label = request.POST['address_label']
    else:
        organization_address.label = None

    if request.POST['address_location']:
        organization_address.location = request.POST['address_location']
    else:
        organization_address.location = None

    if request.POST['address_postal_code']:
        organization_address.postal_code = request.POST['address_postal_code']
    else:
        organization_address.postal_code = None

    if request.POST['address_city']:
        organization_address.city = request.POST['address_city']
    else:
        organization_address.city = None

    if request.POST['address_country']:
        organization_address.country = request.POST['address_country']
    else:
        organization_address.country = None

    if form.is_valid():
        organization.save()
        organization_address.save()
        organizations_list = Organization.find_all()
        return render(request, "organizations.html",
                              {'acronym' :      None,
                               'name'    :      None,
                               'organizations': organizations_list,
                               'init': "0"})
    else:

        return render(request, "organization_form.html",
                              {'organization' : organization,
                               'organization_address_id' : organization_address_id,
                               'form' :         form})


def organization_edit(request, id):
    organization = Organization.find_by_id(id)
    organization_address_id = None
    organization_address = OrganizationAddress.find_by_organization(organization)
    if organization_address:
        organization_address_id = organization_address.id
    return render(request, "organization_form.html", {'organization':             organization,
                                                      'organization_address_id' : organization_address_id})


def organization_create(request):
    organization = Organization()
    return render(request, "organization_form.html", {'organization':     organization})