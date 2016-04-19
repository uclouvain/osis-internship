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
from django.contrib.messages import get_messages

from base import models as mdl
from base.utils import send_mail, pdf_utils, export_utils
from . import layout
from base.views.notes import Notes
from base.views.notes import NotesDetail


@login_required
def scores_encoding(request):
    tutor = mdl.attribution.get_assigned_tutor(request.user)
    academic_yr = mdl.academic_year.current_academic_year()
    if tutor:
        data_dict = get_data(request)
        sessions_list, faculties, notes_list = get_sessions(None, request, tutor, academic_yr)
        return layout.render(request, "scores_encoding.html",
                      {'section':            data_dict['section'],
                       'tutor':              tutor,
                       'academic_year':      academic_yr,
                       'notes_list': notes_list})
    # In case the user is not a tutor we check whether it is a program manager for the offer.
    else:
        is_pgmer = False
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        for program_mgr in program_mgr_list:
            is_pgmer = True
            break
        if is_pgmer:
            tutor_sel = None
            offer_sel = None
            tutor_sel_id = request.POST.get('tutor', None)
            if tutor_sel_id:
                tutor_sel = mdl.tutor.find_by_id(tutor_sel_id)
            offer_sel_id = request.POST.get('offer', None)
            if offer_sel_id:
                offer_sel = mdl.offer_year.find_by_id(offer_sel_id)
            data_dict = get_data_pgmer(request,None,None)
            return layout.render(request, "scores_encoding_mgr.html",
                          {'notes_list':    data_dict['notes_list'],
                           'offer_list':    mdl.offer_year.find_by_user(request.user),
                           'tutor_list':    mdl.tutor.find_by_program_manager(request.user),
                           'tutor':         tutor_sel,
                           'offer':         offer_sel,
                           'academic_year': data_dict['academic_year']})


@login_required
def online_encoding(request, learning_unit_id=None, tutor_id=None):
    data_dict = get_data_online(learning_unit_id, tutor_id, request)
    return layout.render(request, "online_encoding.html",data_dict)


@login_required
def online_encoding_form(request, learning_unit_id=None, tutor_id=None):
    data = get_data_online(learning_unit_id, tutor_id, request)
    enrollments = data['enrollments']
    if request.method == 'GET':
        return layout.render(request, "online_encoding_form.html",
                              {'section': 'scores_encoding',
                               'tutor': data['tutor'],
                               'academic_year': data['academic_year'],
                               'enrollments': enrollments,
                               'learning_unit': data['learning_unit'],
                               'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES,
                               'all_encoded': data['all_encoded']})
    elif request.method == 'POST':
        for enrollment in enrollments:
            score = request.POST.get('score_' + str(enrollment.id), None)
            if score:
                if enrollment.session_exam.learning_unit_year.decimal_scores:
                    enrollment.score_draft = float(score)
                else:
                    enrollment.score_draft = int(float(score))
            else:
                enrollment.score_draft = enrollment.score_final
            if request.POST.get('justification_' + str(enrollment.id), None) == "None":
                enrollment.justification_draft = None
            else:
                enrollment.justification_draft = request.POST.get('justification_' + str(enrollment.id), None)
            enrollment.save()
        if tutor_id:
            return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id, tutor_id)))
        else:
            return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id, )))

@login_required
def online_double_encoding_form(request, learning_unit_id=None, tutor_id=None):
    data = get_data_online_double(learning_unit_id, tutor_id, request)
    enrollments = data['enrollments']
    learning_unit = data['learning_unit']
    if request.method == 'GET':
        return layout.render(request, "online_double_encoding_form.html",
                      {'section':        data['section'],
                       'tutor':          data['tutor'],
                       'academic_year':  data['academic_year'],
                       'enrollments':    enrollments,
                       'learning_unit':  learning_unit,
                       'justifications': data['justifications']})
    elif request.method == 'POST':
        for enrollment in enrollments:
            score = request.POST.get('score_' + str(enrollment.id), None)
            if score:
                if enrollment.session_exam.learning_unit_year.decimal_scores:
                    enrollment.score_reencoded = float(score)
                else:
                    enrollment.score_reencoded = int(float(score))
            else:
                enrollment.score_reencoded = None
            if request.POST.get('justification_' + str(enrollment.id), None) == "None":
                justification = None
            else:
                justification = request.POST.get('justification_' + str(enrollment.id), None)
            if justification:
                enrollment.justification_reencoded = justification
            else:
                enrollment.justification_reencoded = None
            enrollment.save()
        if tutor_id:
            return HttpResponseRedirect(reverse('online_double_encoding_validation', args=(learning_unit.id,tutor_id)))
        else:
            return HttpResponseRedirect(reverse('online_double_encoding_validation', args=(learning_unit.id,)))


@login_required
def online_double_encoding_validation(request, learning_unit_id=None, tutor_id=None):

    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)
    if tutor_id:
        tutor = mdl.tutor.find_by_id(tutor_id)
    else:
        tutor = mdl.tutor.find_by_user(request.user)
    academic_year = mdl.academic_year.current_academic_year()
    if request.method == 'GET':
        sessions_list, faculties, notes_list = get_sessions(learning_unit_id, request, tutor,academic_year)
        all_enrollments = []
        if sessions_list:
            for sessions in sessions_list:
                for session in sessions:
                    enrollments = list(mdl.exam_enrollment.find_exam_enrollments_to_validate_by_session(session))
                    if enrollments:
                        all_enrollments = all_enrollments + enrollments

        return layout.render(request, "online_double_encoding_validation.html",
                      {'section':        'scores_encoding',
                       'tutor':          tutor,
                       'academic_year':  academic_year,
                       'learning_unit':  learning_unit,
                       'enrollments':    all_enrollments,
                       'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES})

    elif request.method == 'POST':
        sessions_list, faculties, notes_list = get_sessions(learning_unit_id, request, tutor, academic_year)
        if sessions_list:
            for sessions in sessions_list:

                for session in sessions:
                    enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session(session))
                    if enrollments:

                        for enrollment in enrollments:
                            score = request.POST.get('score_' + str(enrollment.id), None)
                            if score:
                                if enrollment.session_exam.learning_unit_year.decimal_scores:
                                    enrollment.score_final = float(score)
                                else:
                                    enrollment.score_final = int(float(score))
                                enrollment.score_draft = enrollment.score_final
                            enrollment.score_reencoded = None

                            justification = request.POST.get('justification_' + str(enrollment.id), None)
                            if justification:
                                enrollment.justification_final = justification
                                enrollment.justification_draft = enrollment.justification_final
                            if score or justification:
                                mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment, score, justification)
                            enrollment.justification_reencoded = None
                            enrollment.save()

                        all_encoded = True
                        for enrollment in enrollments:
                            if not enrollment.score_final and not enrollment.justification_final:
                                all_encoded = False

                        if all_encoded:
                            session.status = 'CLOSED'
                            session.save()
        if tutor_id:
            return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit.id, tutor_id)))
        else:
            return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit.id,)))


@login_required
def online_encoding_submission(request, learning_unit_id):
    tutor = None
    program_mgr_list = mdl.program_manager.find_by_user(request.user)
    if not program_mgr_list:
        tutor = mdl.tutor.find_by_user(request.user)

    academic_yr = mdl.academic_year.current_academic_year()

    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)

    sessions_list, faculties, notes_list= get_sessions(learning_unit, request, tutor, academic_yr)

    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:
                enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_by_session(session)
                all_encoded = True
                for enrollment in enrollments:
                    if enrollment.score_draft or enrollment.justification_draft:
                        if enrollment.score_draft:
                            enrollment.score_final = enrollment.score_draft
                        if enrollment.justification_draft:
                            enrollment.justification_final = enrollment.justification_draft
                        enrollment.encoding_status = "SUBMITTED"
                        enrollment.save()
                        mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment,
                                                                            enrollment.score_final,
                                                                            enrollment.justification_final)
                    else:
                        all_encoded = False

                if all_encoded:
                    session.status = 'CLOSED'
                    session.save()

    # Send mail to all the teachers of the submitted learning unit on any submission
    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)
    attributions = mdl.attribution.Attribution.objects.filter(learning_unit=learning_unit)
    persons = [attribution.tutor.person for attribution in attributions if attribution.function == 'PROFESSOR']
    send_mail.send_mail_after_scores_submission(persons, learning_unit.acronym)
    if tutor:
        return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id,tutor.id)))
    else:
        return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id,)))


@login_required
def notes_printing(request, session_exam_id, learning_unit_year_id):
    tutor = mdl.tutor.find_by_user(request.user)
    academic_year = mdl.academic_year.current_academic_year()
    session_exam = mdl.session_exam.find_session_by_id(session_exam_id)
    return pdf_utils.print_notes(request, tutor, academic_year, session_exam, learning_unit_year_id)


@login_required
def upload_score_error(request):
    return layout.render(request, "upload_score_error.html", {})


@login_required
def notes_printing(request, learning_unit_id=None, tutor_id=None):
    tutor = None
    if tutor_id:
        tutor = mdl.tutor.find_by_id(tutor_id)

    academic_year = mdl.academic_year.current_academic_year()

    if tutor:
        is_fac = False
    # In case the user is not a tutor we check whether it is a program manager for the offer.
    else:
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        for program_mgr in program_mgr_list:
            is_fac = True
            break
    if learning_unit_id==-1:
        sessions_list, faculties, notes_list = get_sessions(None, request, tutor, academic_year)
    else:
        sessions_list, faculties, notes_list = get_sessions(learning_unit_id, request, tutor, academic_year)

    return pdf_utils.print_notes(request, tutor, academic_year, learning_unit_id, is_fac, sessions_list)


@login_required
def notes_printing_all(request, tutor_id):
    return notes_printing(request, int(-1), tutor_id)


@login_required
def export_xls(request, learning_unit_id, academic_year_id):
    academic_year = mdl.academic_year.current_academic_year()
    tutor = mdl.tutor.find_by_user(request.user)
    if tutor:
        is_fac = False
    # In case the user is not a tutor we check whether it is a program manager for the offer.
    else:
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        for program_mgr in program_mgr_list:
            is_fac = True
            break
    sessions_list, faculties,notes_list = get_sessions(learning_unit_id, request, tutor, academic_year)

    return export_utils.export_xls(request, learning_unit_id, academic_year_id, is_fac, sessions_list)


def get_sessions(learning_unit_param, request, tutor, academic_yr):
    sessions_list = []
    learning_unit_list = []

    faculties = []
    notes_list = []
    if tutor:
        sessions = mdl.session_exam.find_current_sessions_by_tutor(tutor, academic_yr, learning_unit_param)
        sessions_list.append(sessions)
        learning_unit_list = []
        dict_progress = {}
        dict_progress_ok = {}

        for session in sessions:
            learning_unit=session.learning_unit_year.learning_unit
            enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session(session))
            if learning_unit in learning_unit_list:
                dict_progress[learning_unit.acronym] = dict_progress[learning_unit.acronym]+ len(enrollments)
            else:
                dict_progress[learning_unit.acronym]  = len(enrollments)
                learning_unit_list.append(learning_unit)
            value = get_score_encoded(enrollments)
            if learning_unit.acronym in dict_progress_ok:
                dict_progress_ok[learning_unit.acronym] = dict_progress_ok[learning_unit.acronym]+value
            else:
                dict_progress_ok[learning_unit.acronym] = value

        notes = Notes()
        notes.tutor= tutor
        l_lu_detail = []
        notes_list=[]
        for l in learning_unit_list:
            notes_detail = NotesDetail()
            notes_detail.lu = l
            notes_detail.nb_notes_encoded = dict_progress_ok[l.acronym]
            notes_detail.nb_student = dict_progress[l.acronym]
            l_lu_detail.append(notes_detail)
        notes.lu_list = l_lu_detail
        notes_list.append(notes)
    # In case the user is not a tutor we check whether it is a program manager for the offer.
    else:
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        all_enrollments = []
        for program_mgr in program_mgr_list:


            if program_mgr.offer_year:

                notes = Notes()
                sessions = mdl.session_exam.find_sessions_by_offer(program_mgr.offer_year, academic_yr, learning_unit_param)
                sessions_list.append(sessions)
                faculty = program_mgr.offer_year.structure

                notes.structure = faculty
                if faculty not in faculties:
                    faculties.append(faculty)
                learning_unit_list=[]
                dict_progress = {}
                dict_progress_ok = {}
                for session in sessions:
                    learning_unit = session.learning_unit_year.learning_unit
                    enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session_structure(session, session.offer_year_calendar.offer_year.structure))
                    if enrollments:
                        all_enrollments = all_enrollments + enrollments

                    if session.learning_unit_year.learning_unit in learning_unit_list:
                        dict_progress[learning_unit.acronym] = dict_progress[learning_unit.acronym]+ len(enrollments)
                    else:
                        learning_unit=session.learning_unit_year.learning_unit
                        dict_progress[learning_unit.acronym]  = len(enrollments)
                        learning_unit_list.append(learning_unit)
                    value = get_score_encoded(enrollments)
                    if learning_unit.acronym in dict_progress_ok:
                        dict_progress_ok[learning_unit.acronym]=dict_progress_ok[learning_unit.acronym]+value
                    else:
                        dict_progress_ok[learning_unit.acronym]=value
                l_lu_detail = []
                for l in learning_unit_list:
                    notes_detail = NotesDetail()
                    notes_detail.lu = l
                    notes_detail.nb_notes_encoded = dict_progress_ok[l.acronym]
                    notes_detail.nb_student = dict_progress[l.acronym]
                    l_lu_detail.append(notes_detail)
                notes.lu_list = l_lu_detail
                notes_list.append(notes)
        notes = Notes()
        for l in learning_unit_list:
            notes_detail = NotesDetail()
            notes_detail.lu = l
            notes_detail.nb_notes_encoded = dict_progress_ok[l.acronym]
            notes_detail.nb_student = dict_progress[l.acronym]
            l_lu_detail.append(notes_detail)
        notes.lu_list=l_lu_detail
        notes_list = []
        notes_list.append(notes)

    return sessions_list, faculties, notes_list


def get_score_encoded(enrollments):
    progress = 0
    if enrollments:
        for e in enrollments:
            if e.score_final is not None or e.justification_final is not None:
                progress += 1
    return progress


def get_data(request):
    academic_yr = mdl.academic_year.current_academic_year()
    tutor = mdl.tutor.find_by_user(request.user)
    sessions_list, faculties,notes_list = get_sessions(None, request, tutor, academic_yr)

    return {'section': 'scores_encoding',
            'tutor': tutor,
            'academic_year': academic_yr,
            'notes_list': notes_list}


def get_data_online(learning_unit_id, tutor_id, request):
    tutor = None
    program_mgr_list = None
    coordinator = False
    if tutor_id:
        tutor = mdl.tutor.find_by_id(tutor_id)
        coordinator = mdl.attribution.find_by_function(tutor, learning_unit_id, 'COORDINATOR')
    else:
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        if not program_mgr_list:
            tutor = mdl.tutor.find_by_user(request.user)

    academic_yr = mdl.academic_year.current_academic_year()
    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)
    learning_unit_year = mdl.learning_unit_year.find_learning_unit_years_by_academic_year_learningunit(academic_yr,learning_unit)
    sessions_list, faculties, notes_list = get_sessions(learning_unit, request, tutor, academic_yr)

    tot_enrollments=[]
    tot_progress=[]
    tot_num_encoded_scores=0
    all_encoded = True
    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:

                if program_mgr_list:
                    enrollments = mdl.exam_enrollment.find_exam_enrollments_by_session_pgm(session,program_mgr_list)
                else:
                    enrollments = mdl.exam_enrollment.find_exam_enrollments_by_session(session)

                num_encoded_scores = mdl.exam_enrollment.count_encoded_scores(enrollments)
                tot_enrollments.extend(enrollments)
                tot_progress.extend(tot_progress)
                tot_num_encoded_scores = tot_num_encoded_scores+num_encoded_scores
                if session.status == 'OPEN':
                    all_encoded = False

    progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(tot_enrollments)

    return {'section':            'scores_encoding',
            'tutor':              tutor,
            'academic_year':      academic_yr,
            'progress':           "{0:.0f}".format(progress),
            'enrollments':        tot_enrollments,
            'num_encoded_scores': tot_num_encoded_scores,
            'learning_unit':      learning_unit,
            'all_encoded':        all_encoded,
            'learning_unit_year': learning_unit_year,
            'coordinator':        coordinator}


def get_data_online_double(learning_unit_id,tutor_id,request):
    if tutor_id:
        tutor = mdl.tutor.find_by_id(tutor_id)
    else:
        tutor = None
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        if not program_mgr_list:
            tutor = mdl.tutor.find_by_user(request.user)

    academic_yr = mdl.academic_year.current_academic_year()

    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)

    sessions_list, faculties, notes_list = get_sessions(learning_unit, request, tutor, academic_yr)
    tot_enrollments = []
    tot_progress = []
    tot_num_encoded_scores = 0

    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:
                enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_by_session(session)
                num_encoded_scores = mdl.exam_enrollment.count_encoded_scores(enrollments)
                tot_enrollments.extend(enrollments)
                tot_progress.extend(tot_progress)
                tot_num_encoded_scores=tot_num_encoded_scores+num_encoded_scores

    return {'section':'scores_encoding',
            'tutor' : tutor,
            'academic_year': academic_yr,
            'enrollments': tot_enrollments,
            'num_encoded_scores':tot_num_encoded_scores,
            'learning_unit':learning_unit,
            'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES}


def get_data_pgmer(request, tutor_sel, offer_sel):

    academic_yr = mdl.academic_year.current_academic_year()
    faculties = []
    learning_unit_list = []

    program_mgr_list = mdl.program_manager.find_by_user(request.user)
    all_enrollments = []

    dict_progress = {}
    dict_progress_ok = {}

    for program_mgr in program_mgr_list:
        if program_mgr.offer_year:
            if offer_sel or tutor_sel:
                sessions = mdl.session_exam.find_sessions_by_offer_tutor(offer_sel, academic_yr, tutor_sel)
            else:
                sessions = mdl.session_exam.find_sessions_by_offer(program_mgr.offer_year, academic_yr, None)

            faculty = program_mgr.offer_year.structure
            faculties.append(faculty)

            for session in sessions:
                learning_unit = session.learning_unit_year.learning_unit

                enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session_structure(session, session.offer_year_calendar.offer_year.structure))

                if enrollments and len(enrollments) > 0:
                    #print('learning_unit.acronym',learning_unit.acronym)
                    all_enrollments = all_enrollments + enrollments
                    in_list = False
                    for ll in learning_unit_list:
                        if ll.acronym == learning_unit.acronym:
                            in_list = True
                            break
                    if in_list:
                        n = dict_progress.get(learning_unit.acronym)
                        if n is not None:
                            n = n + len(enrollments)
                            dict_progress[learning_unit.acronym] = n
                    else:
                        dict_progress[learning_unit.acronym] = len(enrollments)
                        learning_unit_list.append(learning_unit)
                if enrollments:
                    value = get_score_encoded(enrollments)
                else:
                    value = 0

                if learning_unit.acronym in dict_progress_ok:
                    dict_progress_ok[learning_unit.acronym] = dict_progress_ok.get(learning_unit.acronym)+value
                else:
                    dict_progress_ok[learning_unit.acronym] = value

    notes_list = []
    notes = Notes()
    l_lu_detail = []
    for l in learning_unit_list:
        notes_detail = NotesDetail()
        notes_detail.lu = l
        notes_detail.nb_notes_encoded = dict_progress_ok.get(l.acronym)
        notes_detail.nb_student = dict_progress.get(l.acronym)
        notes_detail.tutor = mdl.tutor.find_responsible(l)
        if notes_detail.tutor:
            l_lu_detail.append(notes_detail)
    notes.lu_list = l_lu_detail

    notes_list.append(notes)
    return {'section':       'scores_encoding',
            'faculties':     faculties,
            'academic_year': academic_yr,
            'notes_list':    notes_list}


def refresh_list(request):
    tutor_sel = None
    offer_sel = None

    tutor_sel_id = request.GET.get('tutor', None)

    if tutor_sel_id:
        if tutor_sel_id != 'all':
            tutor_sel = mdl.tutor.find_by_id(tutor_sel_id)
    offer_sel_id = request.GET.get('offer', None)

    if offer_sel_id:
        if offer_sel_id != 'all':
            offer_sel = mdl.offer_year.find_by_id(offer_sel_id)
    if offer_sel or tutor_sel:
        data_dict = get_data_pgmer_by_offer(tutor_sel, offer_sel)
    else:
        data_dict = get_data_pgmer(request, tutor_sel, offer_sel)

    return layout.render(request, "scores_encoding_mgr.html",
                  {'notes_list':    data_dict['notes_list'],
                   'offer_list':    mdl.offer_year.find_by_user(request.user),
                   'tutor_list':    mdl.tutor.find_by_program_manager(request.user),
                   'tutor':     tutor_sel,
                   'offer':     offer_sel,
                   'academic_year': data_dict['academic_year']})


def get_data_pgmer_by_offer(tutor_sel, offer_sel):
    academic_yr = mdl.academic_year.current_academic_year()

    notes_list = []
    learning_unit_list = []

    all_enrollments = []
    notes = Notes()

    sessions = mdl.session_exam.find_sessions_by_offer_tutor(offer_sel, academic_yr, tutor_sel)

    dict_progress = {}
    dict_progress_ok = {}

    for session in sessions:
        learning_unit = session.learning_unit_year.learning_unit
        enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session_structure(session, session.offer_year_calendar.offer_year.structure))

        if len(enrollments) > 0:
            all_enrollments = all_enrollments + enrollments
            in_list=False
            for ll in learning_unit_list:
                if ll.acronym == learning_unit.acronym:
                    in_list = True
                    break
            if in_list:
                n = dict_progress.get(learning_unit.acronym)
                if n is not None:
                    n = n + len(enrollments)
                    dict_progress[learning_unit.acronym] = n
            else:
                dict_progress[learning_unit.acronym] = len(enrollments)
                learning_unit_list.append(learning_unit)
        if enrollments and len(enrollments) > 0:
            value = get_score_encoded(enrollments)
        else:
            value = 0

        if learning_unit.acronym in dict_progress_ok:
            dict_progress_ok[learning_unit.acronym] = dict_progress_ok.get(learning_unit.acronym)+value
        else:
            dict_progress_ok[learning_unit.acronym] = value
    l_lu_detail = []

    notes.lu_list = l_lu_detail

    notes_list.append(notes)
    notes_list = []
    notes = Notes()
    for l in learning_unit_list:
        notes_detail = NotesDetail()
        notes_detail.lu = l
        notes_detail.nb_notes_encoded = dict_progress_ok.get(l.acronym,0)
        notes_detail.nb_student = dict_progress.get(l.acronym,0)
        notes_detail.tutor = mdl.tutor.find_responsible(l)
        if notes_detail.tutor:
            l_lu_detail.append(notes_detail)
    notes.lu_list = l_lu_detail

    notes_list.append(notes)

    return {'section':       'scores_encoding',
            'academic_year': academic_yr,
            'notes_list':    notes_list}



@login_required
def online_double_encoding_form_pgmer(request, learning_unit_id):
    return online_double_encoding_form_pgmer(request, learning_unit_id, None)


def message_print(request):
    print('message_print')
    return HttpResponseRedirect(reverse('message_print'))

