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
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict


TAB_IDENTIFICATION = 0
TAB_TRAININGS = 1
TAB_COMPONENTS = 2
TAB_EDUCATIONAL_INFORMATION = 3
TAB_ATTRIBUTIONS = 4
TAB_PROPOSAL = 5


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units(request):
    academic_yr = None
    code = ""

    academic_years = mdl.academic_year.find_academic_years()
    academic_yr_calendar = mdl.academic_year.current_academic_year()

    if academic_yr_calendar:
        academic_yr = academic_yr_calendar.id
    return layout.render(request, "learning_units.html", {'academic_year': academic_yr,
                                                          'code': code,
                                                          'academic_years': academic_years,
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
    code = request.GET['code']
    if academic_year is None:
        academic_year_calendar = mdl.academic_year.current_academic_year()
        if academic_year_calendar:
            academic_year = academic_year_calendar.id

    learning_unts = mdl.learning_unit_year.search(academic_year_id=academic_year,acronym=code)
    academic_years = mdl.academic_year.find_academic_years()

    return layout.render(request, "learning_units.html", {'academic_year': int(academic_year),
                                                          'code': code,
                                                          'academic_years': academic_years,
                                                          'learning_units': learning_unts,
                                                          'init': "0"})


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_read(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    attributions = mdl_attr.attribution.search(learning_unit_year=learning_unit_year)
    enrollments = mdl.learning_unit_enrollment.find_by_learningunit_enrollment(learning_unit_year)
    is_program_manager = mdl.program_manager.is_program_manager(request.user)

    return layout.render(request, "learning_unit/identification.html", {
        'learning_unit_year': learning_unit_year,
        'tab_active': TAB_IDENTIFICATION,
        'data_tab': get_tabs()})


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def detail(request, learning_unit_year_id, tab):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    data = {'learning_unit_year': learning_unit_year,
            'tab_active': tab,
            'data_tab': get_tabs()}

    mapping = {TAB_IDENTIFICATION: identification_detail,
               TAB_TRAININGS:training_detail,
               TAB_COMPONENTS: components_detail,
               TAB_EDUCATIONAL_INFORMATION: educational_information_detail,
               TAB_ATTRIBUTIONS: attributions_detail,
               TAB_PROPOSAL: proposal_detail}

    function = mapping.get(int(tab))
    if function:
        return function(request, data)

    return layout.render(request, "learning_unit/identification.html", data)

def identification_detail(request, data):
    return layout.render(request, "learning_unit/identification.html", data)


def training_detail(request, data):
    return layout.render(request, "learning_unit/trainings.html", data)


def components_detail(request, data):
    return layout.render(request, "learning_unit/components.html", data)


def educational_information_detail(request, data):
    return layout.render(request, "learning_unit/educational_information.html", data)


def attributions_detail(request, data):
    learning_unit_year = data['learning_unit_year']
    attributions = mdl_attr.attribution.search(learning_unit_year=learning_unit_year)
    data.update({'attributions': attributions})
    return layout.render(request, "learning_unit/attributions.html", data)


def proposal_detail(request, data):
    return layout.render(request, "learning_unit/proposal.html", data)


def get_tabs():
    #  Helps to construct tab pannel
    tabs_order_and_label = {'0': _('identification'),
                            '1': _('trainings'),
                            '2': _('components'),
                            '3': _('educational_information'),
                            '4': _('tutor_attributions'),
                            '5': _('proposal')}

    return OrderedDict(sorted(tabs_order_and_label.items(), key=lambda t: t[0]))




