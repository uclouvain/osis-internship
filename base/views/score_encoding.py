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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from base import models as mdl
from base.utils import send_mail, pdf_utils, export_utils


@login_required
def scores_encoding(request):
    data_dict = get_data(request)
    return render(request, "scores_encoding.html",
                  {'section':            data_dict['section'],
                   'tutor':              data_dict['tutor'],
                   'faculties':          data_dict['faculties'],
                   'academic_year':      data_dict['academic_year'],
                   'sessions_list':      data_dict['sessions_list'],
                   'sessions_offer':     data_dict['sessions_offer'],
                   'learning_unit_list': data_dict['learning_unit_list']})


@login_required
def online_encoding(request, learning_unit_id):
    data_dict = get_data_online(learning_unit_id, request)
    return render(request, "online_encoding.html",
                  {'section':            data_dict['section'],
                   'tutor':              data_dict['tutor'],
                   'academic_year':      data_dict['academic_year'],
                   'progress':           "{0:.0f}".format(data_dict['progress']),
                   'enrollments':        data_dict['enrollments'],
                   'num_encoded_scores': data_dict['num_encoded_scores'],
                   'learning_unit':      data_dict['learning_unit'],
                   'faculties':          data_dict['faculties'],
                   'all_encoded':        data_dict['all_encoded']})


@login_required
def online_encoding_form(request, learning_unit_id):
    data = get_data_online(learning_unit_id, request)
    enrollments = data['enrollments']
    if request.method == 'GET':
        return render(request, "online_encoding_form.html",
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
        return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id,)))


@login_required
def online_double_encoding_form(request, learning_unit_id):
    data = get_data_online_double(learning_unit_id, request)
    enrollments = data['enrollments']
    learning_unit = data['learning_unit']
    if request.method == 'GET':
        return render(request, "online_double_encoding_form.html",
                      {'section': data['section'],
                       'tutor': data['tutor'],
                       'academic_year': data['academic_year'],
                       'enrollments': enrollments,
                       'learning_unit': learning_unit,
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
        return HttpResponseRedirect(reverse('online_double_encoding_validation', args=(learning_unit.id,)))


@login_required
def online_double_encoding_validation(request, learning_unit_id):

    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)
    if request.method == 'GET':
        tutor = mdl.tutor.find_by_user(request.user)
        academic_year = mdl.academic_year.current_academic_year()
        sessions_list, faculties = get_sessions(learning_unit_id, request,tutor,academic_year)
        all_enrollments=[]
        if sessions_list:
            for sessions in sessions_list:
                for session in sessions:
                    print(session.id)
                    enrollments = list(mdl.exam_enrollment.find_exam_enrollments_to_validate_by_session(session))
                    if enrollments:
                        all_enrollments = all_enrollments + enrollments

        return render(request, "online_double_encoding_validation.html",
                      {'section': 'scores_encoding',
                       'tutor': tutor,
                       'academic_year': academic_year,
                       'learning_unit': learning_unit,
                       'enrollments': all_enrollments,
                       'justifications': mdl.exam_enrollment.JUSTIFICATION_TYPES})

    elif request.method == 'POST':
        tutor = mdl.tutor.find_by_user(request.user)
        academic_year = mdl.academic_year.current_academic_year()
        sessions_list, faculties = get_sessions(learning_unit_id, request, tutor, academic_year)
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

        return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit.id,)))


@login_required
def online_encoding_submission(request, learning_unit_id):

    program_mgr_list = mdl.program_manager.find_by_user(request.user)
    if not program_mgr_list:
        tutor = mdl.tutor.find_by_user(request.user)

    academic_yr = mdl.academic_year.current_academic_year()

    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)

    sessions_list, faculties = get_sessions(learning_unit, request,tutor,academic_yr)

    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:
                print('for', session.id)
                enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_by_session(session)
                all_encoded = True
                for enrollment in enrollments:
                    if enrollment.score_draft or enrollment.justification_draft:
                        if enrollment.score_draft:
                            enrollment.score_final = enrollment.score_draft
                        if enrollment.justification_draft:
                            enrollment.justification_final = enrollment.justification_draft
                        enrollment.save()
                        mdl.exam_enrollment.create_exam_enrollment_historic(request.user, enrollment, enrollment.score_final,
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

    return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_id,)))


@login_required
def notes_printing(request, session_exam_id, learning_unit_year_id):
    tutor = mdl.tutor.find_by_user(request.user)
    academic_year = mdl.academic_year.current_academic_year()
    session_exam = mdl.session_exam.find_session_by_id(session_exam_id)
    return pdf_utils.print_notes(request, tutor, academic_year, session_exam, learning_unit_year_id)


@login_required
def upload_score_error(request):
    return render(request, "upload_score_error.html", {})


@login_required
def notes_printing(request, learning_unit_id):
    tutor = mdl.tutor.find_by_user(request.user)
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
    sessions_list, faculties = get_sessions(learning_unit_id, request, tutor, academic_year)

    return pdf_utils.print_notes(request, tutor, academic_year, learning_unit_id,is_fac,sessions_list)


@login_required
def notes_printing_all(request, session_id):
    return notes_printing(request, session_id, -1)


@login_required
def export_xls(request, learning_unit_id,academic_year_id):
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
    sessions_list, faculties = get_sessions(learning_unit_id, request, tutor, academic_year)

    return export_utils.export_xls(request, learning_unit_id,academic_year_id, is_fac, sessions_list)


def get_sessions(learning_unit,request,tutor,academic_yr):
    sessions_list = []
    faculties = []
    if tutor:
        sessions = mdl.session_exam.find_sessions_by_tutor(tutor, academic_yr,learning_unit)
        sessions_list.append(sessions)
    # In case the user is not a tutor we check whether it is a program manager for the offer.
    else:
        program_mgr_list = mdl.program_manager.find_by_user(request.user)
        for program_mgr in program_mgr_list:
            if program_mgr.offer_year:
                sessions = mdl.session_exam.find_sessions_by_offer(program_mgr.offer_year, academic_yr, learning_unit)

                sessions_list.append(sessions)
                faculty = program_mgr.offer_year.structure
                faculties.append(faculty)

        print('fin progm')
    return sessions_list, faculties


def get_data(request):
    academic_yr = mdl.academic_year.current_academic_year()

    tutor = mdl.tutor.find_by_user(request.user)

    learning_unit_list = []
    sessions_list, faculties = get_sessions(None, request, tutor, academic_yr)

    # Calculate the progress of all courses of the tutor.
    all_enrollments = []
    session = None
    sessions_offer =[]

    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:
                enrollments = list(mdl.exam_enrollment.find_exam_enrollments_by_session(session))
                if enrollments:
                    all_enrollments = all_enrollments + enrollments

                if session.learning_unit_year.learning_unit in learning_unit_list:
                    pass
                else:
                    learning_unit_list.append(session.learning_unit_year.learning_unit)

            sessions_offer.append(session)

    url_data = {}
    url_data['section']='scores_encoding'
    url_data['tutor'] = tutor
    url_data['faculties'] = faculties
    url_data['academic_year'] = academic_yr
    url_data['sessions_list'] = sessions_list
    url_data['sessions_offer'] = sessions_offer
    url_data['learning_unit_list'] = learning_unit_list

    print('get_data fin')
    return url_data


def get_data_online(learning_unit_id, request):

    tutor = None
    program_mgr_list = mdl.program_manager.find_by_user(request.user)
    if not program_mgr_list:
        tutor = mdl.tutor.find_by_user(request.user)

    academic_yr = mdl.academic_year.current_academic_year()
    session = None
    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)
    sessions_list, faculties = get_sessions(learning_unit, request,tutor,academic_yr)

    tot_enrollments=[]
    tot_progress=[]
    tot_num_encoded_scores=0
    tot = 0
    all_encoded = True
    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:
                enrollments = mdl.exam_enrollment.find_exam_enrollments_by_session(session)
                tot = tot + len(enrollments)
                num_encoded_scores = mdl.exam_enrollment.count_encoded_scores(enrollments)
                tot_enrollments.extend(enrollments)
                tot_progress.extend(tot_progress)
                tot_num_encoded_scores = tot_num_encoded_scores+num_encoded_scores
                if session.status == 'OPEN':
                    all_encoded = False

    progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(tot_enrollments)

    url_data = {}
    url_data['section']='scores_encoding'
    url_data['tutor'] = tutor
    url_data['academic_year'] = academic_yr
    url_data['session'] = session
    url_data['progress'] = progress
    url_data['enrollments'] = tot_enrollments
    url_data['num_encoded_scores'] = tot_num_encoded_scores
    url_data['learning_unit'] = learning_unit
    url_data['faculties'] = faculties
    url_data['all_encoded'] = all_encoded
    return url_data


def get_data_online_double(learning_unit_id, request):

    tutor = None
    program_mgr_list = mdl.program_manager.find_by_user(request.user)
    if not program_mgr_list:
        tutor = mdl.tutor.find_by_user(request.user)

    academic_yr = mdl.academic_year.current_academic_year()

    learning_unit = mdl.learning_unit.find_learning_unit_by_id(learning_unit_id)

    sessions_list, faculties = get_sessions(learning_unit, request,tutor, academic_yr)
    tot_enrollments = []
    tot_progress = []
    tot_num_encoded_scores = 0
    tot = 0
    if sessions_list:
        for sessions in sessions_list:
            for session in sessions:
                print('for', session.id)
                enrollments = mdl.exam_enrollment.find_exam_enrollments_drafts_by_session(session)
                tot = tot + len(enrollments)
                num_encoded_scores = mdl.exam_enrollment.count_encoded_scores(enrollments)
                tot_enrollments.extend(enrollments)
                tot_progress.extend(tot_progress)
                tot_num_encoded_scores=tot_num_encoded_scores+num_encoded_scores

    url_data = {}
    url_data['section']='scores_encoding'
    url_data['tutor'] = tutor
    url_data['academic_year'] = academic_yr
    url_data['enrollments'] = tot_enrollments
    url_data['num_encoded_scores'] = tot_num_encoded_scores
    url_data['learning_unit'] = learning_unit
    url_data['justifications']= mdl.exam_enrollment.JUSTIFICATION_TYPES

    return url_data