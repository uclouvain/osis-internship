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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from internship.forms.form_place_evaluation_item import PlaceEvaluationItemForm
from internship.models.cohort import Cohort
from internship.models.internship_place_evaluation_item import PlaceEvaluationItem


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation(request, cohort_id):
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(Prefetch(
            'placeevaluationitem_set',
            to_attr='evaluation_items'
        )),
        pk=cohort_id
    )
    return render(request, "place_evaluation.html", context={'cohort': cohort})


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_item_new(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    form = PlaceEvaluationItemForm()

    # force options to have 1 empty item
    form.instance.options = ['']

    if request.POST:
        form, saved = internship_place_evaluation_item_save(request, cohort_id)
        if saved:
            messages.add_message(request, messages.SUCCESS, _('Successfully saved item {}').format(form.instance))
            return redirect('place_evaluation', cohort_id=cohort_id)

    return render(request, "place_evaluation_item_form.html", context={
        'cohort': cohort,
        'form': form,
    })


@login_required
@transaction.atomic
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_item_save(request, cohort_id, item=None):
    form = PlaceEvaluationItemForm(request.POST, instance=item)
    if form.is_valid():
        item = form.save(commit=False)
        item.options = request.POST.getlist('options')
        item.cohort_id = cohort_id
        item.save()
        return form, True
    return form, False


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_item_edit(request, cohort_id, item_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    evaluation_item = PlaceEvaluationItem.objects.get(pk=item_id)
    form = PlaceEvaluationItemForm(instance=evaluation_item)

    if request.POST:
        form, saved = internship_place_evaluation_item_save(request, cohort_id, evaluation_item)
        if saved:
            messages.add_message(request, messages.SUCCESS, _('Successfully saved item {}').format(form.instance))
            return redirect('place_evaluation', cohort_id=cohort_id)

    return render(request, "place_evaluation_item_form.html", context={
        'cohort': cohort,
        'form': form,
        'item': evaluation_item
    })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_item_delete(request, cohort_id, item_id):
    item = PlaceEvaluationItem.objects.get(pk=item_id)
    item.delete()
    messages.add_message(request, messages.SUCCESS, message=_('Successfully deleted item {}').format(item))
    return redirect('place_evaluation', cohort_id=cohort_id)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_item_move_up(request, cohort_id, item_id):
    item = PlaceEvaluationItem.objects.get(pk=item_id)
    item.up()
    return redirect('place_evaluation', cohort_id=cohort_id)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_item_move_down(request, cohort_id, item_id):
    item = PlaceEvaluationItem.objects.get(pk=item_id)
    item.down()
    return redirect('place_evaluation', cohort_id=cohort_id)
