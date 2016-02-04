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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.models import *

def offers(request):
    academic_year = None
    faculty = None
    code = ""

    faculties = Structure.objects.all().order_by('acronym')
    academic_years = AcademicYear.objects.all().order_by('year')

    academic_year_calendar = AcademicCalendar.current_academic_year()
    if not academic_year_calendar is None:
        academic_year = academic_year_calendar.id
    return render(request, "offers.html", {'faculties':      faculties,
                                           'academic_year':  academic_year,
                                           'faculty':        faculty,
                                           'code':           code,
                                           'academic_years': academic_years,
                                           'offers':         [] ,
                                           'init':           "1"})


def offers_search(request):
    faculty = request.GET['faculty']
    academic_year = request.GET['academic_year']
    code = request.GET['code']

    faculties = Structure.objects.all().order_by('acronym')
    academic_years = AcademicYear.objects.all().order_by('year')

    if academic_year is None:
        academic_year_calendar = AcademicCalendar.current_academic_year()
        if not academic_year_calendar is None:
            academic_year = academic_year_calendar.id

    query = OfferYear.objects.filter(academic_year=int(academic_year))

    if not faculty is None and faculty != "*" :
        query = query.filter(structure=int(faculty))

    if not code is None and len(code) > 0  :
        query = query.filter(acronym__istartswith=code)

    return render(request, "offers.html", {'faculties':      faculties,
                                           'academic_year':  int(academic_year),
                                           'faculty':        int(faculty),
                                           'code':           code,
                                           'academic_years': academic_years,
                                           'offers':         query ,
                                           'init':           "0"})

def offer_read(request,offer_year_id):
    offer_year = OfferYear.objects.get(pk=offer_year_id)
    return render(request, "offer.html", {'offer':     offer_year})
