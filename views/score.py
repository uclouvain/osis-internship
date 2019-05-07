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
from django.core.paginator import Paginator, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from internship.models.cohort import Cohort
from internship.models.internship_score import InternshipScore
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.period import Period
from internship.utils.importing import import_scores


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def scores_encoding(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')

    students_list = InternshipStudentInformation.objects.filter(cohort=cohort).select_related(
        'person'
    ).order_by('person__last_name')

    scores = InternshipScore.objects.filter(cohort=cohort).select_related(
        'student__person', 'period', 'cohort'
    ).order_by('student__person__last_name')

    paginator = Paginator(students_list, 10)
    page = request.GET.get('page')
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except students:
        students = paginator.page(paginator.num_pages)

    apds = ['APD_{}'.format(index) for index in range(1, 16)]

    for student in students.object_list:
        student.scores = []
        for period in periods:
            student_scores = scores.filter(
                student__person_id=student.person_id,
                cohort=cohort,
                period=period
            ).order_by('period__name').values_list(*apds)
            if list(student_scores):
                student.scores += (period.name, list(student_scores)[0]),

    context = {'cohort': cohort, 'periods': periods, 'scores': scores, 'students': students}
    return render(request, "scores.html", context=context)


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
        if file_name is not None and ".xlsx" not in str(file_name):
            messages.add_message(request, messages.ERROR, _('File extension must be .xlsx'))
        else:
            import_scores.import_xlsx(cohort, file_name, period)
