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
from base import models as mdl
from attribution import models as mdl_attr
from . import layout
from base.enums import learning_unit_year_type
from base.enums import learning_unit_year_status
from base.forms.learning_unit_year import LearningUnitYearForm

@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units(request):
    academic_yr = None
    acronym = ""

    academic_years = mdl.academic_year.find_academic_years()
    academic_yr_calendar = mdl.academic_year.current_academic_year()
    types = learning_unit_year_type.YEAR_TYPES
    status_choices = learning_unit_year_status.LEARNING_UNIT_YEAR_STATUS
    academic_years_all = "1"

    if academic_yr_calendar:
        academic_yr = academic_yr_calendar.id
    return layout.render(request, "learning_units.html", {'academic_year': academic_yr,
                                                          'acronym': acronym,
                                                          'academic_years': academic_years,
                                                          'types' : types,
                                                          'status_choices' : status_choices,
                                                          'academic_year_all' : academic_years_all,
                                                          'learning_units': [],
                                                          'init': "1"})

@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_search(request):
    """
    Learning units search
    """
    # criteria
    academic_year = request.GET['academic_year']
    acronym = request.GET['acronym']
    type = request.GET['type']
    status = request.GET['status']
    keyword = request.GET['keyword']
    types = learning_unit_year_type.YEAR_TYPES
    status_choices = learning_unit_year_status.LEARNING_UNIT_YEAR_STATUS
    academic_years = mdl.academic_year.find_academic_years()

    form = LearningUnitYearForm(request.GET)

    if form.is_valid():
        print("form valid!")
        print(form.cleaned_data)
        learning_unts = mdl.learning_unit_year.search(academic_year_id=academic_year,acronym=acronym,title=keyword,type=type,status=status)
    else:
        print("form NOT valid!")
        print(academic_year)
        #print( form.errors.as_data())
        learning_unts = None

    if academic_year==-1:
        academic_years_all='1'
    else:
        academic_years_all='0'


    return layout.render(request, "learning_units.html", {'academic_year': int(academic_year),
                                                          'acronym': acronym,
                                                          'type': type,
                                                          'academic_years': academic_years,
                                                          'types' : types,
                                                          'status_choices':status_choices,
                                                          'academic_year_all' : academic_years_all,
                                                          '0': learning_unts,
                                                          'form':form,
                                                          'init': "0"})


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_read(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    attributions = mdl_attr.attribution.search(learning_unit_year=learning_unit_year)
    enrollments = mdl.learning_unit_enrollment.find_by_learningunit_enrollment(learning_unit_year)
    is_program_manager = mdl.program_manager.is_program_manager(request.user)

    return layout.render(request, "learning_unit.html", {'learning_unit_year': learning_unit_year,
                                                         'attributions': attributions,
                                                         'enrollments': enrollments,
                                                         'is_program_manager': is_program_manager})
