##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from django.contrib.auth.decorators import login_required, permission_required
from base.forms.academic_calendar import AcademicCalendarForm
from base import models as mdl
from . import layout


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendars(request):
    academic_year = None
    academic_years = mdl.academic_year.find_academic_years()

    academic_year_calendar = mdl.academic_year.current_academic_year()
    if academic_year_calendar:
        academic_year = academic_year_calendar.id
    academic_calendars = mdl.academic_calendar.find_academic_calendar_by_academic_year(academic_year)
    return layout.render(request, "academic_calendars.html", {'academic_year': academic_year,
                                                              'academic_years': academic_years,
                                                              'academic_calendars': academic_calendars})


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendars_search(request):
    academic_year = request.GET['academic_year']
    academic_years = mdl.academic_year.find_academic_years()

    if academic_year is None:
        academic_year_calendar = mdl.academic_year.current_academic_year()
        if academic_year_calendar:
            academic_year = academic_year_calendar.id

    query = mdl.academic_calendar.find_academic_calendar_by_academic_year(academic_year)

    return layout.render(request, "academic_calendars.html", {
        'academic_year': int(academic_year),
        'academic_years': academic_years,
        'academic_calendars': query})

@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_read(request, id):
    academic_calendar = mdl.academic_calendar.find_academic_calendar_by_id(id)
    return layout.render(request, "academic_calendar.html", {'academic_calendar': academic_calendar})


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_new(request):
    return academic_calendar_save(request, None)


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_save(request, academic_calendar_id):
    academic_calendar = None
    if academic_calendar_id:
        academic_calendar = mdl.academic_calendar.find_academic_calendar_by_id(academic_calendar_id)
    form = AcademicCalendarForm(request.POST, instance=academic_calendar)

    academic_years = mdl.academic_year.find_academic_years()
    if form.is_valid():
        form.save()
        return layout.render(request, "academic_calendars.html", {'academic_year': form.academic_year,
                                                                  'academic_years': academic_years,
                                                                  'form': form})
    else:
        return layout.render(request, "academic_calendar_form.html", {'academic_years': academic_years,
                                                                      'form': form})


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_edit(request, id):
    academic_calendar = mdl.academic_calendar.find_academic_calendar_by_id(id)
    form = AcademicCalendarForm(instance=academic_calendar)
    academic_years = mdl.academic_year.find_academic_years()
    return layout.render(request, "academic_calendar_form.html", {'form': form, 'academic_years': academic_years})


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_create(request):
    academic_calendar = mdl.academic_calendar.AcademicCalendar()
    academic_years = mdl.academic_year.find_academic_years()
    return layout.render(request, "academic_calendar_form.html", {'academic_calendar': academic_calendar,
                                                                  'academic_year': None,
                                                                  'academic_years': academic_years})
