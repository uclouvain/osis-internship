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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from internship.models.cohort import Cohort
from internship.models.internship_score import InternshipScore
from internship.models.internship_score_mapping import InternshipScoreMapping
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.period import Period
from internship.utils.importing import import_scores


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def scores_encoding(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')

    students = InternshipStudentInformation.objects.filter(cohort=cohort).select_related(
        'person'
    ).order_by('person__last_name')

    scores = InternshipScore.objects.filter(cohort=cohort).select_related(
        'student__person', 'period', 'cohort'
    ).order_by('student__person__last_name')

    score_mapping = InternshipScoreMapping.objects.filter(cohort=cohort).select_related(
        'period', 'cohort'
    ).values("period", "apd", "score_A", "score_B", "score_C", "score_D")

    score_mapping = [entry for entry in score_mapping]

    apds = ['APD_{}'.format(index) for index in range(1, 16)]

    _map_scores(apds, score_mapping, scores)

    context = {'cohort': cohort, 'periods': periods, 'scores': scores, 'students': students}
    return render(request, "scores.html", context=context)


def _map_scores(apds, score_mapping, scores):
    for score in scores:
        score.global_score = 0
        for apd in apds:
            for mapping in score_mapping:
                if mapping['period'] == score.period.pk and str(mapping['apd']) == apd[4:]:
                    note = vars(score)['APD_{}'.format(mapping['apd'])]
                    if note in ['A', 'B', 'C', 'D']:
                        score.global_score += mapping['score_{}'.format(note)]
        score.global_score /= len(apds)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def upload_scores(request, cohort_id, period_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    period = get_object_or_404(Period, pk=period_id)
    if request.method == 'POST':
        file_name = request.FILES['file_upload']
        if file_name is not None:
            if ".xlsx" not in str(file_name):
                messages.add_message(request, messages.ERROR, _('File extension must be .xlsx'))
            else:
                import_scores.import_xlsx(cohort, file_name, period)

    return HttpResponseRedirect(reverse('internship_scores_encoding', kwargs={'cohort_id': cohort.id}))