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
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from internship.forms.form_place_evaluation_item import PlaceEvaluationItemForm
from internship.models.cohort import Cohort
from internship.models.internship_place_evaluation import PlaceEvaluation
from internship.models.internship_place_evaluation_item import PlaceEvaluationItem
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.organization import Organization
from internship.models.period import get_effective_periods
from internship.utils.exporting import places_evaluations_xls
from osis_common.decorators.download import set_download_cookie


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
def internship_place_evaluation_config(request, cohort_id):
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(Prefetch(
            'placeevaluationitem_set',
            to_attr='evaluation_items'
        )),
        pk=cohort_id
    )

    periods = get_effective_periods(cohort_id)

    if request.POST:
        for period in periods:
            period.place_evaluation_active = period.name in request.POST.getlist('active_period')
            period.save()
        messages.add_message(request, messages.SUCCESS, _('Successfully saved place evaluations configuration'))

    return render(request, "place_evaluation_config.html", context={
        'cohort': cohort,
        'periods': periods,
    })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_place_evaluation_results(request, cohort_id):
    cohort = Cohort.objects.get(pk=cohort_id)
    affectations = InternshipStudentAffectationStat.objects.filter(organization__cohort=cohort).values_list(
        'pk', 'period_id', 'organization_id', 'speciality_id',
        'speciality__acronym', 'organization__reference', named=True
    )
    evaluations = PlaceEvaluation.objects.filter(
        affectation_id__in=[affectation.pk for affectation in affectations]
    ).values_list(
        'affectation__period_id', 'affectation__organization_id', 'affectation__speciality_id', named=True
    )

    periods = get_effective_periods(cohort_id).order_by('date_start')
    periods_items = {
        period.name: {
            'affectations': [affectation for affectation in affectations if affectation.period_id == period.pk],
            'evaluations': [
                evaluation for evaluation in evaluations if evaluation.affectation__period_id == period.pk
            ],
        } for period in periods
    }

    places = Organization.objects.filter(cohort=cohort, fake=False).order_by('reference')
    specialties = InternshipSpeciality.objects.filter(cohort=cohort).order_by('name')
    places_items = {
        f"{place.reference}{specialty.acronym}": {
            'affectations': [
                affectation for affectation in affectations
                if affectation.organization_id == place.pk
                if affectation.speciality_id == specialty.pk
            ],
            'evaluations': [
                evaluation for evaluation in evaluations
                if evaluation.affectation__organization_id == place.pk
                if evaluation.affectation__speciality_id == specialty.pk
            ],
        } for place in places for specialty in specialties
    }

    places_items = _filter_places_items_with_affectations(places_items)

    return render(request, "place_evaluation_results.html", context={
        'cohort': cohort,
        'evaluations': evaluations,
        'affectations': affectations,
        'periods_items': periods_items,
        'periods': periods,
        'places_items': places_items,
        'places': places,
        'specialties': specialties,
        'specialties_available_by_hospital': _get_specialties_available_by_hospital(affectations)
    })


def _filter_places_items_with_affectations(places_items):
    return {key: value for key, value in places_items.items() if value['affectations']}


def _get_specialties_available_by_hospital(affectations):
    organizations = affectations.values_list('organization__reference', flat=True).distinct('organization')
    return {
        organization: set(a.speciality__acronym for a in affectations if a.organization__reference == organization)
        for organization in organizations
    }


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
@set_download_cookie
def export_place_evaluation_results(request, cohort_id):
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(Prefetch(
            'placeevaluationitem_set',
            to_attr='evaluation_items'
        )),
        pk=cohort_id
    )
    affectations = InternshipStudentAffectationStat.objects.filter(organization__cohort=cohort)
    evaluations = PlaceEvaluation.objects.filter(affectation__in=affectations)
    workbook = places_evaluations_xls.export_xls_with_places_evaluations(cohort, evaluations)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = "places_evaluations_{}.xlsx".format(cohort.name.strip().replace(' ', '_'))
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


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
