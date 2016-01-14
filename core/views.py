##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
from io import StringIO
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Tutor, AcademicCalendar, SessionExam, ExamEnrollment
from . import pdfUtils
from core.forms import ScoreFileForm
from core.models import Tutor, AcademicCalendar, SessionExam, ExamEnrollment, \
                        ProgrammeManager, Student, AcademicYear, OfferYear, \
                        LearningUnitYear, LearningUnitEnrollment, OfferEnrollment


def page_not_found(request):
    return render(request,'page_not_found.html')


def access_denied(request):
    return render(request,'acces_denied.html')


def home(request):
    return render(request, "home.html")


@login_required
def studies(request):
    return render(request, "studies.html", {'section': 'studies'})


@login_required
def assessements(request):
    return render(request, "assessements.html", {'section': 'assessements'})


@login_required
def scores_encoding(request):
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.current_session_exam()

    tutor = Tutor.find_by_user(request.user)
    # In case the user is a tutor.
    sessions = None
    faculty = None
    if tutor:
        sessions = SessionExam.find_sessions_by_tutor(tutor, academic_year, session)
    # In case the user is not a tutor we check whether it is member of a faculty.
    elif request.user.groups.filter(name='FAC').exists():
        faculty = ProgrammeManager.find_faculty_by_user(request.user)
        if faculty:
            sessions = SessionExam.find_sessions_by_faculty(faculty, academic_year, session)

    # Calculate the progress of all courses of the tutor.
    all_enrollments = []
    for session in sessions:
        enrollments = list(ExamEnrollment.find_exam_enrollments(session))
        if enrollments:
            all_enrollments = all_enrollments + enrollments
    progress = ExamEnrollment.calculate_progress(all_enrollments)

    return render(request, "scores_encoding.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
                   'faculty':       faculty,
                   'academic_year': academic_year,
                   'session':       session,
                   'sessions':      sessions})


@login_required
def online_encoding(request, session_id):
    tutor = None
    faculty = None
    if request.user.groups.filter(name='FAC').exists():
        faculty = ProgrammeManager.find_faculty_by_user(request.user)
    else:
        tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.find_session(session_id)
    enrollments = ExamEnrollment.find_exam_enrollments(session)
    progress = ExamEnrollment.calculate_progress(enrollments)

    return render(request, "online_encoding.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
                   'faculty':       faculty,
                   'academic_year': academic_year,
                   'session':       session,
                   'progress':      "{0:.0f}".format(progress),
                   'enrollments':   enrollments})


@login_required
def notes_printing(request,session_id,learning_unit_year_id):
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session_exam = SessionExam.current_session_exam()
    sessions = SessionExam.find_sessions_by_tutor(tutor, academic_year, session_exam)
    return pdfUtils.print_notes(request,tutor,academic_year,session_exam,sessions,learning_unit_year_id)


@login_required
def online_encoding_form(request, session_id):
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.find_session(session_id)
    enrollments = ExamEnrollment.find_exam_enrollments(session)
    progress = ExamEnrollment.calculate_progress(enrollments)

    return render(request, "online_encoding_form.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
                   'academic_year': academic_year,
                   'session':       session,
                   'progress':      progress,
                   'enrollments':   enrollments,
                   'justifications':ExamEnrollment.JUSTIFICATION_TYPES,
                   'enrollments':   enrollments})

@login_required
def online_double_encoding_form(request, session_id):
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.find_session(session_id)
    enrollments = ExamEnrollment.find_exam_enrollments(session)
    progress = ExamEnrollment.calculate_progress(enrollments)

    return render(request, "online_double_encoding_form.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
                   'academic_year': academic_year,
                   'session':       session,
                   'progress':      progress,
                   'enrollments':   enrollments,
                   'justifications':ExamEnrollment.JUSTIFICATION_TYPES,
                   'enrollments':   enrollments})


@login_required
def upload_score_error(request):
    print ('upload_score_error')
    return render(request, "upload_score_error.html", {})


@login_required
def all_notes_printing(request,session_id):
    return notes_printing(request,session_id,-1)
