##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import pickle

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from internship.forms.score import StudentsFilterForm
from internship.models.cohort import Cohort
from internship.models.internship_score import InternshipScore
from internship.models.internship_score_mapping import InternshipScoreMapping
from internship.models.period import Period
from internship.utils.importing import import_scores
from internship.views.common import get_object_list


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def scores_encoding(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')

    search_form = StudentsFilterForm(request.GET)
    students_list = []
    if search_form.is_valid():
        students_list = search_form.get_students(cohort=cohort)

    students = get_object_list(request, students_list)

    scores = InternshipScore.objects.filter(cohort=cohort).select_related(
        'student__person', 'period', 'cohort'
    ).order_by('student__person__last_name')

    mapping = InternshipScoreMapping.objects.filter(cohort=cohort).select_related(
        'period'
    )

    _match_scores_with_students(cohort, periods, list(scores), students)

    _map_numeric_score(mapping, students)

    context = {'cohort': cohort, 'periods': periods, 'students': students, 'search_form': search_form}
    return render(request, "scores.html", context=context)


def _map_numeric_score(mapping, students):
    # compute student grades in numerical value based on mapping for each period
    for student in students:
        periods_scores = {}
        _map_student_score(mapping, periods_scores, student)
        student.periods_scores = periods_scores


def _map_student_score(mapping, periods_scores, student):
    for item in student.scores:
        period, scores = item
        period_score = _process_evaluation_grades(mapping, period, scores)
        periods_scores.update({period: period_score})


def _process_evaluation_grades(mapping, period, scores):
    period_score = 0
    effective_apd_count = 0
    for index, note in enumerate(scores):
        if note in ['A', 'B', 'C', 'D']:
            effective_apd_count += 1
            mapped_note = list(filter(_get_mapping_score(period, index + 1), list(mapping)))
            if mapped_note:
                period_score += vars(mapped_note[0])['score_{}'.format(note)]
    return period_score/effective_apd_count if effective_apd_count else 0


def _match_scores_with_students(cohort, periods, scores_list, students):
    # append scores for each period to each students
    for student in students.object_list:
        student.scores = []
        for period in periods:
            student_scores = list(filter(_filter_scores(student, cohort, period), scores_list))
            _append_period_scores_to_student(period, student, student_scores)


def _filter_scores(student, cohort, period):
    return lambda x: x.student.person == student.person and x.cohort == cohort and x.period.name == period.name


def _get_mapping_score(period, apd):
    return lambda x: x.period.name == period and x.apd == apd


def _append_period_scores_to_student(period, student, student_scores):
    if student_scores:
        scores = student_scores[0].get_scores()
        student.scores += (period.name, scores),


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def upload_scores(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    _upload_file(request, cohort)
    return HttpResponseRedirect(reverse('internship_scores_encoding', kwargs={'cohort_id': cohort.id}))


def _upload_file(request, cohort):
    if request.method == 'POST':
        file_name = request.FILES['file_upload']
        period = request.POST['period']
        if file_name and ".xlsx" not in str(file_name):
            messages.add_message(request, messages.ERROR, _('File extension must be .xlsx'))
        else:
            import_scores.import_xlsx(cohort, file_name, period)
