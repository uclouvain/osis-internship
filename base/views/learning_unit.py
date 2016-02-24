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

def learning_units(request):

    academic_year = None
    code = ""

    academic_years = AcademicYear.find_academic_years()
    academic_year_calendar = AcademicCalendar.current_academic_year()

    if not academic_year_calendar is None:
        academic_year = academic_year_calendar.id
    return render(request, "learning_units.html", {
                                           'academic_year':  academic_year,
                                           'code':           code,
                                           'academic_years': academic_years,
                                           'learning_units': [] ,
                                           'init':           "1"})

def learning_units_search(request):
    """
    Learning units search
    """
    #criteria
    academic_year = request.GET['academic_year']
    code = request.GET['code']

    academic_years = AcademicYear.find_academic_years()

    if academic_year is None:
        academic_year_calendar = AcademicCalendar.current_academic_year()
        if not academic_year_calendar is None:
            academic_year = academic_year_calendar.id

    learning_units = LearningUnitYear.find_learning_unit_years_by_academic_year(academic_year)

    if not code is None and len(code) > 0  :
        learning_units = learning_units.filter(acronym__icontains=code)

    return render(request, "learning_units.html", {'academic_year':  int(academic_year),
                                           'code':           code,
                                           'academic_years': academic_years,
                                           'learning_units': learning_units ,
                                           'init':           "0"})

def learning_unit_read(request,learning_unit_id):
    learning_unit_year = LearningUnitYear.find_learning_unit_year_by_id(learning_unit_id)
    return render(request, "learning_unit.html", {'learning_unit_year':    learning_unit_year})
