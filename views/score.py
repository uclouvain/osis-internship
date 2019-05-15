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
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from internship.forms.score import StudentsFilterForm
from internship.models.cohort import Cohort
from internship.models.internship import Internship
from internship.models.internship_score import InternshipScore
from internship.models.internship_score_mapping import InternshipScoreMapping
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.period import Period
from internship.utils.exporting import score_encoding_xls
from internship.utils.importing import import_scores
from internship.views.common import get_object_list

CHOSEN_LENGTH = 7


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
    _prepare_score_table(cohort, periods, students.object_list)
    context = {'cohort': cohort, 'periods': periods, 'students': students, 'search_form': search_form}
    return render(request, "scores.html", context=context)


def _prepare_score_table(cohort, periods, students):
    scores = InternshipScore.objects.filter(cohort=cohort).select_related(
        'student__person', 'period', 'cohort'
    ).order_by('student__person__last_name')
    mapping = InternshipScoreMapping.objects.filter(cohort=cohort).select_related(
        'period'
    )
    persons = students.values_list('person', flat=True)
    students_affectations = InternshipStudentAffectationStat.objects.filter(
        student__person_id__in=list(persons),
    ).select_related(
        'student', 'period', 'speciality'
    ).values(
        'student__person', 'student__registration_id', 'period__name', 'organization__reference',
        'speciality__acronym', 'speciality__sequence', 'internship__speciality_id', 'internship__name',
        'internship__length_in_periods'
    ).order_by('period__date_start')
    _match_scores_with_students(cohort, periods, list(scores), students)
    _map_numeric_score(mapping, students)
    _link_periods_to_organizations(students, students_affectations)
    internships = _link_periods_to_specialties(students, students_affectations)
    _append_registration_ids(students, students_affectations)
    return internships


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
        if note in [score[0] for score in InternshipScore.SCORE_CHOICES]:
            effective_apd_count += 1
            period_score = _sum_mapped_note((index, note), mapping, period, period_score)
    return period_score/effective_apd_count if effective_apd_count else 0


def _sum_mapped_note(indexed_note, mapping, period, period_score):
    index, note = indexed_note
    mapped_note = list(filter(_get_mapping_score(period, index + 1), list(mapping)))
    if mapped_note:
        period_score += vars(mapped_note[0])['score_{}'.format(note)]
    return period_score


def _match_scores_with_students(cohort, periods, scores_list, students):
    # append scores for each period to each students
    for student in students:
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


def _link_periods_to_specialties(students, students_affectations):
    internships_set = set()
    for student in students:
        student.specialties = {}
        _update_student_specialties(internships_set, student, students_affectations)
    return internships_set


def _update_student_specialties(internships_set, student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            _annotate_non_mandatory_internship(affectation)
            acronym = _get_acronym_with_sequence(affectation)
            student.specialties.update({affectation['period__name']: acronym})
            internships_set.add(acronym)


def _get_acronym_with_sequence(affectation):
    speciality = affectation['internship__speciality_id']
    length = affectation['internship__length_in_periods']
    sequence = affectation['speciality__sequence']
    acronym = affectation['speciality__acronym']
    if speciality and length and sequence:
        acronym = "{}{}".format(acronym, length)
    return acronym


def _link_periods_to_organizations(students, students_affectations):
    for student in students:
        student.organizations = {}
        update_student_organizations(student, students_affectations)


def update_student_organizations(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            student.organizations.update(
                {
                    affectation['period__name']: "{}{}".format(
                        affectation['speciality__acronym'],
                        affectation['organization__reference']
                    )
                }
            )


def _annotate_non_mandatory_internship(affectation):
    if affectation['internship__speciality_id'] is None and affectation['internship__name']:
        affectation['speciality__acronym'] = affectation['internship__name'][-CHOSEN_LENGTH:].replace(" ", "").upper()


def _append_registration_ids(students, students_affectations):
    for student in students:
        student.registration_id = None
        _append_student_registration_id(student, students_affectations)


def _append_student_registration_id(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            student.registration_id = affectation['student__registration_id']


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


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def download_scores(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')
    students = InternshipStudentInformation.objects.filter(cohort=cohort).order_by('person__last_name')[:4]
    internships = Internship.objects.filter(cohort=cohort).order_by(
        'position'
    )
    internships = _list_internships_acronyms(internships)
    _prepare_score_table(cohort, periods, students)
    workbook = score_encoding_xls.export_xls_with_scores(cohort, periods, students, internships)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = "encodage_notes_{}.xlsx".format(cohort.name.strip().replace(' ', '_'))
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


def _list_internships_acronyms(internships):
    internships_acronyms = []
    for internship in internships:
        if internship.speciality and internship.length_in_periods and internship.speciality.sequence:
            internships_acronyms.append("{}{}".format(internship.speciality.acronym, internship.length_in_periods))
        elif internship.speciality:
            internships_acronyms.append(internship.speciality.acronym)
        else:
            internships_acronyms.append(internship.name[-CHOSEN_LENGTH:].replace(" ", "").upper())
    return internships_acronyms
