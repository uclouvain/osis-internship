from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Tutor, AcademicCalendar, SessionExam, ExamEnrollment

def home(request):
    return render(request, "home.html", {})

@login_required
def studies(request):
    return render(request, "studies.html", {'section': 'studies'})

@login_required
def assessements(request):
    return render(request, "assessements.html", {'section': 'assessements'})

@login_required
def scores_encoding(request):
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.current_session_exam()
    sessions = SessionExam.sessions(tutor, academic_year, session)

    # Calculate the progress of all courses of the tutor.
    all_enrollments = []
    for session in sessions:
        enrollments = ExamEnrollment.find_exam_enrollments(session)
        if not all_enrollments:
            all_enrollments = enrollments
        else:
            all_enrollments.append(enrollments)
    progress = ExamEnrollment.calculate_progress(all_enrollments)

    return render(request, "scores_encoding.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
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
                   'justifications':ExamEnrollment.JUSTIFICATION_TYPES})
