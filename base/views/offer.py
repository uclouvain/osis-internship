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

from base import models as mdl
from django.utils.translation import ugettext_lazy as _


def offers(request):
    academic_yr = None
    code = ""

    faculties = mdl.structure.find_by_type('FACULTY')
    academic_years = mdl.academic_year.find_academic_years()

    academic_year_calendar = mdl.academic_year.current_academic_year()
    if academic_year_calendar:
        academic_yr = academic_year_calendar.id
    return render(request, "offers.html", {'faculties': faculties,
                                           'academic_year': academic_yr,
                                           'code': code,
                                           'academic_years': academic_years,
                                           'offers': [],
                                           'init': "1"})


def offers_search(request):
    entity_acronym = request.GET['entity_acronym']

    academic_yr = None
    if request.GET['academic_year']:
        academic_yr = request.GET['academic_year']
    acronym = request.GET['code']

    faculties = mdl.structure.find_by_type('FACULTY')
    academic_years = mdl.academic_year.find_academic_years()

    message = None
    offer_years = None
    bad_criteria=False
    if entity_acronym is None and academic_yr is None and acronym is None :
        message = "%s" % _('You must choose at least one criteria!')
    else:
        entity = None
        if entity_acronym:
            entity = mdl.structure.find_by_acronym(entity_acronym)
            if entity is None:
                message = "%s" % _('Invalid value for the entity\'s criteria!')
                entity_acronym = None
                bad_criteria=True

        if not bad_criteria:
            offer_years = mdl.offer_year.search_root_offers(entity=entity, academic_yr=academic_yr, acronym=acronym)

    if academic_yr is None :
        academic_yr = None
    else:
        academic_yr = int(academic_yr)
    return render(request, "offers.html", {'faculties':       faculties,
                                           'academic_year':   academic_yr,
                                           'entity_acronym': entity_acronym,
                                           'code':            acronym,
                                           'academic_years':  academic_years,
                                           'offer_years':     offer_years,
                                           'init':            "0",
                                           'message':         message})


def offer_read(request, offer_year_id):
    offer_yr = mdl.offer_year.find_offer_year_by_id(offer_year_id)
    offer_yr_events = mdl.offer_year_calendar.find_offer_year_calendar(offer_yr)
    return render(request, "offer.html", {'offer_year': offer_yr,
                                          'offer_year_events': offer_yr_events})
