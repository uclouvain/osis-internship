##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from base import models as mdl
from base.utils import send_mail, pdf_utils, export_utils
from . import layout

Workflows = type(
    "Workflow",
    (),
    {
         'ONLINE_ENCODING': 'First encoding (online)',
         'DUBBLE_ENCODING_VALIDATION': 'Validation between the first encoding and the dubble encoding (online)',
         'DUBBLE_ENCODING': 'Dubble encoding (online)',
    })


@login_required
def scores_encoding(request):
    tutor = mdl.attribution.get_assigned_tutor(request.user)
    academic_yr = mdl.academic_year.current_academic_year()

    # In case the user is a Tutor
    if tutor:
        scores_encodings = get_data(tutor)
        # sessions_list, faculties, notes_list = get_sessions(None, request, tutor, academic_yr, None)

        return layout.render(request, "assessments/scores_encoding.html",
                                      {'tutor': tutor,
                                       'academic_year': academic_yr,
                                       'notes_list': scores_encodings})

    # In case the user is not a tutor we check whether it is a program manager for the offer.
    else:
        # program_mgr_list = mdl.program_manager.find_by_user(request.user)
        # tutor_sel = None
        # offer_sel = None
        # if program_mgr_list:
        #     tutor_sel_id = request.POST.get('tutor', None)
        #     if tutor_sel_id:
        #         tutor_sel = mdl.tutor.find_by_id(tutor_sel_id)
        #     offer_sel_id = request.POST.get('offer', None)
        #     if offer_sel_id:
        #         offer_sel = mdl.offer_year.find_by_id(offer_sel_id)
        # offer_list = mdl.offer_year.find_by_user(request.user)
        # offer_years_managed = mdl.offer_year.find_by_user(request.user, academic_year=academic_yr)
        return get_data_pgmer(request)
        # return layout.render(request, "assessments/scores_encoding_mgr.html",
        #                               {'notes_list':    data,
        #                                'offer_list':    offer_years_managed,
        #                                'tutor_list':    tutors,
        #                                # 'tutor':         tutor_sel,
        #                                # 'offer':         offer_sel,
        #                                'academic_year': academic_yr})


@login_required
def online_encoding(request, learning_unit_year_id=None):
    data_dict = get_data_online(learning_unit_year_id, request)
    return layout.render(request, "assessments/online_encoding.html", data_dict)


def _truncate_decimals(new_score, new_justification, decimal_scores_authorized):
    """
    Truncate decimals of new scores if decimals are unothorized.
    :param new_score:
    :param new_justification:
    :return:
    """
    if new_score:
        new_score = new_score.strip().replace(',', '.')
        if decimal_scores_authorized:
            new_score = float(new_score)
        else:
            new_score = int(float(new_score))
    elif new_score == '':
        new_score = None
    if new_justification == "None":
        new_justification = None
    return new_score, new_justification


@login_required
def online_encoding_form(request, learning_unit_year_id=None):
    data = get_data_online(learning_unit_year_id, request)
    enrollments = data['enrollments']
    if request.method == 'GET':
        return layout.render(request, "assessments/online_encoding_form.html", data)
                                      # {
                                      #     # 'section':           'scores_encoding',
                                      #  # 'tutor':             data['tutor'],
                                      #  'academic_year':     data['academic_year'],
                                      #  'enrollments':       enrollments,
                                      #  # 'learning_unit':     data['learning_unit'],
                                      #  'justifications':    mdl.exam_enrollment.JUSTIFICATION_TYPES,
                                      #  # 'all_encoded':       data['all_encoded'],
                                      #  # 'tutor_responsible': data['tutor_responsible'],
                                      #  'is_program_manager':          data['is_program_manager']})
    elif request.method == 'POST':
        # Case the user submit his first online scores encodings
        decimal_scores_authorized = data['learning_unit_year'].decimal_scores
        for enrollment in enrollments:
            score = request.POST.get('score_' + str(enrollment.id), None)
            justification = request.POST.get('justification_' + str(enrollment.id), None)
            modification_possible = True
            if not data['is_program_manager'] and (enrollment.score_final or enrollment.justification_final):
                modification_possible = False
            if modification_possible:
                # _save_exam_enrollment(request.user,
                #                       enrollment,
                #                       score, justification,
                #                       data['is_program_manager'],
                #                       decimal_scores=decimal_scores_authorized)
                new_score, new_justification = _truncate_decimals(score, justification, decimal_scores_authorized)
                enrollment.score_reencoded = None
                enrollment.justification_reencoded = None

                # Case it is the program manager who validates the dubble encoding
                if data['is_program_manager']:
                    enrollment.score_final = new_score
                    enrollment.justification_final = new_justification
                    mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment,
                                                                        enrollment.score_final,
                                                                        enrollment.justification_final)
                else:  # Case it is the tutor who validates the dubble encoding
                    enrollment.score_draft = new_score
                    enrollment.justification_draft = new_justification
                enrollment.save()


                # if score:
                #     score = score.strip().replace(',', '.')
                #     if enrollment.session_exam.learning_unit_year.decimal_scores:
                #         if data['is_program_manager']:
                #             enrollment.score_final = float(score)
                #             enrollment.score_draft = float(score)
                #         else:
                #             enrollment.score_draft = float(score)
                #     else:
                #         if data['is_program_manager']:
                #             enrollment.score_final = int(float(score))
                #             enrollment.score_draft = int(float(score))
                #         else:
                #             enrollment.score_draft = int(float(score))
                # else:
                #     if justification == 'None':
                #         if data['is_program_manager']:
                #             enrollment.score_final = None
                #         else:
                #             enrollment.score_draft = None
                #
                # if justification and justification != "None":
                #     if data['is_program_manager']:
                #         enrollment.justification_final = justification
                #         enrollment.justification_draft = justification
                #     else:
                #         enrollment.justification_draft = justification
                # else:
                #     if data['is_program_manager']:
                #         enrollment.justification_final = None
                #     else:
                #         enrollment.justification_draft = None
                # enrollment.save()
        return layout.render(request, "assessments/online_encoding.html", data)
        # if tutor_id:
        #     return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year.learning_unit_id, tutor_id)))
        # else:
        #     return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year.learning_unit_id, )))


@login_required
def online_double_encoding_form(request, learning_unit_year_id=None):
    # learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    # is_program_manager = mdl.program_manager.is_program_manager(request.user, learning_unit_year=learning_unit_year)
    # tutor = mdl.attribution.get_assigned_tutor(request.user)
    # tutor_id = None
    # if tutor:
    #     tutor_id = tutor.id
    data = get_data_online_double(learning_unit_year_id, request)
    exam_enrollments = data['enrollments']
    # learning_unit = data['learning_unit']

    # Case asking for a dubble encoding
    if request.method == 'GET':
        if len(exam_enrollments) > 0:
            return layout.render(request, "assessments/online_double_encoding_form.html", data)
                                          # {'section':        data['section'],
                                          #  'tutor':          data['tutor'],
                                          #  'academic_year':  data['academic_year'],
                                          #  'enrollments':    enrollments,
                                          #  'learning_unit':  learning_unit,
                                          #  'justifications': data['justifications'],
                                          #  'is_program_manager': is_program_manager})
        else:
            messages.add_message(request, messages.WARNING, "%s" % _('no_score_encoded_double_encoding_impossible'))
            return online_encoding(request, learning_unit_year_id=learning_unit_year_id)
    elif request.method == 'POST':
        # Case asking for a comparison with scores dubble encoded
        decimal_scores_authorized = data['learning_unit_year'].decimal_scores

        for exam_enrol in exam_enrollments:
            score_dubble_encoded = request.POST.get('score_' + str(exam_enrol.id), None)
            justification_dubble_encoded = request.POST.get('justification_' + str(exam_enrol.id), None)
            # _save_exam_enrollment(request.user,
            #                       exam_enrol,
            #                       score_validated,
            #                       justification_validated,
            #                       is_program_manager,
            #                       decimal_scores=decimal_scores_authorized)

            score_dubble_encoded, justification_dubble_encoded = _truncate_decimals(score_dubble_encoded,
                                                                                    justification_dubble_encoded,
                                                                                    decimal_scores_authorized)
            exam_enrol.score_reencoded = score_dubble_encoded
            exam_enrol.justification_reencoded = justification_dubble_encoded
            exam_enrol.save()

        # Needs to filter by examEnrollments where the score_reencoded and justification_reencoded are not None
        exam_enrollments = [exam_enrol for exam_enrol in exam_enrollments
                            if exam_enrol.score_reencoded or exam_enrol.justification_reencoded]
        data['enrollments'] = exam_enrollments
        if len(exam_enrollments) == 0:
            messages.add_message(request, messages.WARNING, "%s" % _('no_dubble_score_encoded_comparison_impossible'))
            return online_encoding(request, learning_unit_year_id=learning_unit_year_id)
        return layout.render(request, "assessments/online_double_encoding_validation.html", data)
                             # {'section': 'scores_encoding',
                             #  # 'tutor': tutor,
                             #  'academic_year': academic_year,
                             #  'learning_unit_year': learning_unit_year,
                             #  'enrollments': exam_enrollments,
                             #  'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES,
                             #  'is_program_manager': data['is_program_manager']})

        # programme manager encoding
        # for enrollment in enrollments:
        #     score = request.POST.get('score_' + str(enrollment.id), None)
        #     score = score.strip().replace(',', '.')
        #     if score:
        #         if enrollment.session_exam.learning_unit_year.decimal_scores:
        #             enrollment.score_reencoded = float(score)
        #         else:
        #             enrollment.score_reencoded = int(float(score))
        #     else:
        #         enrollment.score_reencoded = None
        #     if request.POST.get('justification_' + str(enrollment.id), None) == "None":
        #         justification = None
        #     else:
        #         justification = request.POST.get('justification_' + str(enrollment.id), None)
        #     if justification:
        #         enrollment.justification_reencoded = justification
        #     else:
        #         enrollment.justification_reencoded = None
        #     enrollment.save()
        # return HttpResponseRedirect(reverse('online_double_encoding_validation', args=(learning_unit_year_id,)))
        # if is_program_manager:
        #     return HttpResponseRedirect(reverse('online_double_encoding_validation', args=(learning_unit.id,)))
        # else:
        #     return HttpResponseRedirect(reverse('online_double_encoding_validation', args=(learning_unit.id, tutor_id)))


@login_required
def online_double_encoding_validation(request, learning_unit_year_id=None, tutor_id=None):
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    academic_year = mdl.academic_year.current_academic_year()
    # learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
    # is_program_manager = False
    # if mdl.program_manager.is_program_manager(request.user):
    #     is_program_manager = True
    #     offer_years_managed = mdl.offer_year.find_by_user(request.user, academic_year=academic_year)
    #     exam_enrollments = list(mdl.exam_enrollment.find_by_learning_unit_year_id(learning_unit_year_id,
    #                                                                               offers_year=offer_years_managed))
    # else:
    #     exam_enrollments = list(mdl.exam_enrollment.find_by_learning_unit_year_id(learning_unit_year_id))
    exam_enrollments, is_program_manager = _get_exam_enrollments(request.user,
                                                                 learning_unit_year_id=learning_unit_year_id,
                                                                 academic_year=academic_year)

    # is_program_manager = False
    #
    # if tutor_id:
    #     tutor = mdl.tutor.find_by_id(tutor_id)
    # else:
    #     is_program_manager = True
    #     tutor = mdl.attribution.get_assigned_tutor(request.user)

    if request.method == 'GET':
        # sessions_list, faculties, notes_list = get_sessions(learning_unit_id, request, tutor, academic_year, None)
        # all_enrollments = []
        # if sessions_list:
        #     for sessions in sessions_list:
        #         for session in sessions:
        #             if is_program_manager:
        #                 enrollments = list(mdl.exam_enrollment.find_exam_enrollments_double_pgmer_by_session(session))
        #             else:
        #                 enrollments = list(mdl.exam_enrollment.find_exam_enrollments_drafts_existing_by_session(session))
        #             if enrollments:
        #                 all_enrollments = all_enrollments + enrollments
        return layout.render(request, "assessments/online_double_encoding_validation.html",
                                      {'section': 'scores_encoding',
                                       # 'tutor': tutor,
                                       'academic_year': academic_year,
                                       'learning_unit_year': learning_unit_year,
                                       'enrollments': exam_enrollments,
                                       'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES,
                                       'is_program_manager': is_program_manager})
    elif request.method == 'POST':
        # Case the user validate his choice between the first and the dubble encoding
        sessions_exam_still_open = set() # contains all SessionExams where the encoding is not terminated (progression < 100%)
        all_sessions_exam = set() # contains all sessions exams in exam_enrollments list

        decimal_scores_authorized = learning_unit_year.decimal_scores

        for exam_enrol in exam_enrollments:
            score_validated = request.POST.get('score_' + str(exam_enrol.id), None)
            justification_validated = request.POST.get('justification_' + str(exam_enrol.id), None)

            new_score, new_justification = _truncate_decimals(score_validated, justification_validated, decimal_scores_authorized)
            exam_enrol.score_reencoded = None
            exam_enrol.justification_reencoded = None

            # A choice must be done between the first and the dubble encoding to save new changes.
            if new_score or new_justification:
                # Case it is the program manager who validates the dubble encoding
                if is_program_manager:
                    exam_enrol.score_final = new_score
                    exam_enrol.justification_final = new_justification
                    mdl.exam_enrollment.create_exam_enrollment_historic(request.user, exam_enrol,
                                                                        exam_enrol.score_final,
                                                                        exam_enrol.justification_final)
                else:  # Case it is the tutor who validates the dubble encoding
                    exam_enrol.score_draft = new_score
                    exam_enrol.justification_draft = new_justification
                exam_enrol.save()

            # if score_validated or justification_validated:
            #     if score_validated:
            #         score_validated = score_validated.strip().replace(',', '.')
            #         if decimal_scores_authorized:
            #             score_validated = float(score_validated)
            #         else:
            #             score_validated = int(float(score_validated))
            #     if justification_validated == "None":
            #         justification_validated = None
            #
            #     exam_enrol.score_reencoded = None
            #     exam_enrol.justification_reencoded = None
            #
            #     if is_program_manager:
            #         exam_enrol.score_final = score_validated
            #         exam_enrol.justification_final = justification_validated
            #         mdl.exam_enrollment.create_exam_enrollment_historic(request.user, exam_enrol,
            #                                                         exam_enrol.score_final,
            #                                                         exam_enrol.justification_final)
            #     else: # Case it is the tutor who validates the dubble encoding
            #         exam_enrol.score_draft = score_validated
            #         exam_enrol.justification_draft = justification_validated
            #     exam_enrol.save()

            if not exam_enrol.score_final and not exam_enrol.justification_final:
                sessions_exam_still_open.add(exam_enrol.session_exam)
            all_sessions_exam.add(exam_enrol.session_exam)

        sessions_exam_to_close = all_sessions_exam - sessions_exam_still_open
        for session_exam in sessions_exam_to_close:
            session_exam.status = 'CLOSED'
            session_exam.save()

        # if min_one_choosen:
        #     messages.add_message(request, messages.WARNING,
        #                          "%s" % _('no_dubble_score_encoded_comparison_impossible'))
        #     return online_encoding(request, learning_unit_year_id=learning_unit_year_id)

        return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year_id,)))

        # sessions_list, faculties, notes_list = get_sessions(learning_unit_id, request, tutor, academic_year, None)
        # if sessions_list:
        #     for sessions in sessions_list:
        #         for session in sessions:
        #             enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session(session))
        #             if enrollments:
        #                 for enrollment in enrollments:
        #                     score = request.POST.get('score_' + str(enrollment.id), None)
        #                     if score:
        #                         score = score.strip().replace(',', '.')
        #                     justification = request.POST.get('justification_' + str(enrollment.id), None)
        #                     if justification == "None":
        #                         justification = None
        #
        #                     if is_program_manager:
        #                         if score:
        #                             if enrollment.session_exam.learning_unit_year.decimal_scores:
        #                                 enrollment.score_final = float(score)
        #                             else:
        #                                 enrollment.score_final = int(float(score))
        #                             enrollment.score_draft = enrollment.score_final
        #                         else:
        #                             if justification:
        #                                 enrollment.score_draft = None
        #                                 enrollment.score_final = None
        #                         enrollment.score_reencoded = None
        #
        #                         if justification:
        #                             enrollment.justification_final = justification
        #                             enrollment.justification_draft = enrollment.justification_final
        #
        #                         if score or justification:
        #                             mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment,
        #                                                                                 enrollment.score_final,
        #                                                                                 enrollment.justification_final)
        #                         enrollment.justification_reencoded = None
        #                         enrollment.save()
        #                     else:
        #                         # tutor
        #                         if score:
        #                             if enrollment.session_exam.learning_unit_year.decimal_scores:
        #                                 enrollment.score_draft = float(score)
        #                             else:
        #                                 enrollment.score_draft = int(float(score))
        #                         else:
        #                             if justification:
        #                                 enrollment.score_draft = None
        #
        #                         enrollment.score_reencoded = None
        #
        #                         if justification:
        #                             enrollment.justification_draft = justification
        #
        #                         enrollment.justification_reencoded = None
        #                         enrollment.save()

                        # all_encoded = True
                        # for enrollment in enrollments:
                        #     if not enrollment.score_final and not enrollment.justification_final:
                        #         all_encoded = False
                        #
                        # if all_encoded:
                        #     session.status = 'CLOSED'
                        #     session.save()
        # if tutor_id:
        #     return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit.id, tutor_id)))
        # else:
        #     return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit.id,)))


# @login_required
# <<<<<<< Updated upstream
# def online_encoding_submission(request, learning_unit_id):
#     tutor = None
#     program_mgr_list = mdl.program_manager.find_by_user(request.user)
#     if not program_mgr_list:
#         tutor = mdl.tutor.find_by_user(request.user)
#
#     academic_yr = mdl.academic_year.current_academic_year()
#
#     learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
#
#     sessions_list, faculties, notes_list = get_sessions(learning_unit, request, tutor, academic_yr, None)
#
#     if sessions_list:
#         submitted_enrollments = []
#         all_encoded = True
#         for sessions in sessions_list:
#             for session in sessions:
#                 enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_by_session(session)
#                 for enrollment in enrollments:
#                     if (enrollment.score_draft and not enrollment.score_final)\
#                             or (enrollment.justification_draft and not enrollment.justification_final):
#                         submitted_enrollments.append(enrollment)
#                     if enrollment.score_draft or enrollment.justification_draft:
#                         if enrollment.score_draft:
#                             enrollment.score_final = enrollment.score_draft
#                         if enrollment.justification_draft:
#                             enrollment.justification_final = enrollment.justification_draft
#                         enrollment.save()
#                         mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment,
#                                                                             enrollment.score_final,
#                                                                             enrollment.justification_final)
#                     else:
#                         all_encoded = False
#
#                 if all_encoded:
#                     session.status = 'CLOSED'
#                     session.save()
# =======
def online_encoding_submission(request, learning_unit_year_id):
    exam_enrollments, is_program_manager = _get_exam_enrollments(request.user,
                                                                 learning_unit_year_id=learning_unit_year_id)

    # # Case the user is a program manager
    # if mdl.program_manager.is_program_manager(request.user):
    #     is_program_manager = True
    #     # Get examEnrollments for all offers managed by the program manager
    #     offers_year = list(mdl.offer_year.find_by_user(request.user, academic_year=academic_year))
    #     exam_enrollments = list(mdl.exam_enrollment \
    #         .find_by_learn_unit_year_tutor_offers_year(learning_unit_year_id=learning_unit_year_id,
    #                                                    offers_year=offers_year))
    # else:  # Case the user is a tutor
    #     tutor = mdl.tutor.find_by_user(request.user)
    #     exam_enrollments = list(mdl.exam_enrollment \
    #         .find_by_learn_unit_year_tutor_offers_year(learning_unit_year_id=learning_unit_year_id,
    #                                                    tutor=tutor))
    submitted_enrollments = []
    sessions_exam_still_open = set()  # contains all SessionExams where the encoding is not terminated (progression < 100%)
    all_sessions_exam = set()  # contains all sessions exams in exam_enrollments list
    for exam_enroll in exam_enrollments:
        if (exam_enroll.score_draft and not exam_enroll.score_final) \
                or (exam_enroll.justification_draft and not exam_enroll.justification_final):
            submitted_enrollments.append(exam_enroll)
        if exam_enroll.score_draft or exam_enroll.justification_draft:
            if exam_enroll.score_draft:
                exam_enroll.score_final = exam_enroll.score_draft
            if exam_enroll.justification_draft:
                exam_enroll.justification_final = exam_enroll.justification_draft
            # exam_enroll.score_draft = None
            # exam_enroll.justification_draft = None
            exam_enroll.save()
            mdl.exam_enrollment.create_exam_enrollment_historic(request.user, exam_enroll,
                                                                    exam_enroll.score_final,
                                                                    exam_enroll.justification_final)

        if not exam_enroll.score_final and not exam_enroll.justification_final:
            sessions_exam_still_open.add(exam_enroll.session_exam)
        all_sessions_exam.add(exam_enroll.session_exam)

    sessions_exam_to_close = all_sessions_exam - sessions_exam_still_open
    for session_exam in sessions_exam_to_close:
        session_exam.status = 'CLOSED'
        session_exam.save()




    # tutor = None
    # program_mgr_list = mdl.program_manager.find_by_user(request.user)
    # if not program_mgr_list:
    #     tutor = mdl.tutor.find_by_user(request.user)
    #
    # academic_yr = mdl.academic_year.current_academic_year()
    #
    # learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
    #
    # sessions_list, faculties, notes_list = get_sessions(learning_unit, request, tutor, academic_yr, None)
    #
    # if sessions_list:
    #     for sessions in sessions_list:
    #         for session in sessions:
    #             enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_by_session(session)
    #             all_encoded = True
    #             for enrollment in enrollments:
    #                 if enrollment.score_draft or enrollment.justification_draft:
    #                     if enrollment.score_draft:
    #                         enrollment.score_final = enrollment.score_draft
    #                     if enrollment.justification_draft:
    #                         enrollment.justification_final = enrollment.justification_draft
    #                     enrollment.save()
    #                     mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment,
    #                                                                         enrollment.score_final,
    #                                                                         enrollment.justification_final)
    #                 else:
    #                     all_encoded = False
    #
    #             if all_encoded:
    #                 session.status = 'CLOSED'
    #                 session.save()

    # Send mail to all the teachers of the submitted learning unit on any submission
    all_encoded = len(sessions_exam_still_open) == 0
    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
    attributions = mdl.attribution.Attribution.objects.filter(learning_unit=learning_unit_year.learning_unit)
    persons = [attribution.tutor.person for attribution in attributions if attribution.function == 'PROFESSOR']
    send_mail.send_mail_after_scores_submission(persons, learning_unit_year.acronym, submitted_enrollments, all_encoded)
    # if tutor:
    #     return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id, tutor.id)))
    # else:
    return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year_id,)))


# @login_required
# def notes_printing(request, session_exam_id, learning_unit_year_id):
#     academic_year = mdl.academic_year.current_academic_year()
#     session_exam = mdl.session_exam.find_session_by_id(session_exam_id)
#     return pdf_utils.print_notes(request.user, academic_year, session_exam, learning_unit_year_id)


@login_required
def upload_score_error(request):
    return layout.render(request, "assessments/upload_score_error.html", {})


@login_required
def notes_printing(request, learning_unit_year_id=None, tutor_id=None, offer_id=None):

    academic_year = mdl.academic_year.current_academic_year()
    learning_unit_id = int(-1) # To refactor in PdfUtils...
    if learning_unit_year_id:
        learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)
        learning_unit_id = learning_unit_year.learning_unit.id
    # is_program_manager = False

    exam_enrollments, is_program_manager = _get_exam_enrollments(request.user,
                                                                 learning_unit_year_id=learning_unit_year_id,
                                                                 academic_year=academic_year,
                                                                 tutor_id=tutor_id,
                                                                 offer_year_id=offer_id)

    # # Case the user is a program manager
    # if mdl.program_manager.is_program_manager(request.user):
    #     is_program_manager = True
    #     tutor = None
    #     if tutor_id:
    #         tutor = mdl.tutor.find_by_id(tutor_id)
    #     if offer_id:
    #         # Get examEnrollments for only one offer
    #         offers_year = [mdl.offer_year.find_by_id(offer_id)]
    #     else:
    #         # Get examEnrollments for all offers managed by the program manager
    #         offers_year = list(mdl.offer_year.find_by_user(request.user, academic_year=academic_year))
    #     exam_enrollments = list(mdl.exam_enrollment\
    #                           .find_by_learn_unit_year_tutor_offers_year(learning_unit_year_id=learning_unit_year_id,
    #                                                                      tutor=tutor,
    #                                                                      offers_year=offers_year))
    # else: # Case the user is a tutor
    #     # Note : The tutor can't filter by offerYear ; the offer_id is always None. Not necessary to check.
    #     tutor = mdl.tutor.find_by_user(request.user)
    #     exam_enrollments = list(mdl.exam_enrollment \
    #         .find_by_learn_unit_year_tutor_offers_year(learning_unit_year_id=learning_unit_year_id,
    #                                                    tutor=tutor))

    # # if tutor:
    # is_fac = False
    # # In case the user is not a tutor we check whether it is a program manager for the offer.
    # # else:
    # program_mgr_list = mdl.program_manager.find_by_user(request.user)
    # for program_mgr in program_mgr_list:
    #     is_fac = True
    #     break
    # if learning_unit_id == -1:
    #     sessions_list, faculties, notes_list = get_sessions(None, request, tutor, academic_year, offer_id)
    # else:
    #     sessions_list, faculties, notes_list = get_sessions(learning_unit_id, request, tutor, academic_year, None)

    return pdf_utils.print_notes(request.user, academic_year, learning_unit_id, is_program_manager, exam_enrollments)


@login_required
def notes_printing_all(request, tutor_id=None, offer_id=None):
    return notes_printing(request, tutor_id=tutor_id, offer_id=offer_id)
    # academic_year = mdl.academic_year.current_academic_year()
    # is_fac = False
    # program_mgr_list = mdl.program_manager.find_by_user(request.user)
    # for program_mgr in program_mgr_list:
    #     is_fac = True
    #     break
    # tutor = None
    # if tutor_id:
    #     tutor = mdl.tutor.find_by_id(tutor_id)
    # sessions_list, faculties, notes_list = get_sessions(None, request, tutor, academic_year, offer_id)
    # return pdf_utils.print_notes(request.user, academic_year, int(-1), is_fac, sessions_list, tutor=tutor)


@login_required
def export_xls(request, learning_unit_year_id, academic_year_id):
    academic_year = mdl.academic_year.current_academic_year()
    exam_enrollments, is_program_manager = _get_exam_enrollments(request.user,
                                                                 learning_unit_year_id=learning_unit_year_id,
                                                                 academic_year=academic_year)

    # tutor = mdl.tutor.find_by_user(request.user)
    # if tutor:
    #     is_fac = False
    # # In case the user is not a tutor we check whether it is a program manager for the offer.
    # else:
    #     program_mgr_list = mdl.program_manager.find_by_user(request.user)
    #     for program_mgr in program_mgr_list:
    #         is_fac = True
    #         break
    # sessions_list, faculties, notes_list = get_sessions(learning_unit_year.learning_unit.id,
    #                                                     request,
    #                                                     tutor,
    #                                                     academic_year,
    #                                                     None)

    return export_utils.export_xls(academic_year_id, is_program_manager, exam_enrollments)


# def get_sessions(learning_unit_param, request, tutor, academic_yr, offer_id):
#     sessions_list = []
#     learning_unit_list = []
#
#     faculties = []
#     notes_list = []
#
#     if tutor or offer_id:
#         if offer_id:
#             offer_year = mdl.offer_year.find_by_id(offer_id)
#         else:
#             offer_year = None
#         sessions = mdl.session_exam.find_current_sessions_by_tutor_offer(tutor, academic_yr, learning_unit_param,
#                                                                          offer_year)
#         sessions_list.append(sessions)
#         learning_unit_list = []
#         dict_progress = {}
#         dict_progress_ok = {}
#
#         for session in sessions:
#             learning_unit = session.learning_unit_year.learning_unit
#             enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session(session))
#
#             if learning_unit in learning_unit_list:
#                 dict_progress[learning_unit.acronym] += len(enrollments)
#             else:
#                 dict_progress[learning_unit.acronym] = len(enrollments)
#                 learning_unit_list.append(learning_unit)
#             value = get_score_encoded(enrollments)
#             if learning_unit.acronym in dict_progress_ok:
#                 dict_progress_ok[learning_unit.acronym] = dict_progress_ok[learning_unit.acronym]+value
#             else:
#                 dict_progress_ok[learning_unit.acronym] = value
#
#         notes = Notes()
#         notes.tutor = tutor
#         l_lu_detail = []
#         notes_list = []
#         learning_unit_list = order_learning_unit_list_by_acronym(learning_unit_list)
#         for learning_unit_elt in learning_unit_list:
#             notes_detail = NotesDetail()
#             notes_detail.lu = learning_unit_elt
#             notes_detail.nb_notes_encoded = dict_progress_ok[learning_unit_elt.acronym]
#             notes_detail.nb_student = dict_progress[learning_unit_elt.acronym]
#             l_lu_detail.append(notes_detail)
#         notes.lu_list = l_lu_detail
#         notes_list.append(notes)
#     # In case the user is not a tutor we check whether it is a program manager for the offer.
#     else:
#         program_mgr_list = mdl.program_manager.find_by_user(request.user, academic_year=academic_yr)
#         all_enrollments = []
#
#         for program_mgr in program_mgr_list:
#             if program_mgr.offer_year:
#                 notes = Notes()
#                 sessions = mdl.session_exam.find_sessions_by_offer(program_mgr.offer_year, academic_yr,
#                                                                    learning_unit_param)
#                 sessions_list.append(sessions)
#
#                 faculty = program_mgr.offer_year.structure
#
#                 notes.structure = faculty
#                 if faculty not in faculties:
#                     faculties.append(faculty)
#                 learning_unit_list = []
#                 dict_progress = {}
#                 dict_progress_ok = {}
#                 for session in sessions:
#                     learning_unit = session.learning_unit_year.learning_unit
#                     enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session(session))
#
#                     if enrollments:
#                         all_enrollments = all_enrollments + enrollments
#
#                     if session.learning_unit_year.learning_unit in learning_unit_list:
#                         dict_progress[learning_unit.acronym] += len(enrollments)
#                     else:
#                         learning_unit = session.learning_unit_year.learning_unit
#                         dict_progress[learning_unit.acronym] = len(enrollments)
#                         learning_unit_list.append(learning_unit)
#                     value = get_score_encoded(enrollments)
#                     if learning_unit.acronym in dict_progress_ok:
#                         dict_progress_ok[learning_unit.acronym] = dict_progress_ok[learning_unit.acronym]+value
#                     else:
#                         dict_progress_ok[learning_unit.acronym] = value
#                 l_lu_detail = []
#                 for learning_unit_elt in learning_unit_list:
#                     notes_detail = NotesDetail()
#                     notes_detail.lu = learning_unit_elt
#                     notes_detail.nb_notes_encoded = dict_progress_ok[learning_unit_elt.acronym]
#                     notes_detail.nb_student = dict_progress[learning_unit_elt.acronym]
#                     l_lu_detail.append(notes_detail)
#                 notes.lu_list = l_lu_detail
#                 notes_list.append(notes)
#         notes = Notes()
#         learning_unit_list = order_learning_unit_list_by_acronym(learning_unit_list)
#         for learning_unit_elt in learning_unit_list:
#             notes_detail = NotesDetail()
#             notes_detail.lu = learning_unit_elt
#             notes_detail.nb_notes_encoded = dict_progress_ok[learning_unit_elt.acronym]
#             notes_detail.nb_student = dict_progress[learning_unit_elt.acronym]
#             l_lu_detail.append(notes_detail)
#         notes.lu_list = l_lu_detail
#         notes_list = [notes]
#
#     return sessions_list, faculties, notes_list


def get_score_encoded(enrollments):
    progress = 0
    if enrollments:
        for e in enrollments:
            if e.score_final or e.justification_final:
                progress += 1
    return progress


def get_data(tutor):
    exam_enrollments = mdl.exam_enrollment.find_for_score_encodings(mdl.session_exam.find_session_exam_number(),
                                                                    tutor=tutor)

    # Grouping by learningUnitYear
    group_by_learn_unit_year = {}
    for exam_enrol in exam_enrollments:
        learn_unit_year = exam_enrol.session_exam.learning_unit_year
        score_encoding = group_by_learn_unit_year.get(learn_unit_year.id)
        if score_encoding:
            if exam_enrol.score_final or exam_enrol.justification_final:
                score_encoding['exam_enrollments_encoded'] += 1
            score_encoding['total_exam_enrollments'] += 1
        else:
            if exam_enrol.score_final or exam_enrol.justification_final:
                exam_enrollments_encoded = 1
            else :
                exam_enrollments_encoded = 0
            group_by_learn_unit_year[learn_unit_year.id] = {'learning_unit_year': learn_unit_year,
                                                            'exam_enrollments_encoded': exam_enrollments_encoded,
                                                            'total_exam_enrollments': 1}

    return group_by_learn_unit_year.values()

    # academic_yr = mdl.academic_year.current_academic_year()
    # tutor = mdl.tutor.find_by_user(request.user)note_detail.exam_enrollments_encoded==note_detail.total_exam_enrollments
    # sessions_list, faculties, notes_list = get_sessions(None, request, tutor, academic_yr, None)
    #
    # return {'section':       'scores_encoding',
    #         'tutor':         tutor,
    #         'academic_year': academic_yr,
    #         'notes_list':    notes_list}


def get_data_online(learning_unit_year_id, request):
    academic_yr = mdl.academic_year.current_academic_year()
    exam_enrollments, is_program_manager = _get_exam_enrollments(request.user,
                                                                 learning_unit_year_id=learning_unit_year_id,
                                                                 academic_year=academic_yr)
    # if mdl.program_manager.is_program_manager(request.user):
    #     offer_years_managed = mdl.offer_year.find_by_user(request.user, academic_year=academic_yr)
    #     exam_enrollments = list(mdl.exam_enrollment.find_by_learning_unit_year_id(learning_unit_year_id,
    #                                                                               offers_year=offer_years_managed))
    # else:
    #     exam_enrollments = list(mdl.exam_enrollment.find_by_learning_unit_year_id(learning_unit_year_id))

    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)

    coordinator = mdl.tutor.find_responsible(learning_unit_year.learning_unit)
    progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(exam_enrollments)
    nb_scores_encoded = len([exam_enrol for exam_enrol in exam_enrollments
                             if exam_enrol.justification_final or exam_enrol.score_final])

    return {'section': 'scores_encoding',
            # 'tutor': tutor,
            'academic_year': academic_yr,
            'progress': "{0:.0f}".format(progress),
            'enrollments': exam_enrollments,
            'num_encoded_scores': nb_scores_encoded,
            # 'learning_unit': learning_unit,
            # 'all_encoded': all_encoded,
            'learning_unit_year': learning_unit_year,
            'coordinator': coordinator,
            # 'tutor_responsible': tutor_responsible,
            'is_program_manager': mdl.program_manager.is_program_manager(request.user)}


    # tutor = None
    # coordinator = False
    # a_learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
    # is_programme_manager = False
    # if tutor_id:
    #     tutor = mdl.tutor.find_by_id(tutor_id)
    #     coordinator = mdl.attribution.find_by_function(tutor, learning_unit_id, 'COORDINATOR')
    #
    #     tutor_responsible = mdl.tutor.find_responsible(a_learning_unit)
    # else:
    #     program_mgr_list = mdl.program_manager.find_by_user(request.user)
    #     if not program_mgr_list:
    #         tutor = mdl.tutor.find_by_user(request.user)
    #     else:
    #         is_programme_manager = True
    #     tutor_responsible = mdl.tutor.find_responsible(a_learning_unit)
    #
    # academic_yr = mdl.academic_year.current_academic_year()
    # learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
    # learning_unit_year = mdl.learning_unit_year.search(academic_year_id=academic_yr,
    #                                                    learning_unit=learning_unit).first()
    # sessions_list, faculties, notes_list = get_sessions(learning_unit, request, tutor, academic_yr, None)
    #
    # tot_enrollments = []
    # tot_progress = []
    # tot_num_encoded_scores = 0
    # all_encoded = True
    #
    # if sessions_list:
    #     for sessions in sessions_list:
    #         for session in sessions:
    #             enrollments = mdl.exam_enrollment.find_exam_enrollments_by_session(session)
    #             num_encoded_scores = mdl.exam_enrollment.count_encoded_scores(enrollments)
    #             tot_enrollments.extend(enrollments)
    #             tot_progress.extend(tot_progress)
    #             tot_num_encoded_scores += num_encoded_scores
    #             if session.status == 'OPEN':
    #                 all_encoded = False
    #
    # progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(tot_enrollments)
    # return {'section':            'scores_encoding',
    #         'tutor':              tutor,
    #         'academic_year':      academic_yr,
    #         'progress':           "{0:.0f}".format(progress),
    #         'enrollments':        tot_enrollments,
    #         'num_encoded_scores': tot_num_encoded_scores,
    #         'learning_unit':      learning_unit,
    #         'all_encoded':        all_encoded,
    #         'learning_unit_year': learning_unit_year,
    #         'coordinator':        coordinator,
    #         'tutor_responsible':  tutor_responsible,
    #         'is_pgmer':           is_programme_manager}


def get_data_online_double(learning_unit_year_id, request):
    academic_yr = mdl.academic_year.current_academic_year()
    if mdl.program_manager.is_program_manager(request.user):
        offer_years_managed = mdl.offer_year.find_by_user(request.user, academic_year=academic_yr)
        exam_enrollments = list(mdl.exam_enrollment.find_for_score_encodings(mdl.session_exam.find_session_exam_number(),
                                                                             learning_unit_year_id=learning_unit_year_id,
                                                                             with_justification_or_score_final=True,
                                                                             offers_year=offer_years_managed))
    else:
        exam_enrollments = list(mdl.exam_enrollment.find_for_score_encodings(mdl.session_exam.find_session_exam_number(),
                                                                             learning_unit_year_id=learning_unit_year_id,
                                                                             with_justification_or_score_draft=True))

    learning_unit_year = mdl.learning_unit_year.find_by_id(learning_unit_year_id)

    nb_scores_encoded = len([exam_enrol for exam_enrol in exam_enrollments
                             if exam_enrol.justification_final or exam_enrol.score_final])

    return {'section': 'scores_encoding',
            'academic_year': academic_yr,
            'enrollments': exam_enrollments,
            'num_encoded_scores': nb_scores_encoded,
            'learning_unit_year': learning_unit_year,
            'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES,
            'is_program_manager': mdl.program_manager.is_program_manager(request.user)
            }




    # is_programme_manager = False
    # if tutor_id:
    #     tutor = mdl.tutor.find_by_id(tutor_id)
    # else:
    #     tutor = None
    #     program_mgr_list = mdl.program_manager.find_by_user(request.user)
    #     if not program_mgr_list:
    #         tutor = mdl.tutor.find_by_user(request.user)
    #     else:
    #         is_programme_manager = True
    #
    # academic_yr = mdl.academic_year.current_academic_year()
    #
    # learning_unit = mdl.learning_unit.find_by_id(learning_unit_id)
    #
    # sessions_list, faculties, notes_list = get_sessions(learning_unit, request, tutor, academic_yr, None)
    # tot_enrollments = []
    # tot_progress = []
    # tot_num_encoded_scores = 0
    #
    # if sessions_list:
    #     for sessions in sessions_list:
    #         for session in sessions:
    #             if is_programme_manager:
    #                 enrollments = mdl.exam_enrollment.find_exam_enrollments_final_existing_pgmer_by_session(session)
    #             else:
    #                 enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_existing_by_session(session)
    #             num_encoded_scores = mdl.exam_enrollment.count_encoded_scores(enrollments)
    #             tot_enrollments.extend(enrollments)
    #             tot_progress.extend(tot_progress)
    #             tot_num_encoded_scores = tot_num_encoded_scores+num_encoded_scores
    #
    # return {'section': 'scores_encoding',
    #         'tutor': tutor,
    #         'academic_year': academic_yr,
    #         'enrollments': tot_enrollments,
    #         'num_encoded_scores': tot_num_encoded_scores,
    #         'learning_unit': learning_unit,
    #         'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES}


def get_data_pgmer(request, offer_year_id=None, tutor_id=None):
    academic_yr = mdl.academic_year.current_academic_year()
    offer_years_managed = request.session.get('offer_years_managed',
                                              mdl.offer_year.find_by_user(request.user, academic_year=academic_yr))

    all_tutors = request.session.get('all_tutors',
                                     mdl.tutor.find_by_program_manager(offer_years_managed))

    if not offer_year_id:
        scores_encodings = list(mdl.scores_encoding.search(request.user))
        # Adding exam_enrollments_encoded & total_exam_enrollments
        # from each offers year for a matching learning_unit_year
        group_by_learning_unit = {}
        for score_encoding in scores_encodings:
            try:
                group_by_learning_unit[score_encoding.learning_unit_year_id].exam_enrollments_encoded\
                    += score_encoding.exam_enrollments_encoded
                group_by_learning_unit[score_encoding.learning_unit_year_id].total_exam_enrollments\
                    += score_encoding.total_exam_enrollments
            except KeyError:
                group_by_learning_unit[score_encoding.learning_unit_year_id] = score_encoding
        scores_encodings = group_by_learning_unit.values()
    else:
        # Filter list by offer_year
        offer_year_id = int(offer_year_id)  # The offer_year_id received in session is a String, not an Int
        scores_encodings = list(mdl.scores_encoding.search(request.user))
        scores_encodings = [score_encoding for score_encoding in scores_encodings
                            if score_encoding.offer_year_id == offer_year_id]

    if tutor_id:
        # Filter list by tutor
        tutor_id = int(tutor_id) # The tutor_id received in session is a String, not an Int
        learning_unit_years = list(mdl.learning_unit_year.find_by_tutor(tutor_id))
        learning_unit_year_ids = set([learn_unit_year.id for learn_unit_year in learning_unit_years])
        scores_encodings = [score_encoding for score_encoding in scores_encodings
                            if score_encoding.learning_unit_year_id in learning_unit_year_ids]

    # Ordering by learning_unit_year.acronym
    scores_encodings = sorted(scores_encodings, key=lambda k: k.learning_unit_year.acronym)

    return layout.render(request, "assessments/scores_encoding_mgr.html",
                         {'notes_list': scores_encodings,
                          'offer_list': offer_years_managed,
                          'tutor_list': all_tutors,
                          'offer_year_id': offer_year_id,
                          'tutor_id': tutor_id,
                          'academic_year': academic_yr})


def refresh_list(request):
    return get_data_pgmer(request,
                          offer_year_id=request.GET.get('offer', None),
                          tutor_id=request.GET.get('tutor', None))


# def order_learning_unit_list_by_acronym(learning_unit_list):
#     list_ids = []
#     for learning_unit_elt in learning_unit_list:
#         list_ids.append(learning_unit_elt.id)
#     if list_ids and len(list_ids) > 0:
#         return mdl.learning_unit.find_by_ids(list_ids).order_by('acronym')
#     return learning_unit_list


def _get_exam_enrollments(user,
                         learning_unit_year_id=None, tutor_id=None, offer_year_id=None,
                         academic_year=mdl.academic_year.current_academic_year()):
    """
    :param user: The user who's asking for exam_enrollments (for scores' encoding).
    :param learning_unit_year_id: To filter ExamEnroll by learning_unit_year.
    :param tutor_id: To filter ExamEnroll by tutor.
    :param offer_year_id: To filter ExamEnroll by OfferYear.
    :param academic_year: The academic year for the data returned.
    :return: All exam enrollments for the user passed in parameter (check if it is a program manager or a tutor) and
             a Boolean is_program_manager (True if the user is a program manager, False if the user is a Tutor/coord).
    """
    is_program_manager = False
    # Case the user is a program manager
    if mdl.program_manager.is_program_manager(user):
        is_program_manager = True
        tutor = None
        if tutor_id:
            tutor = mdl.tutor.find_by_id(tutor_id)
        if offer_year_id:
            # Get examEnrollments for only one offer
            offers_year = [mdl.offer_year.find_by_id(offer_year_id)]
        else:
            # Get examEnrollments for all offers managed by the program manager
            offers_year = list(mdl.offer_year.find_by_user(user, academic_year=academic_year))
        exam_enrollments = list(mdl.exam_enrollment\
                              .find_for_score_encodings(mdl.session_exam.find_session_exam_number(),
                                                        learning_unit_year_id=learning_unit_year_id,
                                                        tutor=tutor,
                                                        offers_year=offers_year))
    else: # Case the user is a tutor
        # Note : The tutor can't filter by offerYear ; the offer_id is always None. Not necessary to check.
        tutor = mdl.tutor.find_by_user(user)
        exam_enrollments = list(mdl.exam_enrollment \
            .find_for_score_encodings(mdl.session_exam.find_session_exam_number(),
                                      learning_unit_year_id=learning_unit_year_id,
                                      tutor=tutor))

    exam_enrollments = sorted(exam_enrollments, key=lambda k: k.learning_unit_enrollment.offer_enrollment.offer_year.acronym
                                                              + k.learning_unit_enrollment.offer_enrollment.student.person.last_name
                                                              + k.learning_unit_enrollment.offer_enrollment.student.person.first_name)
    return exam_enrollments, is_program_manager
