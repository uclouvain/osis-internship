##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import render, get_object_or_404

from internship.forms.form_place_evaluation_item import PlaceEvaluationItemForm
from internship.models.cohort import Cohort
from internship.models.internship_place_evaluation_item import PlaceEvaluationItem


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    evaluation_items = PlaceEvaluationItem.objects.filter(cohort=cohort)
    return render(request, "place_evaluation.html", context={'cohort': cohort, 'evaluation_items': evaluation_items})


def internship_place_evaluation_item_edit(request, cohort_id, item_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    evaluation_item = PlaceEvaluationItem.objects.get(pk=item_id)
    form = PlaceEvaluationItemForm()
    return render(request, "place_evaluation_item_form.html", context={
        'cohort': cohort,
        'form': form,
        'evaluation_item': evaluation_item
    })

