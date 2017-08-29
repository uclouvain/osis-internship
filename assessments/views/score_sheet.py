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

from base import models as mdl
from reference import models as mdl_ref
from base.views import layout
from django.http import HttpResponse


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def offer_score_encoding_tab(request, offer_year_id):
    offer_year = mdl.offer_year.find_by_id(offer_year_id)
    countries = mdl_ref.country.find_all()
    is_program_manager = mdl.program_manager.is_program_manager(request.user, offer_year=offer_year)
    return layout.render(request, "offer/score_sheet_address_tab.html", locals())


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
def save_score_sheet_address(request, offer_year_id):
    if request.method == 'POST':
        offer_yr = mdl.offer_year.find_by_id(offer_year_id)
        offer_yr.recipient = request.POST.get('recipient')
        offer_yr.location = request.POST.get('location')
        offer_yr.postal_code = request.POST.get('postal_code')
        offer_yr.city = request.POST.get('city')
        country_id = request.POST.get('country')
        country = mdl_ref.country.find_by_id(country_id)
        offer_yr.country = country
        offer_yr.phone = request.POST.get('phone')
        offer_yr.fax = request.POST.get('fax')
        offer_yr.email = request.POST.get('email')
        offer_yr.save()
        data = "ok"
    else:
        data = "nok"

    return HttpResponse(data, content_type='text/plain')
