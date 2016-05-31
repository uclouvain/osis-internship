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
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ungettext
from openpyxl import load_workbook
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from internship.models import Organization, OrganizationAddress
from internship.forms import OrganizationForm
from base import models as mdl


@login_required
def upload_places_file(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        file_name = request.FILES['file']
        if file_name is not None:
            if ".xls" not in str(file_name):
                messages.add_message(request, messages.ERROR, _('file_must_be_xls'))
            else:
                __save_xls_scores(request, file_name, request.user)

    return HttpResponseRedirect(reverse('internships_places'))


def __save_xls_scores(request, file_name, user):
    workbook = load_workbook(file_name, read_only=True)
    worksheet = workbook.active
    form = OrganizationForm(request)
    col_reference = 0
    col_name = 1
    col_address = 2
    col_postal_code = 3
    col_city = 4
    col_country = 5
    col_url = 7

    # Iterates over the lines of the spreadsheet.
    for count, row in enumerate(worksheet.rows):
        new_score = False
        if row[col_reference].value is None \
                or row[col_reference].value == 0 \
                or not _is_registration_id(row[col_reference].value):
            continue

        place = Organization.search(reference=row[col_reference].value)
        if place :
            organization = Organization.find_by_id(place[0].id)
        else:
            organization = Organization()

        if row[col_reference].value:
            ref = ""
            if row[col_reference].value < 10 :
                ref = "0"+str(row[col_reference].value)
            else :
                ref = str(row[col_reference].value)
            organization.reference = ref
        else:
            organization.reference = None

        if row[col_name].value:
            organization.name = row[col_name].value
            organization.acronym = row[col_name].value[:14]
        else:
            organization.name = None
            organization.acronym = None

        if row[col_url].value:
            organization.website = row[col_url].value
        else:
            organization.website = ""

        organization.type = "service partner"

        organization.save()

        if place :
            organization_address = OrganizationAddress.find_by_organization(organization)
            if not organization_address:
                organization_address = OrganizationAddress()
        else :
            organization_address = OrganizationAddress()

        organization_address.organization = organization
        if organization:
            organization_address.label = "Addr"+organization.name[:14]
        else:
            organization_address.label = " "

        if row[col_address].value:
            organization_address.location = row[col_address].value
        else:
            organization_address.location = " "

        if row[col_postal_code].value:
            organization_address.postal_code = row[col_postal_code].value
        else:
            organization_address.postal_code = " "

        if row[col_city].value:
            organization_address.city = row[col_city].value
        else:
            organization_address.city = " "

        if row[col_country].value:
            organization_address.country = row[col_country].value
        else:
            organization_address.country = " "

        organization_address.save()

def _is_registration_id(registration_id):
    try:
        int(registration_id)
        return True
    except ValueError:
        return False
