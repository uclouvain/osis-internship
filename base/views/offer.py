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
import operator
from functools import reduce
from django.db import models

def offers(request):
    academic_yr = None
    faculty = None
    code = ""

    faculties = mdl.structure.find_structures()
    academic_years = mdl.academic_year.find_academic_years()

    academic_year_calendar = mdl.academic_year.current_academic_year()
    if academic_year_calendar:
        academic_yr = academic_year_calendar.id
    return render(request, "offers.html", {'faculties': faculties,
                                           'academic_year': academic_yr,
                                           'faculty': faculty,
                                           'code': code,
                                           'academic_years': academic_years,
                                           'offers': [],
                                           'init': "1"})


def offers_search(request):
    criterias = []
    faculty = request.GET['faculty']
    academic_yr = request.GET['academic_year']
    code = request.GET['code']

    faculties = mdl.structure.find_structures()
    academic_years = mdl.academic_year.find_academic_years()
    criteria_present = False

    if academic_yr and academic_yr != "*":
        criterias.append(models.Q(academic_year=academic_yr))
        criteria_present = True

    if faculty and faculty != "*":
        criterias.append(models.Q(structure=int(faculty)))
        criteria_present = True

    if code and len(code) > 0:
        criterias.append(models.Q(acronym__icontains=code))
        criteria_present = True

    message = None
    offer_years=None
    if not criteria_present :
        message = "%s" %  _('You must choose at least one criteria!')
    else:
        # on ne doit prendre que les offres racines (pas les finalités)
        criterias.append(models.Q(parent=None))
        offer_years = mdl.offer_year.OfferYear.objects.filter(reduce(operator.and_, criterias))
    if faculty is None or faculty == "*":
        faculty = None
    else:
        faculty = int(faculty)

    if academic_yr is None or academic_yr == "*":
        academic_yr = None
    else:
        academic_yr = int(academic_yr)

    return render(request, "offers.html", {'faculties':      faculties,
                                           'academic_year':  academic_yr,
                                           'faculty':        faculty,
                                           'code':           code,
                                           'academic_years': academic_years,
                                           'offer_years':    offer_years,
                                           'init':           "0",
                                           'message' :       message})


def offer_read(request, offer_year_id):
    offer_yr = mdl.offer_year.find_offer_year_by_id(offer_year_id)
    offer_yr_events = mdl.offer_year_calendar.find_offer_year_calendar(offer_yr)
    return render(request, "offer.html", {'offer_year': offer_yr,
                                          'offer_year_events': offer_yr_events})
