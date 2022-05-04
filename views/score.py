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
import datetime
import itertools
import json
import re
from itertools import groupby
from numbers import Real
from operator import itemgetter

from dateutil.utils import today
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext as _

from base.models.student import Student
from base.utils.cache import cache_filter
from base.views.common import display_error_messages, display_success_messages
from internship.business.scores import InternshipScoreRules
from internship.forms.score import ScoresFilterForm
from internship.models.cohort import Cohort
from internship.models.internship_score import InternshipScore, APD_NUMBER, MIN_APDS, MAX_APDS
from internship.models.internship_score_mapping import InternshipScoreMapping
from internship.models.internship_score_reason import InternshipScoreReason
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.master_allocation import MasterAllocation
from internship.models.period import get_effective_periods, get_assignable_periods
from internship.templatetags.dictionary import is_edited, is_excused
from internship.templatetags.student import has_remedial
from internship.utils.exporting import score_encoding_xls
from internship.utils.importing import import_scores, import_eval
from internship.utils.mails import mails_management
from internship.views.common import get_object_list, round_half_up
from osis_common.decorators.download import set_download_cookie

CHOSEN_LENGTH = 7
MINIMUM_SCORE = 0
MAXIMUM_SCORE = 20

UPDATE_SCORE_ERROR_MSG = _("An error occured during score update")


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
@cache_filter()
def scores_encoding(request, cohort_id):
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(
            'internshipstudentinformation_set',
            'period_set',
            'internshipspeciality_set',
            'organization_set'
        ),
        pk=cohort_id
    )
    all_periods = get_effective_periods(cohort_id)
    assignable_periods = get_assignable_periods(cohort_id)
    periods = all_periods.order_by('date_end')
    completed_periods = periods.filter(date_end__lt=today())
    search_form = ScoresFilterForm(request.GET, cohort=cohort)
    students_list = []

    affectations_count = InternshipStudentAffectationStat.objects.filter(internship__cohort=cohort).count()

    if search_form.is_valid():
        students_list = search_form.get_students(cohort=cohort)
        periods = search_form.get_periods(cohort=cohort)
        grades_filter = search_form.get_all_grades_submitted_filter()
        evals_filter = search_form.get_evaluations_submitted_filter()
        apds_filter = search_form.get_all_apds_validated_filter()
        students_list = _filter_students_with_specialty_organization(cohort, students_list, search_form)
        students_list = _filter_students_with_all_grades_submitted(cohort, students_list, periods, grades_filter)
        students_list = _filter_students_with_evaluations_submitted(students_list, periods, evals_filter)
        students_list = _filter_students_with_all_apds_validated(cohort, students_list, periods, apds_filter)

    students = get_object_list(request, students_list)

    mapping = _prepare_score_table(cohort, periods, students.object_list)
    grades = [grade for grade, _ in InternshipScore.SCORE_CHOICES]
    context = {
        'cohort': cohort, 'periods': periods, 'mandatory_periods': assignable_periods, 'all_periods': all_periods,
        'students': students, 'grades': grades, 'affectations_count': affectations_count, 'search_form': search_form,
        'mapping': list(mapping), 'completed_periods': completed_periods, 'apd_range': range(1, APD_NUMBER + 1),
        'score_edit_reasons': InternshipScoreReason.objects.all()
    }
    return render(request, "scores.html", context=context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def score_detail_form(request, cohort_id, student_registration_id, period_id):
    cohort = Cohort.objects.get(pk=cohort_id)
    student = Student.objects.get(registration_id=student_registration_id)
    student_affectation, created = InternshipStudentAffectationStat.objects.get_or_create(
        student__registration_id=student_registration_id,
        period_id=period_id,
        defaults={'cost': 0, 'student': student}
    )
    score, created = InternshipScore.objects.select_related(
        'student_affectation__student',
        'student_affectation__period',
        'student_affectation__speciality',
        'student_affectation__organization'
    ).get_or_create(
        student_affectation=student_affectation
    )
    master = _get_main_internship_master(score)
    apds = range(1, APD_NUMBER + 1)

    if request.POST:
        apds_data = {'APD_{}'.format(apd): request.POST.get('apd-{}'.format(apd)) for apd in apds}
        reason = request.POST.get('reason') if request.POST.get('reason') else None
        if _validate_score(request, apds_data):
            update = InternshipScore.objects.filter(pk=score.pk).update(
                **apds_data,
                reason=reason,
                validated=True,
                validated_by=request.user.person
            )
            if update:
                messages.add_message(request, messages.SUCCESS, _('Score updated successfully for {}'.format(
                    score.student_affectation
                )))
                return redirect(reverse('internship_scores_encoding', kwargs={'cohort_id': cohort_id}))
            else:
                messages.add_message(request, messages.ERROR, UPDATE_SCORE_ERROR_MSG)
        else:
            _cache_apd_form_values(apds_data, score)

    context = {
        'cohort': cohort,
        'score': score,
        'master': master,
        'apds': apds,
        'available_grades': [grade for grade, _ in InternshipScore.SCORE_CHOICES],
    }

    return render(request, "score_form.html", context=context)


def _get_main_internship_master(score):
    main_master_allocation = MasterAllocation.objects.filter(
        specialty=score.student_affectation.speciality,
        organization=score.student_affectation.organization
    ).first()
    return main_master_allocation.master if main_master_allocation else None


def _cache_apd_form_values(apds_data, score):
    for apd, value in apds_data.items():
        vars(score)[apd] = value


def _validate_score(request, apds_data):
    filled_apds_data = dict(filter(lambda apd: apd[1], apds_data.items()))
    if not MIN_APDS <= len(filled_apds_data) <= MAX_APDS:
        messages.add_message(
            request,
            messages.ERROR,
            _("An evaluation should include minimum {} and maximum {} evaluated APDs").format(MIN_APDS, MAX_APDS)
        )
        return False
    return True


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def send_recap(request, cohort_id, period_id=None):
    selected_persons = InternshipStudentInformation.objects.filter(
        pk__in=request.POST.getlist('selected_student'),
    ).select_related('person').values_list('person', flat=True)
    periods = get_effective_periods(cohort_id)
    if period_id:
        periods = periods.filter(pk=period_id)
    affectations = InternshipStudentAffectationStat.objects.filter(
        period__in=periods, student__person__in=selected_persons
    ).order_by('period__date_start')
    affectations_person_period = affectations.values_list('student__person', 'period')
    scores = InternshipScore.objects.filter(
        student_affectation__in=affectations,
        validated=True
    ).values_list('student_affectation__student__person', 'student_affectation__period')

    persons_dict = {person: {p.name: _("No internship") for p in periods} for person in selected_persons}
    for person in selected_persons:
        send_mail_recap_per_student(person, persons_dict,
                                    affectations=affectations_person_period,
                                    cohort_id=cohort_id,
                                    periods=periods,
                                    connected_user=request.user,
                                    scores=scores)
    _show_reminder_sent_success_message(request)
    return redirect('{}?{}'.format(
        reverse('internship_scores_encoding', kwargs={
            'cohort_id': cohort_id,
        }), generate_query_string(request))
    )


def send_mail_recap_per_student(person, persons_dict, **kwargs):
    affectations = kwargs.get('affectations')
    cohort_id = kwargs.get('cohort_id')
    periods = kwargs.get('periods')
    connected_user = kwargs.get('connected_user')
    scores = kwargs.get('scores')

    today = datetime.date.today()
    for period in periods:
        pp = (person, period.id)
        if pp in affectations:
            spec = period.internshipstudentaffectationstat_set.select_related(
                'period', 'student__person'
            ).get(student__person=person).speciality.name
            if today > period.date_end:
                persons_dict[person][period.name] = (spec + " - " + _("Grades received")) if pp in scores \
                    else (spec + " - " + _("Grades not received"))
            else:
                persons_dict[person][period.name] = (spec + " - " + _("Internship not done yet"))
    mails_management.send_score_encoding_recap(data={
        'today': today,
        'person_id': person,
        'periods': persons_dict[person],
        'ordered_periods': periods,
        'cohort_id': cohort_id
    }, connected_user=connected_user)


def generate_query_string(request):
    prev_url = request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else ''
    query_string = prev_url.split('?')[1] if prev_url and '?' in prev_url else ''
    return query_string


def _retrieve_blank_periods_by_student(persons, periods, scores, reverse=False):
    # get students with blank periods, students without blank periods if reverse set to true
    students = {person: [] for person in persons}
    students_without_grades = {}
    students_with_grades = {}
    for student, period in scores:
        students[student].append(period)
    for student in students.keys():
        blank_periods = [period for period in periods if period not in students[student]]
        if blank_periods:
            students_without_grades[student] = blank_periods
        else:
            students_with_grades[student] = blank_periods
    return students_with_grades if reverse else students_without_grades


def _show_reminder_sent_error_message(request):
    display_success_messages(
        request, _('An error occured while sending reminders')
    )


def _show_reminder_sent_success_message(request):
    display_success_messages(
        request, _('Summaries have been sent successfully')
    )


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_evaluation_status(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    registration_id = request.POST.get("student")
    period_name = request.POST.get("period")
    status = json.loads(request.POST.get("status"))
    evaluations = {"registration_id": registration_id, "period": period_name}
    update, error_info = _update_evaluation_status(status, [evaluations], cohort)
    return _json_response_success() if update else _json_response_error(_('An error occured while updating status'))


def _update_evaluation_status(status, evaluations, cohort):
    sorted_evaluations = sorted(evaluations, key=itemgetter('period'))
    evaluations_by_period = {
        key: [item['registration_id'] for item in group]
        for key, group in itertools.groupby(sorted_evaluations, lambda eval: eval['period'])
    }
    for period_name, registration_ids in evaluations_by_period.items():
        update = InternshipStudentAffectationStat.objects.filter(
            period__cohort=cohort,
            period__name=period_name,
            student__registration_id__in=registration_ids
        ).update(
            internship_evaluated=status
        )
        if not update:
            return False, {'period': period_name}
    return True, {'periods': evaluations_by_period.keys()}


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def refresh_evolution_score(request, cohort_id):
    n_completed_periods = get_effective_periods(cohort_id).filter(date_end__lt=today()).count()
    if 'scores' in request.POST:
        scores = _load_json_scores(request)
        if 'period' in request.POST:
            value = request.POST.get('edited', request.POST.get('computed'))
            period = request.POST['period']
            scores[period] = int(value) if value else None
        evolution_score = _get_scores_mean(scores, n_completed_periods)
        response = JsonResponse({
            'updated_scores': str(scores),
            'evolution_score': evolution_score,
            'computed_title_text': _("Score edited. Computed score: "),
        })
        response.status_code = 200
        return response
    else:
        return HttpResponse(status=204)


def _load_json_scores(request):
    return json.loads(re.sub(r"(?<!\w)'(?<!\w)|(?!\w)'(?!\w)", '\"', request.POST['scores']).replace('None', 'null'))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_evolution_score(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    edited_score = int(request.POST.get("edited"))
    computed_score = int(request.POST.get("computed"))
    registration_id = request.POST.get("student")
    reason = request.POST.get("reason")
    scores = _load_json_scores(request)
    student = {
        'registration_id': registration_id,
        'evolution_score': {
            "computed": computed_score,
            "edited": {'score': edited_score, 'reason': reason}
        },
        'periods_scores': scores
    }

    if edited_score >= MINIMUM_SCORE and edited_score <= MAXIMUM_SCORE:
        if _update_evolution_score(cohort, edited_score, registration_id, reason):
            return render(request, "fragment/evolution_score_cell.html", context={
                "student": student,
            })
        else:
            return _json_response_error(UPDATE_SCORE_ERROR_MSG)
    else:
        return _json_response_error(
            _("Score must be between %(minimum)d and %(maximum)d") % {
                'minimum': MINIMUM_SCORE, 'maximum': MAXIMUM_SCORE
            }
        )


def _update_evolution_score(cohort, edited_score, registration_id, reason):
    person = Student.objects.select_related('person').get(
        registration_id=registration_id,
    ).person
    return cohort.internshipstudentinformation_set.filter(
        person=person
    ).update(
        evolution_score=edited_score,
        evolution_score_reason=reason
    )


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def delete_evolution_score(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    registration_id = request.POST.get("student")
    computed_score = int(request.POST.get("computed"))
    scores = _load_json_scores(request)
    student = {
        'registration_id': registration_id,
        'evolution_score': computed_score,
        'periods_scores': scores
    }
    person = Student.objects.select_related('person').get(
        registration_id=registration_id,
    ).person
    if cohort.internshipstudentinformation_set.filter(
            person=person
    ).update(evolution_score=None):
        return render(request, "fragment/evolution_score_cell.html", context={
            "student": student,
        })
    else:
        return _json_response_error(_("An error occured during score deletion"))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_edited_score(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    edited_score = int(request.POST.get("edited") or 0)
    computed_score = int(request.POST.get("computed") or 0)
    registration_id = request.POST.get("student")
    period_name = request.POST.get("period")
    reason = request.POST.get("reason")
    student = {'registration_id': registration_id}
    period = {'name': period_name}
    period_score = {
        "computed": computed_score,
        "edited": {'score': edited_score, 'reason': reason}
    }

    if edited_score >= MINIMUM_SCORE and edited_score <= MAXIMUM_SCORE:
        if _update_score(cohort, edited_score, period_name, registration_id, reason):
            return render(request, "fragment/score_cell.html", context={
                "student": student,
                "period": period,
                "period_score": period_score,
            })
        else:
            return _json_response_error(UPDATE_SCORE_ERROR_MSG)
    else:
        return _json_response_error(
            _("Score must be between %(minimum)d and %(maximum)d") % {
                'minimum': MINIMUM_SCORE, 'maximum': MAXIMUM_SCORE
            }
        )


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def delete_edited_score(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    registration_id = request.POST.get("student")
    period_name = request.POST.get("period")
    student = {'registration_id': registration_id}
    period = {'name': period_name}
    period_score = int(request.POST.get("computed"))
    if _delete_score(cohort, period_name, registration_id):
        return render(request, "fragment/score_cell.html", context={
            "student": student,
            "period": period,
            "period_score": period_score,
        })
    else:
        return _json_response_error(_("An error occured during score deletion"))


def _delete_score(cohort, period_name, registration_id):
    return InternshipScore.objects.filter(
        student_affectation__period__name=period_name,
        student_affectation__student__registration_id=registration_id
    ).update(score=None, excused=False)


def _update_score(cohort, edited_score, period_name, registration_id, reason):
    period = cohort.period_set.get(name=period_name)
    student = Student.objects.get(registration_id=registration_id)
    student_affectation, created = InternshipStudentAffectationStat.objects.get_or_create(
        student=student, period=period, defaults={'cost': 0}
    )
    return InternshipScore.objects.update_or_create(student_affectation=student_affectation, defaults={
        'score': edited_score, 'reason': reason, 'student_affectation': student_affectation, 'validated': True
    })


def _json_response_success():
    response = JsonResponse({})
    response.status_code = 204
    return response


def _json_response_error(msg):
    response = JsonResponse({"error": msg})
    response.status_code = 500
    return response


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def empty_score(request, cohort_id):
    cohort = get_object_or_404(Cohort.objects.prefetch_related('period_set'), pk=cohort_id)
    student = Student.objects.get(registration_id=request.POST.get('registration_id'))
    period = cohort.period_set.get(name=request.POST.get("period_name"))
    affectation, created = InternshipStudentAffectationStat.objects.get_or_create(
        period=period, student=student, defaults={'cohort': cohort, 'student': student, 'period': period, 'cost': 0}
    )
    score, created = InternshipScore.objects.update_or_create(
        student_affectation=affectation,
        defaults={'excused': True}
    )
    if score:
        return render(request, "fragment/score_cell.html", context={
            "student": {'registration_id': student.registration_id},
            "period": {'name': period.name},
            "period_score": {"computed": 0, "edited": {'excused': None, 'reason': score.reason}}
        })


def _prepare_score_table(cohort, periods, students):
    persons = [student.person.pk for student in students]

    scores = InternshipScore.objects.filter(
        student_affectation__student__person_id__in=persons, validated=True,
    ).select_related(
        'student_affectation__student__person', 'student_affectation__period__cohort'
    ).order_by('student_affectation__student__person')
    mapping = cohort.internshipscoremapping_set.all().select_related('period')
    students_affectations = InternshipStudentAffectationStat.objects.filter(
        student__person_id__in=list(persons),
        period__cohort=cohort,
    ).select_related(
        'student', 'period', 'speciality'
    ).values(
        'student__person', 'student__registration_id', 'period__name', 'organization__reference', 'organization__name',
        'speciality__acronym', 'speciality__sequence', 'speciality__name', 'internship__speciality_id',
        'internship__name', 'internship__length_in_periods', 'internship_evaluated'
    ).order_by('period__date_start')

    scores = _group_by_students_and_periods(scores)

    _prepare_students_extra_data(students)
    _match_scores_with_students(cohort, periods, scores, students)
    _set_condition_fulfilled_status(students)
    _map_numeric_score(mapping, students)
    _link_periods_to_organizations(students, students_affectations)
    _link_periods_to_specialties(students, students_affectations)
    _link_periods_to_evaluations(students, students_affectations)
    _append_registration_ids(students, students_affectations)
    _append_remedials_count(students, students_affectations)
    _compute_evolution_score(students, cohort.id)
    return mapping


def _group_by_students_and_periods(scores):
    return {
        person_id: {
            period_id: list(score)
            for period_id, score in groupby(value, lambda score: score.period.pk)
        }
        for person_id, value in groupby(scores, lambda score: score.student.person.pk)
    }


def _prepare_students_extra_data(students):
    for student in students:
        student.scores = []
        student.numeric_scores = {}
        student.specialties = {}
        student.organizations = {}
        student.evaluations = {}
        student.comments = {}
        student.remedial_periods_count = 0


def _compute_evolution_score(students, cohort_id):
    n_completed_periods = get_effective_periods(cohort_id).filter(date_end__lt=today()).count()
    for student in students:
        if student.evolution_score is None:
            student.evolution_score = _get_scores_mean(student.periods_scores, n_completed_periods)
        else:
            student.evolution_score = {
                'edited': {'score': student.evolution_score, 'reason': student.evolution_score_reason},
                'computed': _get_scores_mean(student.periods_scores, n_completed_periods)
            }


def _get_scores_mean(scores, n_periods):
    evolution_score = 0
    effective_n_periods = n_periods - _count_emptied_scores(scores)
    for key in scores.keys():
        period_score = _get_period_score(scores[key])
        evolution_score += period_score / effective_n_periods if period_score and isinstance(period_score, Real) else 0
    return round_half_up(evolution_score)


def _get_period_score(score):
    if is_edited(score):
        if not is_excused(score['edited']):
            return score['edited']['score']
        else:
            return None
    else:
        return score


def _count_emptied_scores(scores):
    return len([key for key in scores.keys() if _get_period_score(scores[key]) is None])


def _link_periods_to_evaluations(students, students_affectations):
    for student in students:
        _update_student_evaluations(student, students_affectations)


def _update_student_evaluations(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            student.evaluations.update(
                {
                    affectation['period__name']: affectation['internship_evaluated']
                }
            )


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
    effective_count = 0
    for index, note in enumerate(scores):
        if note in [score[0] for score in InternshipScore.SCORE_CHOICES]:
            effective_count += 1
            period_score = _sum_mapped_note((index, note), mapping, period, period_score)
    return round_half_up(period_score / effective_count) if effective_count else 0


def _sum_mapped_note(indexed_note, mapping, period, period_score):
    index, note = indexed_note
    mapped_note = list(filter(_get_mapping_score(period, index + 1), list(mapping)))
    if mapped_note:
        period_score += vars(mapped_note[0])['score_{}'.format(note)]
    return period_score


def _match_scores_with_students(cohort, periods, scores, students):
    # append scores for each period to each student
    for student in students:
        for period in periods:
            if student.person.pk in scores.keys() and period.pk in scores[student.person.pk].keys():
                student_scores = scores[student.person.pk][period.pk]
                _append_period_scores_and_comments_to_student(period, student, list(student_scores))


def _set_condition_fulfilled_status(students):
    for student in students:
        student.fulfill_condition = InternshipScoreRules.student_has_fulfilled_requirements(student)


def _get_mapping_score(period, apd):
    return lambda x: x.period.name == period and x.apd == apd


def _append_period_scores_and_comments_to_student(period, student, student_scores):
    if student_scores:
        scores = student_scores[0].get_scores()
        comments = student_scores[0].comments
        student.scores += (period.name, scores),
        student.comments.update({period.name: _replace_comments_keys_with_translations(comments)})
        _retrieve_scores_entered_manually(period, student, student_scores)


def _retrieve_scores_entered_manually(period, student, student_scores):
    student_score = student_scores[0]
    score = student_score.score
    if score or student_score.excused:
        student.numeric_scores.update(
            {
                period.name: {'excused': score, 'reason': student_score.reason}
                if student_score.excused else {'score': score, 'reason': student_score.reason}}
        )


def _link_periods_to_specialties(students, students_affectations):
    for student in students:
        _update_student_specialties(student, students_affectations)


def _update_student_specialties(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            _annotate_non_mandatory_internship(affectation)
            acronym = _get_acronym_with_sequence(affectation)
            specialty_name = affectation['speciality__name']
            student.specialties.update({
                affectation['period__name']: {
                    'acronym': acronym,
                    'name': specialty_name
                }
            })


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
        update_student_organizations(student, students_affectations)


def update_student_organizations(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            student.organizations.update(
                {
                    affectation['period__name']: {
                        "reference": "{}{}".format(
                            affectation['speciality__acronym'],
                            affectation['organization__reference']
                        ),
                        "name": affectation['organization__name']
                    }
                }
            )


def _annotate_non_mandatory_internship(affectation):
    if affectation['internship__speciality_id'] is None and affectation['internship__name']:
        affectation['speciality__acronym'] = affectation['internship__name'][-CHOSEN_LENGTH:].replace(" ", "").upper()


def _append_registration_ids(students, students_affectations):
    for student in students:
        student.registration_id = None
        _append_student_registration_id(student, students_affectations)


def _append_remedials_count(students, students_affectations):
    for student in students:
        if has_remedial(student):
            student.remedial_periods_count = students_affectations.filter(
                period__remedial=True,
                student__person=student.person
            ).count()


def _append_student_registration_id(student, students_affectations):
    for affectation in students_affectations:
        if affectation['student__person'] == student.person.pk:
            student.registration_id = affectation['student__registration_id']


def _filter_students_with_all_grades_submitted(cohort, students, periods, filter):
    if filter is not None:
        persons = students.values_list('person', flat=True)
        completed_periods = periods.filter(date_end__lt=today()).values_list('id', flat=True)
        students_with_affectations = InternshipStudentAffectationStat.objects.filter(
            student__person__in=persons, period__in=completed_periods,
        ).values_list('student', flat=True)
        scores = InternshipScore.objects.filter(
            student_affectation__student__in=students_with_affectations,
            student_affectation__period__pk__in=completed_periods,
            validated=True,
        ).select_related(
            'student_affectation__student', 'student_affectation__period'
        ).values_list(
            'student_affectation__student__person',
            'student_affectation__period'
        )
        persons_with_affectations = students_with_affectations.values_list('student__person', flat=True)
        periods_persons = _retrieve_blank_periods_by_student(
            persons_with_affectations,
            completed_periods,
            scores,
            filter
        )
        students = students.filter(person__pk__in=periods_persons.keys())
    return students


def _filter_students_with_evaluations_submitted(students, periods, filter):
    if filter is not None:
        persons = students.values_list('person', flat=True)
        completed_periods = periods.filter(date_end__lt=today()).values_list('id', flat=True)
        students_with_affectations = InternshipStudentAffectationStat.objects.filter(
            student__person__in=persons, period__in=completed_periods, internship_evaluated=filter
        ).values_list('student', flat=True)
        persons_with_affectations = students_with_affectations.values_list('student__person', flat=True)
        students = students.filter(person__pk__in=persons_with_affectations)
    return students


def _filter_students_with_all_apds_validated(cohort, students, periods, filter):
    if filter is not None:
        persons = students.values_list('person', flat=True)
        scores = InternshipScore.objects.filter(
            student_affectation__period__cohort=cohort,
            student_affectation__student__person_id__in=list(persons)).select_related(
            'student_affectation__student__person', 'student_affectation__period__cohort'
        ).order_by('student_affectation__student__person')
        scores = _group_by_students_and_periods(scores)
        _prepare_students_extra_data(students)
        _match_scores_with_students(cohort, periods, scores, students)
        _set_condition_fulfilled_status(students)
        students = [s for s in students if s.fulfill_condition == filter]
    return students


def _filter_students_with_specialty_organization(cohort, students, search_form):
    organization = search_form.get_organizations(cohort)
    specialty = search_form.get_specialties(cohort)
    periods = search_form.get_periods(cohort)

    if organization or specialty or periods:
        persons = students.values_list('person', flat=True)
        persons_with_affectations = InternshipStudentAffectationStat.objects.filter(
            organization__in=organization,
            speciality__in=specialty,
            period__in=periods,
            student__person__in=persons
        ).values_list('student__person', flat=True)
        students = students.filter(person__pk__in=persons_with_affectations)
    return students


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def upload_scores(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    _upload_scores_file(request, cohort)
    return HttpResponseRedirect(reverse('internship_scores_encoding', kwargs={'cohort_id': cohort.id}))


def _upload_scores_file(request, cohort):
    if request.method == 'POST':
        file_name = request.FILES['file_upload']
        period = request.POST['period']
        if file_name and ".xlsx" not in str(file_name):
            messages.add_message(request, messages.ERROR, _('File extension must be .xlsx'))
        else:
            import_errors = import_scores.import_xlsx(cohort, file_name, period)
            _process_errors(request, import_errors, period)


def _upload_eval_file(request, cohort):
    if request.method == 'POST':
        file_name = request.FILES['file_upload']
        if file_name and ".xlsx" not in str(file_name):
            display_error_messages(request, _('File extension must be .xlsx'))
        else:
            evaluations = import_eval.import_xlsx(file_name)
            _process_evaluations(request, cohort, evaluations)


def _process_evaluations(request, cohort, evaluations):
    registration_ids = [eval['registration_id'] for eval in evaluations]
    valid_reg_ids, non_valid_reg_ids = _check_registration_ids_validity(cohort, registration_ids)
    if non_valid_reg_ids:
        display_error_messages(
            request,
            _('Evaluation status importation aborted. '
              'Following registration ids do not exist in cohort: %(registration_ids)s')
            % {'registration_ids': ', '.join(non_valid_reg_ids)}
        )
    else:
        filtered_evaluations = [eval for eval in evaluations if eval['registration_id'] in valid_reg_ids]
        status_updated, info = _update_evaluation_status(
            status=True, evaluations=filtered_evaluations, cohort=cohort
        )
        if status_updated:
            display_success_messages(request, _('Evaluation status successfully updated for %(periods)s' % {
                'periods': ', '.join(info['periods'])
            }))
        else:
            period = info['period']
            display_error_messages(request, _('An error occured during evaluation status update in {}').format(period))


def _check_registration_ids_validity(cohort, registration_ids):
    student_registration_id_query = Student.objects.filter(person=OuterRef('person')).values('registration_id')[:1]
    filtered_students = cohort.internshipstudentinformation_set.all().annotate(
        registration_id=Subquery(student_registration_id_query)
    ).values_list('registration_id', flat=True)
    non_valid_registration_ids = set(registration_ids).difference(set(filtered_students))
    valid_registration_ids = set(registration_ids).difference(non_valid_registration_ids)
    non_valid_registration_ids.difference_update({'', None})
    return valid_registration_ids, non_valid_registration_ids


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
@set_download_cookie
def download_scores(request, cohort_id):
    cohort = get_object_or_404(
        Cohort.objects.prefetch_related(
            'internshipstudentinformation_set',
            'internship_set',
            'period_set'
        ),
        pk=cohort_id
    )
    selected_periods = request.POST.getlist('period')
    periods = cohort.period_set.filter(name__in=selected_periods).order_by('date_start')
    students = cohort.internshipstudentinformation_set.all().select_related(
        'person'
    ).order_by('person__last_name')
    internships = cohort.internship_set.all().order_by('position')
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
def upload_eval(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    _upload_eval_file(request, cohort)
    return HttpResponseRedirect(reverse('internship_scores_encoding', kwargs={'cohort_id': cohort.id}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_mapping(request, cohort_id):
    cohort = get_object_or_404(Cohort.objects.prefetch_related('period_set'), pk=cohort_id)
    periods = cohort.period_set.all().order_by('date_start')
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


def _replace_comments_keys_with_translations(comments):
    comments_keys_mapping = {
        'impr_areas': _('Improvement areas'),
        'suggestions': _('Suggestions'),
        'good_perf_ex': _('Good performance example'),
        'intermediary_evaluation': _('Intermediary evaluation')
    }
    return {comments_keys_mapping[k]: v for k, v in comments.items()}
