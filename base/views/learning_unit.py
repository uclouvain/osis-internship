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
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _

from attribution import models as mdl_attr
from base import models as mdl
from base.forms.learning_units import LearningUnitYearForm
from . import layout


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units(request):
    if request.GET.get('academic_year'):
        form = LearningUnitYearForm(request.GET)
    else:
        form = LearningUnitYearForm()
    found_learning_units = None
    if form.is_valid():
        found_learning_units = form.get_learning_units()
        _check_if_display_message(request, learning_units)

    context = _get_common_context_list_learning_unit_years()
    context.update({
        'form': form,
        'academic_years': mdl.academic_year.find_academic_years(),
        'learning_units': found_learning_units,
        'current_academic_year': mdl.academic_year.current_academic_year()
    })
    return layout.render(request, "learning_units.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_identification(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    tab_active = 'identification'
    return layout.render(request, "learning_unit/identification.html", locals())


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_formations(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    tab_active = 'formations'
    return layout.render(request, "learning_unit/formations.html", locals())


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_components(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    tab_active = 'components'
    return layout.render(request, "learning_unit/components.html", locals())


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_pedagogy(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    tab_active = 'pedagogy'
    return layout.render(request, "learning_unit/pedagogy.html", locals())


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_attributions(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    attributions = mdl_attr.attribution.search(learning_unit_year=learning_unit_year)
    tab_active = 'attributions'
    return layout.render(request, "learning_unit/attributions.html", locals())


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_proposals(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    tab_active = 'proposals'
    return layout.render(request, "learning_unit/proposals.html", locals())


def _check_if_display_message(request, learning_units):
    if not learning_units:
        messages.add_message(request, messages.WARNING, _('no_result'))


def _get_common_context_list_learning_unit_years():
    today = datetime.date.today()
    date_ten_years_before = today.replace(year=today.year-10)
    academic_years = mdl.academic_year.find_academic_years()\
                                      .filter(start_date__gte=date_ten_years_before)

    context = {
        'academic_years': academic_years
    }
    return context
