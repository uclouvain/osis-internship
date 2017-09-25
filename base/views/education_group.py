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
from . import layout


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_groups(request):
    academic_yr = None
    academic_years = mdl.academic_year.find_academic_years()

    academic_year_calendar = mdl.academic_year.current_academic_year()
    if academic_year_calendar:
        academic_yr = academic_year_calendar.id
    return layout.render(request, "education_groups.html", {'academic_year': academic_yr,
                                                  'academic_years': academic_years,
                                                  'education_group_years': [],
                                                  'init': "1"})


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_groups_search(request):
    entity = request.GET['entity_acronym']
    academic_yr = None
    if request.GET.get('academic_year', None):
        academic_yr = int(request.GET['academic_year'])
    acronym = request.GET['code']

    academic_years = mdl.academic_year.find_academic_years()

    education_group_years = get_education_group_years(academic_yr, acronym, entity)

    return layout.render(request, "education_groups.html", {'academic_year': academic_yr,
                                                  'entity_acronym': entity,
                                                  'code': acronym,
                                                  'academic_years': academic_years,
                                                  'education_group_years': education_group_years,
                                                  'init': "0"})


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_group_read(request, education_group_year_id):
    return _education_group_identification_tab(request, education_group_year_id)


def _education_group_identification_tab(request, education_group_year_id):
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)
    return layout.render(request, "education_group/tab_identification.html", locals())


def get_education_group_years(academic_yr, acronym, entity):
    if entity:
        education_group_year_entitys = []
        education_group_years = mdl.education_group_year.search(academic_yr=academic_yr, acronym=acronym)
        for education_group_yr in education_group_years:
            if education_group_yr.management_entity and education_group_yr.management_entity.acronym.upper() == entity.upper():
                education_group_year_entitys.append(education_group_yr)
        return education_group_year_entitys
    else:
        return mdl.education_group_year.search(academic_yr=academic_yr, acronym=acronym)
