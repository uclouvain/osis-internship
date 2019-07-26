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
from collections import Counter

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext as _

from base.views.common import display_error_messages, display_success_messages
from internship.forms.score import ScoresFilterForm
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
MINIMUM_SCORE = 0
MAXIMUM_SCORE = 20


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def scores_encoding(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')
    search_form = ScoresFilterForm(request.GET, cohort=cohort)
    students_list = []
    if search_form.is_valid():
        students_list = search_form.get_students(cohort=cohort)
        periods = search_form.get_period(cohort=cohort)
        score_filter = search_form.get_score_filter()
    students_list = _filter_students_by_internship_score(cohort, students_list, periods, score_filter)
    students = get_object_list(request, students_list)
    mapping = _prepare_score_table(cohort, periods, students.object_list)
    context = {'cohort': cohort, 'periods': periods,
               'students': students, 'search_form': search_form, 'mapping': list(mapping)}
    return render(request, "scores.html", context=context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_edited_score(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    edited_score = float(request.POST.get("value"))
    computed_score = float(request.POST.get("computed"))
    registration_id = request.POST.get("student")
    period_name = request.POST.get("period")
    student = {'registration_id': registration_id}
    period = {'name': period_name}
    period_score = {
        "computed": computed_score,
        "edited": edited_score
    }

    if edited_score >= MINIMUM_SCORE and edited_score <= MAXIMUM_SCORE:
        if _update_score(cohort, edited_score, period_name, registration_id):
            return render(request, "fragment/score_cell.html", context={
                "student": student,
                "period": period,
                "period_score": period_score,
            })
        else:
            return _json_response_error(_("An error occured during score update"))
    else:
        return _json_response_error(_("Score must be between 0 and 20"))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def delete_edited_score(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    registration_id = request.POST.get("student")
    period_name = request.POST.get("period")
    student = {'registration_id': registration_id}
    period = {'name': period_name}
    period_score = float(request.POST.get("computed"))

    if _delete_score(cohort, period_name, registration_id):
        return render(request, "fragment/score_cell.html", context={
            "student": student,
            "period": period,
            "period_score": period_score,
        })
    else:
        return _json_response_error(_("An error occured during score update"))


def _delete_score(cohort, period_name, registration_id):
    return InternshipScore.objects.filter(
        cohort=cohort,
        period__name=period_name,
        student__registration_id=registration_id
    ).update(score=None)


def _update_score(cohort, edited_score, period_name, registration_id):
    return InternshipScore.objects.filter(
        cohort=cohort,
        period__name=period_name,
        student__registration_id=registration_id
    ).update(
        score=edited_score
    )


def _json_response_error(msg):
    response = JsonResponse({"error": msg})
    response.status_code = 500
    return response


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
        period__cohort=cohort,
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
    _link_periods_to_specialties(students, students_affectations)
    _append_registration_ids(students, students_affectations)
    return mapping


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
        if period in student.numeric_scores.keys():
            periods_scores.update(
                {
                    period: {
                        'computed': period_score,
                        'edited': student.numeric_scores[period],
                    }
                }
            )
        else:
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
        student.numeric_scores = {}
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
        _retrieve_scores_entered_manually(period, student, student_scores)


def _retrieve_scores_entered_manually(period, student, student_scores):
    if student_scores[0].score:
        student.numeric_scores.update({period.name: student_scores[0].score})


def _link_periods_to_specialties(students, students_affectations):
    for student in students:
        student.specialties = {}
        _update_student_specialties(student, students_affectations)


def _update_student_specialties(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            _annotate_non_mandatory_internship(affectation)
            acronym = _get_acronym_with_sequence(affectation)
            student.specialties.update({affectation['period__name']: acronym})


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


def _filter_students_by_internship_score(cohort, students, periods, score_filter=None):
    if score_filter is not None:
        persons = InternshipScore.objects.filter(
            cohort=cohort,
            period__in=periods
        ).values_list('student__person', flat=True)
        persons = _keep_persons_with_periods_scores(periods, persons)
        if score_filter:
            return students.filter(person__pk__in=persons)
        else:
            return students.exclude(person__pk__in=persons)
    else:
        return students


def _keep_persons_with_periods_scores(periods, persons):
    count = len(periods)
    counter = Counter(persons)
    for k in list(counter):
        if counter[k] < count:
            del counter[k]
    persons = [key for key, _ in counter.most_common()]
    return persons


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
            import_errors = import_scores.import_xlsx(cohort, file_name, period)
            _process_errors(request, import_errors, period)


def _process_errors(request, import_errors, period):
    if import_errors and 'registration_error' in import_errors.keys():
        _show_import_error_message(request, import_errors['registration_error'], period)
    elif import_errors and 'period_error' in import_errors.keys():
        _show_period_error_message(request, import_errors['period_error'], period)
    else:
        _show_import_success_message(request, period)


def _show_period_error_message(request, period_error, period):
    display_error_messages(
        request,
        "{}: {} ≠ {}".format(
            _('Periods do not match'), period, period_error
        )
    )


def _show_import_error_message(request, errors, period):
    message_content = _('Import aborted for period %(period)s due to error(s) on:') % {'period': period}
    for row_error in errors:
        message_content += "<br/> - {} : {}".format(
            _('row %(row_id)s') % {'row_id': row_error[0].row},
            _("student with registration id '%(reg_id)s' not found") % {'reg_id': escape(row_error[0].value)}
        )
    display_error_messages(request, message_content, extra_tags='safe')


def _show_import_success_message(request, period):
    display_success_messages(
        request, _('Internships ratings successfully imported for period %(period)s') % {'period': period}
    )


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def download_scores(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')
    students = InternshipStudentInformation.objects.filter(cohort=cohort).order_by('person__last_name')
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


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_mapping(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods = Period.objects.filter(cohort=cohort).order_by('date_start')
    anchor = "#mapping"
    if request.POST:
        _save_mapping_diff(cohort, periods, request)
        period = request.POST['activePeriod']
        anchor = "#mapping_{}".format(period)
    return HttpResponseRedirect(reverse('internship_scores_encoding', kwargs={'cohort_id': cohort.id}) + anchor)


@transaction.atomic
def _save_mapping_diff(cohort, periods, request):
    for period in periods:
        for grade in [x[0] for x in InternshipScore.SCORE_CHOICES]:
            apds = request.POST.getlist('mapping{}_{}'.format(grade, period.name))
            _update_or_create_mapping(apds, cohort, grade, period)


def _update_or_create_mapping(apds, cohort, grade, period):
    for index, value in enumerate(apds):
        if value:
            _update_or_create_apd_mapping(cohort, grade, period, (index, value))


def _update_or_create_apd_mapping(cohort, grade, period, enum_item):
    index, value = enum_item
    mapping, created = InternshipScoreMapping.objects.get_or_create(
        period=period,
        apd=index + 1,
        cohort=cohort
    )
    if int(value) != 0 and vars(mapping)['score_{}'.format(grade)] != int(value):
        vars(mapping)['score_{}'.format(grade)] = value
        mapping.save()
