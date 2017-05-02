##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
import json
import logging
import copy
import traceback
from decimal import Decimal, Context, Inexact

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as  PsycopInterfaceError

from assessments.business import score_encoding_progress
from assessments.views import export_utils
from attribution import models as mdl_attr
from base import models as mdl
from base.enums import exam_enrollment_justification_type
from base.enums.exam_enrollment_justification_type import JUSTIFICATION_TYPES
from base.utils import send_mail
from base.views import layout
from osis_common.document import paper_sheet
from osis_common.models.queue_exception import QueueException


logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def _is_inside_scores_encodings_period(user):
    return mdl.session_exam_calendar.current_session_exam()


def _is_not_inside_scores_encodings_period(user):
    return not _is_inside_scores_encodings_period(user)


@login_required
@permission_required('base.can_access_evaluation', raise_exception=True)
def assessments(request):
    return layout.render(request, "assessments.html", {'section': 'assessments'})


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_not_inside_scores_encodings_period, login_url=reverse_lazy('scores_encoding'))
def outside_period(request):
    latest_session_exam = mdl.session_exam_calendar.get_latest_session_exam()
    closest_new_session_exam = mdl.session_exam_calendar.get_closest_new_session_exam()

    if latest_session_exam:
        session_number = latest_session_exam.number_session
        str_date = latest_session_exam.academic_calendar.end_date.strftime(_('date_format'))
        messages.add_message(request, messages.WARNING, _('outside_scores_encodings_period_latest_session') % (session_number,str_date))

    if closest_new_session_exam:
        session_number = closest_new_session_exam.number_session
        str_date = closest_new_session_exam.academic_calendar.start_date.strftime(_('date_format'))
        messages.add_message(request, messages.WARNING, _('outside_scores_encodings_period_closest_session') % (session_number,str_date))

    if not messages.get_messages(request):
        messages.add_message(request, messages.WARNING, _('score_encoding_period_not_open'))
    return layout.render(request, "outside_scores_encodings_period.html", {})


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def scores_encoding(request):
    template_name = "scores_encoding.html"
    academic_yr = mdl.academic_year.current_academic_year()
    number_session = mdl.session_exam_calendar.find_session_exam_number()
    score_encoding_progress_list = None
    context = {'academic_year': academic_yr,
               'number_session': number_session,
               'active_tab': request.GET.get('active_tab')}

    offer_year_id = request.GET.get('offer', None)
    if offer_year_id:
        offer_year_id = int(offer_year_id)

    if mdl.program_manager.is_program_manager(request.user):
        template_name = "scores_encoding_by_learning_unit.html"
        NOBODY = -1

        tutor_id = request.GET.get('tutor')
        if tutor_id:
            tutor_id = int(tutor_id)
        learning_unit_year_acronym = request.GET.get('learning_unit_year_acronym')
        incomplete_encodings_only = request.GET.get('incomplete_encodings_only', False)

        # Manage filter
        learning_unit_year_ids = None
        if learning_unit_year_acronym:
            learning_unit_year_ids = mdl.learning_unit_year.search(acronym=learning_unit_year_acronym) \
                .values_list('id', flat=True)
        if tutor_id and tutor_id != NOBODY:
            learning_unit_year_ids_filter_by_tutor = mdl_attr.attribution.search(tutor=tutor_id) \
                .distinct('learning_unit_year') \
                .values_list('learning_unit_year_id', flat=True)
            learning_unit_year_ids = learning_unit_year_ids_filter_by_tutor if not learning_unit_year_ids else \
                set(learning_unit_year_ids) & set(learning_unit_year_ids_filter_by_tutor)

        score_encoding_progress_list = score_encoding_progress.get_scores_encoding_progress(
            user=request.user,
            offer_year_id=offer_year_id,
            number_session=number_session,
            academic_year=academic_yr,
            learning_unit_year_ids=learning_unit_year_ids
        )

        score_encoding_progress_list = score_encoding_progress.\
            append_related_tutors_and_score_responsibles(score_encoding_progress_list)

        if incomplete_encodings_only:
            score_encoding_progress_list = score_encoding_progress.filter_only_incomplete(score_encoding_progress_list)

        if tutor_id == NOBODY:
            score_encoding_progress_list = score_encoding_progress.\
                filter_only_without_attribution(score_encoding_progress_list)

        all_tutors = score_encoding_progress.find_related_tutors(score_encoding_progress_list)

        all_offers = mdl.offer_year.find_by_user(request.user, academic_yr=academic_yr)

        if not score_encoding_progress_list:
            messages.add_message(request, messages.WARNING, "%s" % _('no_result'))

        context.update({'offer_list': all_offers,
                        'tutor_list': all_tutors,
                        'offer_year_id': offer_year_id,
                        'tutor_id': tutor_id,
                        'learning_unit_year_acronym': learning_unit_year_acronym,
                        'incomplete_encodings_only': incomplete_encodings_only,
                        'last_synchronization': mdl.synchronization.find_last_synchronization_date()})

    elif mdl.tutor.is_tutor(request.user):
        tutor = mdl.tutor.find_by_user(request.user)
        score_encoding_progress_list = score_encoding_progress.get_scores_encoding_progress(user=request.user,
                                                                                            offer_year_id=offer_year_id,
                                                                                            number_session=number_session,
                                                                                            academic_year=academic_yr)
        all_offers = score_encoding_progress.find_related_offer_years(score_encoding_progress_list)

        context.update({'tutor': tutor,
                        'offer_year_list': all_offers,
                        'offer_year_id': offer_year_id})

    context.update({
        'notes_list': score_encoding_progress.group_by_learning_unit_year(score_encoding_progress_list)
                      if not offer_year_id else score_encoding_progress_list
    })

    return layout.render(request, template_name, context)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def online_encoding(request, learning_unit_year_id=None):
    data_dict = get_data_online(request, learning_unit_year_id)
    return layout.render(request, "online_encoding.html", data_dict)


def __send_messages_for_each_offer_year(all_enrollments, learning_unit_year, updated_enrollments):
    """
    Send a message for each offer year to all the tutors of a learning unit inside a program
    managed by the program manager if all the scores
    of this learning unit, inside this program, are encoded and at most one score is newly encoded.
    Th encoder is a program manager, so all the encoded scores are final.
    :param enrollments: The enrollments to the learning unit year , inside the managed program.
    :param learning_unit_year: The learning unit year of the enrollments.
    :param updated_enrollments: list of exam enrollments objects which has been updated
    :return: A list of error message if message cannot be sent
    """
    sent_error_messages = []
    offer_years = get_offer_years_from_enrollments(updated_enrollments)
    for offer_year in offer_years:
        sent_error_message = __send_message_for_offer_year(all_enrollments, learning_unit_year,
                                                           offer_year)
        if sent_error_message:
            sent_error_messages.append(sent_error_message)
    return sent_error_messages


def get_offer_years_from_enrollments(enrollments):
    list_offer_years = [enrollment.learning_unit_enrollment.offer_enrollment.offer_year for enrollment in enrollments]
    return list(set(list_offer_years))


def __send_message_for_offer_year(all_enrollments, learning_unit_year, offer_year):
    enrollments = filter_enrollments_by_offer_year(all_enrollments, offer_year)
    progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(enrollments)
    offer_acronym = offer_year.acronym
    sent_error_message = None
    if progress == 100:
        persons = list(set([tutor.person for tutor in mdl.tutor.find_by_learning_unit(learning_unit_year)]))
        sent_error_message = send_mail.send_message_after_all_encoded_by_manager(persons, enrollments,
                                                                                 learning_unit_year.acronym,
                                                                                 offer_acronym)
    return sent_error_message


def filter_enrollments_by_offer_year(enrollments, offer_year):
    filtered_enrollments = filter(
        lambda enrollment: enrollment.learning_unit_enrollment.offer_enrollment.offer_year == offer_year,
        enrollments
    )
    return list(filtered_enrollments)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def online_encoding_form(request, learning_unit_year_id=None):
    if request.method == 'GET':
        data = get_data_online(request, learning_unit_year_id)
        return layout.render(request, "online_encoding_form.html", data)
    elif request.method == 'POST':
        encoded_exam_enrollments = get_encoded_exam_enrollments(request)
        updated_enrollments = update_enrollments_if_changed(encoded_exam_enrollments, request)

        if messages.get_messages(request):
            data = get_data_online(request, learning_unit_year_id)
            data = _preserve_encoded_values(request, data)
            return layout.render(request, "online_encoding_form.html", data)
        else:
            data = get_data_online(request, learning_unit_year_id)
            send_messages_to_notify_encoding_progress(request, data["enrollments"], data["learning_unit_year"],
                                                      data["is_program_manager"], updated_enrollments)
            return layout.render(request, "online_encoding.html", data)


def _preserve_encoded_values(request, data):
    data = copy.deepcopy(data)
    is_program_manager = data['is_program_manager']
    for enrollment in data['enrollments']:
        enrollment.score_draft = request.POST.get('score_' + str(enrollment.id))
        enrollment.justification_draft = request.POST.get('justification_' + str(enrollment.id))
        if is_program_manager:
            enrollment.score_final = request.POST.get('score_' + str(enrollment.id))
            enrollment.justification_final = request.POST.get('justification_' + str(enrollment.id))
    return data


def get_encoded_exam_enrollments(request):
    enrollment_ids = _extract_id_from_post_data(request)
    enrollments = list(mdl.exam_enrollment
                          .find_by_ids(enrollment_ids)
                          .select_related('learning_unit_enrollment__learning_unit_year')
                          .select_related('learning_unit_enrollment__offer_enrollment__offer_year')
                          .select_related('learning_unit_enrollment__offer_enrollment__student__person'))
    return _extract_encoded_values_from_post_data(enrollments, request)


def _extract_id_from_post_data(request):
    post_data = dict(request.POST.lists())
    return [int(param.split("_")[-1]) for param, value in post_data.items()
            if "score_changed_" in param and next(iter(value or []), None) == "true"]


def _extract_encoded_values_from_post_data(enrollments, request):
    enrollment_with_encoded_values = copy.deepcopy(enrollments)
    for enrollment in enrollment_with_encoded_values:
        enrollment.score_encoded = request.POST.get('score_' + str(enrollment.id))
        enrollment.justification_encoded = request.POST.get('justification_' + str(enrollment.id))
    return enrollment_with_encoded_values


def update_enrollments_if_changed(enrollments, request):
    try:
        user = request.user
        is_program_manager = mdl.program_manager.is_program_manager(user)

        updated_enrollments = []
        for enrollment in enrollments:
            enrollment_updated = update_enrollment_if_changed(enrollment, user, is_program_manager)
            if enrollment_updated:
                updated_enrollments.append(enrollment_updated)

        return updated_enrollments
    except ValidationError as e:
        messages.add_message(request, messages.ERROR, _(e.messages[0]))
    except Exception as e:
        messages.add_message(request, messages.ERROR, _(e.args[0]))


def update_enrollment_if_changed(enrollment, user, is_program_manager):
    enrollment = _clean_score_and_justification(enrollment)

    if _is_enrollment_changed(enrollment, is_program_manager) and \
       _can_modify_exam_enrollment(enrollment, is_program_manager):

        enrollment_updated = _set_score_and_justification(enrollment, is_program_manager)

        if is_program_manager:
            mdl.exam_enrollment.create_exam_enrollment_historic(user, enrollment)

        return enrollment_updated
    return None


def _clean_score_and_justification(enrollment):
    is_decimal_scores_authorized = enrollment.learning_unit_enrollment.learning_unit_year.decimal_scores

    score_clean = None
    if enrollment.score_encoded:
        score_clean = _truncate_decimals(enrollment.score_encoded, is_decimal_scores_authorized)

    justification_clean = None if not enrollment.justification_encoded else enrollment.justification_encoded
    if enrollment.justification_encoded == exam_enrollment_justification_type.SCORE_MISSING:
        justification_clean = score_clean = None

    enrollment_cleaned = copy.deepcopy(enrollment)
    enrollment_cleaned.score_encoded = score_clean
    enrollment_cleaned.justification_encoded = justification_clean
    return enrollment_cleaned


def _truncate_decimals(score, decimal_scores_authorized):
    score = score.strip().replace(',', '.')

    if not score.replace('.', '').isdigit():  # Case not empty string but have alphabetic values
        raise ValueError("scores_must_be_between_0_and_20")

    if decimal_scores_authorized:
        try:
            # Ensure that we cannot have more than 2 decimal
            return Decimal(score).quantize(Decimal(10) ** -2, context=Context(traps=[Inexact]))
        except:
            raise ValueError("score_have_more_than_2_decimal_places")
    else:
        try:
            # Ensure that we cannot have no decimal
            return Decimal(score).quantize(Decimal('1.'), context=Context(traps=[Inexact]))
        except:
            raise ValueError("decimal_score_not_allowed")


def _is_enrollment_changed(enrollment, is_program_manager):
    if not is_program_manager and (not enrollment.score_final or enrollment.justification_final):
        return (enrollment.justification_draft != enrollment.justification_encoded) or \
               (enrollment.score_draft != enrollment.score_encoded)
    else:
        return (enrollment.justification_final != enrollment.justification_encoded) or \
               (enrollment.score_final != enrollment.score_encoded)


def _can_modify_exam_enrollment(enrollment, is_program_manager) :
    if is_program_manager:
        return not mdl.exam_enrollment.is_deadline_reached(enrollment)
    else:
        return not mdl.exam_enrollment.is_deadline_tutor_reached(enrollment) and \
               not enrollment.score_final and not enrollment.justification_final


def _set_score_and_justification(enrollment, is_program_manager):
    enrollment.score_reencoded = None
    enrollment.justification_reencoded = None
    enrollment.score_draft = enrollment.score_encoded
    enrollment.justification_draft = enrollment.justification_encoded
    if is_program_manager:
        enrollment.score_final = enrollment.score_encoded
        enrollment.justification_final = enrollment.justification_encoded

    #Validation
    enrollment.full_clean()
    enrollment.save()

    return enrollment


def bulk_send_messages_to_notify_encoding_progress(request, updated_enrollments, is_program_manager):
    if is_program_manager:
        mail_already_sent_by_learning_unit = set()
        for enrollment in updated_enrollments:
            learning_unit_year = enrollment.learning_unit_enrollment.learning_unit_year
            if learning_unit_year in mail_already_sent_by_learning_unit:
                continue
            all_enrollments = _get_exam_enrollments(request.user,
                                                    learning_unit_year_id = learning_unit_year.id,
                                                    is_program_manager = is_program_manager)
            send_messages_to_notify_encoding_progress(request, all_enrollments, learning_unit_year, is_program_manager,
                                                      updated_enrollments)
            mail_already_sent_by_learning_unit.add(learning_unit_year)


def send_messages_to_notify_encoding_progress(request, all_enrollments, learning_unit_year, is_program_manager,
                                              updated_enrollments):
    if is_program_manager:
        sent_error_messages = __send_messages_for_each_offer_year(all_enrollments,
                                                                  learning_unit_year,
                                                                  updated_enrollments)
        for sent_error_message in sent_error_messages:
            messages.add_message(request, messages.ERROR, "%s" % sent_error_message)


def online_double_encoding_get_form(request, data=None, learning_unit_year_id=None):
    if data['enrollments']:
        return layout.render(request, "online_double_encoding_form.html", data)
    else:
        messages.add_message(request, messages.WARNING, "%s" % _('no_score_encoded_double_encoding_impossible'))
        return online_encoding(request, learning_unit_year_id=learning_unit_year_id)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def online_double_encoding_form(request, learning_unit_year_id=None):
     if request.method == 'GET':
        data = get_data_online_double(learning_unit_year_id, request)
        return online_double_encoding_get_form(request, data, learning_unit_year_id)
     elif request.method == 'POST':
        encoded_exam_enrollments = get_encoded_exam_enrollments(request)
        reencoded_exam_enrollments = validate_rencoded_enrollments(encoded_exam_enrollments, request)

        if messages.get_messages(request):
            data = get_data_online_double(learning_unit_year_id, request)
            data = _preserve_encoded_values(request, data)
            return online_double_encoding_get_form(request, data, learning_unit_year_id)
        elif not reencoded_exam_enrollments:
            messages.add_message(request, messages.WARNING, "%s" % _('no_dubble_score_encoded_comparison_impossible'))
            return online_encoding(request, learning_unit_year_id=learning_unit_year_id)
        else:
            data = get_data_online_double(learning_unit_year_id, request)
            data['enrollments'] = mdl.exam_enrollment.sort_for_encodings(reencoded_exam_enrollments)
            return layout.render(request, "online_double_encoding_validation.html", data)


def validate_rencoded_enrollments(enrollments, request):
    try:
        reencoded_exam_enrollments = []
        for enrollment in enrollments:
            enrollment = _clean_score_and_justification(enrollment)

            enrollment.score_reencoded = enrollment.score_encoded
            enrollment.justification_reencoded = enrollment.justification_encoded
            enrollment.full_clean()
            reencoded_exam_enrollments.append(enrollment)
        return reencoded_exam_enrollments
    except ValidationError as e:
        messages.add_message(request, messages.ERROR, _(e.messages[0]))
    except Exception as e:
        messages.add_message(request, messages.ERROR, _(e.args[0]))




@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def online_double_encoding_validation(request, learning_unit_year_id=None):
    if request.method == 'POST':
        academic_year = mdl.academic_year.current_academic_year()
        is_program_manager = mdl.program_manager.is_program_manager(request.user)
        encoded_exam_enrollments = get_encoded_exam_enrollments(request)
        learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
        updated_enrollments = update_enrollments_if_changed(encoded_exam_enrollments, request)

        if updated_enrollments:
            exam_enrollments = _get_exam_enrollments(request.user,
                                                     learning_unit_year_id=learning_unit_year_id,
                                                     academic_year=academic_year,
                                                     is_program_manager=is_program_manager)
            send_messages_to_notify_encoding_progress(request, exam_enrollments, learning_unit_year, is_program_manager,
                                                   updated_enrollments)
    return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year_id,)))


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def online_encoding_submission(request, learning_unit_year_id):
    is_program_manager = mdl.program_manager.is_program_manager(request.user)
    exam_enrollments = _get_exam_enrollments(request.user,
                                             learning_unit_year_id=learning_unit_year_id,
                                             is_program_manager=is_program_manager)
    submitted_enrollments = []
    draft_scores_not_sumitted_yet = [exam_enrol for exam_enrol in exam_enrollments
                                     if exam_enrol.is_draft and not exam_enrol.is_final]
    not_submitted_enrollments = set([ex for ex in exam_enrollments if not ex.is_final])
    for exam_enroll in draft_scores_not_sumitted_yet:
        if (exam_enroll.score_draft is not None and exam_enroll.score_final is None) \
                or (exam_enroll.justification_draft and not exam_enroll.justification_final):
            submitted_enrollments.append(exam_enroll)
            not_submitted_enrollments.remove(exam_enroll)
        if exam_enroll.is_draft:
            if exam_enroll.score_draft is not None:
                exam_enroll.score_final = exam_enroll.score_draft
            if exam_enroll.justification_draft:
                exam_enroll.justification_final = exam_enroll.justification_draft
            exam_enroll.full_clean()
            exam_enroll.save()
            mdl.exam_enrollment.create_exam_enrollment_historic(request.user, exam_enroll)

    # Send mail to all the teachers of the submitted learning unit on any submission
    all_encoded = len(not_submitted_enrollments) == 0
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    attributions = mdl_attr.attribution.Attribution.objects.filter(learning_unit_year=learning_unit_year)
    persons = list(set([attribution.tutor.person for attribution in attributions]))
    sent_error_message = send_mail.send_mail_after_scores_submission(persons, learning_unit_year.acronym,
                                                                     submitted_enrollments, all_encoded)
    if sent_error_message:
        messages.add_message(request, messages.ERROR, "%s" % sent_error_message)
    return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year_id,)))


@login_required
def upload_score_error(request):
    return layout.render(request, "upload_score_error.html", {})


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def notes_printing(request, learning_unit_year_id=None, tutor_id=None, offer_id=None):
    academic_year = mdl.academic_year.current_academic_year()
    is_program_manager = mdl.program_manager.is_program_manager(request.user)
    exam_enrollments = _get_exam_enrollments(request.user,
                                             learning_unit_year_id=learning_unit_year_id,
                                             academic_year=academic_year,
                                             tutor_id=tutor_id,
                                             offer_year_id=offer_id,
                                             is_program_manager=is_program_manager)
    tutor = mdl.tutor.find_by_user(request.user) if not is_program_manager else None
    sheet_data = mdl.exam_enrollment.scores_sheet_data(exam_enrollments, tutor=tutor)
    return paper_sheet.print_notes(sheet_data)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
def notes_printing_all(request, tutor_id=None, offer_id=None):
    return notes_printing(request, tutor_id=tutor_id, offer_id=offer_id)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def export_xls(request, learning_unit_year_id):
    academic_year = mdl.academic_year.current_academic_year()
    is_program_manager = mdl.program_manager.is_program_manager(request.user)
    exam_enrollments = _get_exam_enrollments(request.user,
                                             learning_unit_year_id=learning_unit_year_id,
                                             academic_year=academic_year,
                                             is_program_manager=is_program_manager,
                                             with_closed_exam_enrollments=False)
    return export_utils.export_xls(exam_enrollments)


def get_score_encoded(enrollments):
    return len(list(filter(lambda e: e.is_final, enrollments)))


def get_data_online(request, learning_unit_year_id):
    """
    Args:
        learning_unit_year_id: The id of an annual learning unit.
        request: default http request.
    Returns:
        a reusable map used by several templates to show data on the user interface.
    """
    academic_yr = mdl.academic_year.current_academic_year()
    is_program_manager = mdl.program_manager.is_program_manager(request.user)
    exam_enrollments = _get_exam_enrollments(request.user,
                                             learning_unit_year_id=learning_unit_year_id,
                                             academic_year=academic_yr,
                                             is_program_manager=is_program_manager)
    number_session = exam_enrollments[0].session_exam.number_session if exam_enrollments else _('none')
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)

    score_responsibles = mdl_attr.attribution.find_all_responsibles(learning_unit_year)
    tutors = mdl.tutor.find_by_learning_unit(learning_unit_year) \
                      .exclude(id__in=[score_responsible.id for score_responsible in score_responsibles])
    progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(exam_enrollments)

    draft_scores_not_submitted = len([exam_enrol for exam_enrol in exam_enrollments
                                      if exam_enrol.is_draft and not exam_enrol.is_final])
    return {'section': 'scores_encoding',
            'academic_year': academic_yr,
            'progress': "{0:.0f}".format(progress),
            'progress_int': progress,
            'enrollments': exam_enrollments,
            'learning_unit_year': learning_unit_year,
            'score_responsibles': score_responsibles,
            'is_program_manager': is_program_manager,
            'is_coordinator': mdl_attr.attribution.is_score_responsible(request.user, learning_unit_year),
            'draft_scores_not_submitted': draft_scores_not_submitted,
            'number_session':number_session,
            'tutors': tutors,
            'exam_enrollments_encoded': get_score_encoded(exam_enrollments),
            'total_exam_enrollments': len(exam_enrollments)}


def get_data_online_double(learning_unit_year_id, request):
    academic_yr = mdl.academic_year.current_academic_year()
    number_session = mdl.session_exam_calendar.find_session_exam_number()

    if mdl.program_manager.is_program_manager(request.user):
        offer_years_managed = mdl.offer_year.find_by_user(request.user, academic_yr=academic_yr)
        total_exam_enrollments = list(mdl.exam_enrollment
                                      .find_for_score_encodings(number_session,
                                                                learning_unit_year_id=learning_unit_year_id,
                                                                offers_year=offer_years_managed,
                                                                academic_year=academic_yr))
        # We must know the total count of enrollments (not only the encoded one) ???
        encoded_exam_enrollments = list(filter(lambda e: e.is_final, total_exam_enrollments))
    elif mdl.tutor.is_tutor(request.user):
        total_exam_enrollments = list(mdl.exam_enrollment
                                      .find_for_score_encodings(number_session,
                                                                learning_unit_year_id=learning_unit_year_id,
                                                                academic_year=academic_yr))
        encoded_exam_enrollments = list(filter(lambda e: e.is_draft and not e.is_final, total_exam_enrollments))
    else:
        encoded_exam_enrollments = []
        total_exam_enrollments = []
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)

    nb_final_scores = get_score_encoded(encoded_exam_enrollments)
    score_responsibles = mdl_attr.attribution.find_all_responsibles(learning_unit_year)
    tutors = mdl.tutor.find_by_learning_unit(learning_unit_year) \
        .exclude(id__in=[score_responsible.id for score_responsible in score_responsibles])
    encoded_exam_enrollments = mdl.exam_enrollment.sort_for_encodings(encoded_exam_enrollments)

    return {'section': 'scores_encoding',
            'academic_year': academic_yr,
            'enrollments': encoded_exam_enrollments,
            'num_encoded_scores': nb_final_scores,
            'learning_unit_year': learning_unit_year,
            'justifications': JUSTIFICATION_TYPES,
            'is_program_manager': mdl.program_manager.is_program_manager(request.user),
            'score_responsibles': score_responsibles,
            'count_total_enrollments': len(total_exam_enrollments),
            'number_session': encoded_exam_enrollments[0].session_exam.number_session
            if len(encoded_exam_enrollments) > 0 else _('none'),
            'tutors': tutors}


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def get_data_specific_criteria(request):
    registration_id = request.POST.get('registration_id', None)
    last_name = request.POST.get('last_name', None)
    first_name = request.POST.get('first_name', None)
    justification = request.POST.get('justification', None)
    offer_year_id = request.POST.get('program', None)

    academic_yr = mdl.academic_year.current_academic_year()
    number_session = mdl.session_exam_calendar.find_session_exam_number()

    offers_year_managed = mdl.offer_year.find_by_user(request.user, academic_yr)

    is_program_manager = mdl.program_manager.is_program_manager(request.user)

    exam_enrollments = []

    if request.method == 'POST':
        if is_program_manager:
            if not registration_id and not last_name and not first_name and not justification and not offer_year_id:
                messages.add_message(request, messages.WARNING, "%s" % _('minimum_one_criteria'))
            else:
                offer_year_id = int(
                    offer_year_id) if offer_year_id else None  # The offer_year_id received in session is a String, not an Int
                exam_enrollments = list(mdl.exam_enrollment.find_for_score_encodings(number_session,
                                                                                     registration_id=registration_id,
                                                                                     student_last_name=last_name,
                                                                                     student_first_name=first_name,
                                                                                     justification=justification,
                                                                                     offer_year_id=offer_year_id,
                                                                                     offers_year=offers_year_managed))
                exam_enrollments = mdl.exam_enrollment.sort_by_offer_acronym_last_name_first_name(exam_enrollments)
                exam_enrollments = _append_session_exam_deadline(exam_enrollments)
                if len(exam_enrollments) == 0:
                    messages.add_message(request, messages.WARNING, "%s" % _('no_result'))
        else:
            messages.add_message(request, messages.ERROR, "%s" % _('user_is_not_program_manager'))
    return {'offer_year_id': offer_year_id,
            'registration_id': registration_id,
            'last_name': last_name,
            'first_name': first_name,
            'justification': justification,
            'academic_year': academic_yr,
            'offer_list': offers_year_managed,
            'number_session': number_session,
            'exam_enrollments': exam_enrollments,
            'is_program_manager': is_program_manager
            }


def _append_session_exam_deadline(exam_enrollments):
    exam_enrollments_with_deadline = copy.deepcopy(exam_enrollments)
    for enrollment in exam_enrollments_with_deadline:
        enrollment.deadline_tutor_computed = mdl.exam_enrollment.get_deadline_tutor_computed(enrollment)
        enrollment.deadline_reached = mdl.exam_enrollment.is_deadline_reached(enrollment)
        enrollment.deadline_tutor_reached = mdl.exam_enrollment.is_deadline_tutor_reached(enrollment)
    return exam_enrollments_with_deadline


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
def search_by_specific_criteria(request):
    if request.method == "POST" and request.POST.get('action') == 'save':
        return specific_criteria_submission(request)
    else:
        return specific_criteria(request)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
def specific_criteria(request):
    data = get_data_specific_criteria(request)
    return layout.render(request, "scores_encoding_by_specific_criteria.html", data)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
def specific_criteria_submission(request):
    encoded_exam_enrollments = get_encoded_exam_enrollments(request)
    updated_enrollments = update_enrollments_if_changed(encoded_exam_enrollments, request)

    if messages.get_messages(request):
        data = get_data_specific_criteria(request)
        data = _preserve_encoded_values(request, data)
        return layout.render(request, "scores_encoding_by_specific_criteria.html", data)
    else:
        is_program_manager = mdl.program_manager.is_program_manager(request.user)
        bulk_send_messages_to_notify_encoding_progress(request, updated_enrollments, is_program_manager)
        if updated_enrollments:
            messages.add_message(request, messages.SUCCESS, "%s %s" % (len(updated_enrollments), _('scores_saved')))

        return specific_criteria(request)


def _get_exam_enrollments(user, learning_unit_year_id=None, tutor_id=None, offer_year_id=None, academic_year=None,
                          is_program_manager=False, with_closed_exam_enrollments=True):
    """
    Args:
        user: The user who's asking for exam_enrollments (for scores' encoding).
        learning_unit_year_id: To filter ExamEnroll by learning_unit_year.
        tutor_id: To filter ExamEnroll by tutor.
        offer_year_id: To filter ExamEnroll by OfferYear.
        academic_year: The academic year for the data returned.
    Returns:
        All exam enrollments for the user passed in parameter (check if it is a program manager or a tutor) and
        a Boolean is_program_manager (True if the user is a program manager, False if the user is a Tutor/coord).
    """
    if not academic_year:
        academic_year = mdl.academic_year.current_academic_year()
    number_session = mdl.session_exam_calendar.find_session_exam_number()
    # Case the user is a program manager
    if is_program_manager:
        tutor = None
        if tutor_id:
            tutor = mdl.tutor.find_by_id(tutor_id)
        if offer_year_id:
            # Get examEnrollments for only one offer
            offers_year = [mdl.offer_year.find_by_id(offer_year_id)]
        else:
            # Get examEnrollments for all offers managed by the program manager
            offers_year = list(mdl.offer_year.find_by_user(user, academic_yr=academic_year))
        exam_enrollments = list(mdl.exam_enrollment
                                .find_for_score_encodings(number_session,
                                                          learning_unit_year_id=learning_unit_year_id,
                                                          tutor=tutor,
                                                          offers_year=offers_year,
                                                          academic_year=academic_year))
        if not with_closed_exam_enrollments:
             exam_enrollments = [enrollment for enrollment in exam_enrollments if
                                 not mdl.exam_enrollment.is_deadline_reached(enrollment)]

    # Case the user is a tutor
    elif mdl.tutor.is_tutor(user):
        # Note : The tutor can't filter by offerYear ; the offer_id is always None. Not necessary to check.
        tutor = mdl.tutor.find_by_user(user)
        exam_enrollments = list(mdl.exam_enrollment
                                .find_for_score_encodings(number_session,
                                                          learning_unit_year_id=learning_unit_year_id,
                                                          tutor=tutor,
                                                          academic_year=academic_year))
        if not with_closed_exam_enrollments:
            exam_enrollments = [enrollment for enrollment in exam_enrollments if
                                not mdl.exam_enrollment.is_deadline_tutor_reached(enrollment)]

    else:
        exam_enrollments = []
    # Ordering by offeryear.acronym, then person.lastname & firstname
    exam_enrollments = mdl.exam_enrollment.sort_for_encodings(exam_enrollments)
    exam_enrollments = _append_session_exam_deadline(exam_enrollments)

    return exam_enrollments


def get_json_data_scores_sheets(tutor_global_id):
    try:
        person = mdl.person.find_by_global_id(tutor_global_id)
        tutor = mdl.tutor.find_by_person(person)
        number_session = mdl.session_exam_calendar.find_session_exam_number()
        academic_yr = mdl.academic_year.current_academic_year()

        if tutor:
            exam_enrollments = list(mdl.exam_enrollment.find_for_score_encodings(number_session,
                                                                                 tutor=tutor,
                                                                                 academic_year=academic_yr))
            data = mdl.exam_enrollment.scores_sheet_data(exam_enrollments, tutor=tutor)
            return json.dumps(data)
        else:
            return json.dumps({})
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError) as ep:
        trace = traceback.format_exc()
        try:
            data = json.dumps({'tutor_global_id': tutor_global_id})
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('PAPER_SHEET'),
                                             message=data,
                                             exception_title='[Catched and retried] - {}'.format(type(ep).__name__),
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            logger.error(trace)
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging :\n {}'.format(log_trace))
        connection.close()
        get_json_data_scores_sheets(tutor_global_id)
    except Exception as e:
        trace = traceback.format_exc()
        try:
            data = json.dumps({'tutor_global_id': tutor_global_id})
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('PAPER_SHEET'),
                                             message=data,
                                             exception_title=type(e).__name__,
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            logger.error(trace)
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging :\n {}'.format(log_trace))
        return None
