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
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.find_session(session_id)
    enrollments = ExamEnrollment.find_exam_enrollments(session)
    progress = ExamEnrollment.calculate_progress(enrollments)

    return render(request, "online_encoding.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
                   'academic_year': academic_year,
                   'session':       session,
                   'progress':      progress,
                   'enrollments':   enrollments})


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
def download_scores_file(request, session_id):
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.find_session(session_id)
    enrollments = ExamEnrollment.find_exam_enrollments(session)
    xls_data = __make_xls_data_from_enrollments(academic_year,session,enrollments)
    sheet = pyexcel.Sheet(xls_data)
    io = StringIO()
    sheet.save_to_memory("xls",io)
    output = pyexcel.make_response(io.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=scores.xls"
    output.headers["Content-type"] = "application/vnd.ms-excel"
    return output


def __make_xls_data_from_enrollments(academic_year,session,enrollments):
    data = [['Année académique','Session','Code Cours','Programme','Section','Noma','Nom','Prénom','Note Chiffrée','Autre Note','Date Remise'],]
    data += map(lambda x : [academic_year,session.number_session,
                            x.learning_unit_enrollment.learning_unit_year.acronym,
                            x.learning_unit_enrollment,
                            x.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
                            '',
                            x.learning_unit_enrollment.offer_enrollment.student.registration_id,
                            x.learning_unit_enrollment.offer_enrollment.student.person.last_name,
                            x.learning_unit_enrollment.offer_enrollment.student.person.first_name,
                            x.score,
                            '',
                            x.session_exam.offer_year_calendar.end_date],enrollments)
    return data


@login_required
def upload_scores_file(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ScoreFileForm(request.POST, request.FILES)
        if form.is_valid():
            __save_xls_scores(request.FILES['file'])
            return HttpResponseRedirect(reverse('score_encoding'))


def __save_xls_scores(file):
    filename = file.filename
    extension = filename.split(".")[1]
    sheet = pyexcel.load_from_memory(extension,file.read())
    records = sheet.get_records()
    for record in records :
        student = Student.objects.get(registration_id=record['Noma'])
        academic_year = AcademicYear.objects.get(year=record['Année académique'][:4])
        offer_year = OfferYear.objects.get(academic_year=academic_year,acronym=record['Programme'])
        offer_enrollment = OfferEnrollment.objects.get(student=student,offer_year=offer_year)
        learning_unit_year = LearningUnitYear.objects.get(academic_year=academic_year,acronym=record['Code cours'])
        learning_unit_enrollment = LearningUnitEnrollment.objects.find(learning_unit_year=learning_unit_year,offer_enrollment=offer_enrollment)
        exam_enrollment = ExamEnrollment.objects.filter(learning_unit_enrollment = learning_unit_enrollment).filter(session_exam__number_session = record['Session']).first()
        exam_enrollment.score = record['Note chiffrée']
        exam_enrollment.save()


def upload_score_error(request):
    print ('upload_score_error')
    return render(request, "upload_score_error.html", {})
