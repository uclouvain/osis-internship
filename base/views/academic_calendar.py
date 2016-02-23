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
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from base.models import *

def academic_calendars(request):
    academic_year = None
    academic_years = AcademicYear.find_academic_years()

    academic_year_calendar = AcademicCalendar.current_academic_year()
    if not academic_year_calendar is None:
        academic_year = academic_year_calendar.id
    academic_calendars = AcademicCalendar.find_by_academic_year(academic_year)
    return render(request, "academic_calendars.html", {'academic_year': academic_year,
                                           'academic_years': academic_years,
                                           'academic_calendars': academic_calendars ,
                                           'init': "1"})


def academic_calendars_search(request):
    academic_year = request.GET['academic_year']
    academic_years = AcademicYear.find_academic_years()

    if academic_year is None:
        academic_year_calendar = AcademicCalendar.current_academic_year()
        if not academic_year_calendar is None:
            academic_year = academic_year_calendar.id

    query = AcademicCalendar.find_by_academic_year(academic_year)

    return render(request, "academic_calendars.html", {
                                           'academic_year':  int(academic_year),
                                           'academic_years': academic_years,
                                           'academic_calendars': query ,
                                           'init':           "0"})


def academic_calendar_read(request,id):
    academic_calendar = AcademicCalendar.find_by_id(id)
    return render(request, "academic_calendar.html", {'academic_calendar':     academic_calendar})


def academic_calendar_save(request,id):
    academic_calendar = AcademicCalendar.find_by_id(id)
    academic_year=None
    academic_year_id = request.POST['academic_year']

    #get the screen modifications
    if academic_year_id:
        academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
        academic_calendar.academic_year = academic_year
    else:
        academic_calendar.academic_year = None
    academic_calendars = AcademicCalendar.find_by_academic_year(academic_year)    
    if request.POST['title']:
        academic_calendar.title = request.POST['title']
    else:
        academic_calendar.title = None

    if request.POST['start_date']:
        academic_calendar.start_date = datetime.strptime(request.POST['start_date'], '%d/%m/%Y')
    else:
        academic_calendar.start_date = None

    if request.POST['end_date']:
        academic_calendar.end_date = datetime.strptime(request.POST['end_date'], '%d/%m/%Y')
    else:
        academic_calendar.end_date = None
    #validate

    #save
    academic_calendar.save()

    return render(request, "academic_calendars.html", {
                                           'academic_year': academic_year,
                                           'academic_years': AcademicYear.find_academic_years(),
                                           'academic_calendars':academic_calendars,
                                           'init': "0"})

def academic_calendar_edit(request, id):
    academic_calendar = AcademicCalendar.find_by_id(id)
    academic_years = AcademicYear.find_academic_years()
    return render(request, "academic_calendar_form.html", {'academic_calendar':     academic_calendar,
                                                           'academic_years': academic_years})

def academic_calendar_delete(request, id):
    academic_calendar = AcademicCalendar.find_by_id(id)
    return render(request, "academic_calendar_form.html", {'academic_calendar':     academic_calendar})
