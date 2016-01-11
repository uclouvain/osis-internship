from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Tutor, AcademicCalendar, SessionExam, ExamEnrollment
import os
from . import pdfUtils

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
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session = SessionExam.current_session_exam()
    sessions = SessionExam.sessions(tutor, academic_year, session)
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
def notes_printing(request,session_id):
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicCalendar.current_academic_year()
    session_exam = SessionExam.current_session_exam()
    sessions = SessionExam.sessions(tutor, academic_year, session_exam)
    return pdfUtils.pdf_test(request,tutor,academic_year,session_exam,sessions)
    # return render(request, "scores_encoding.html",
    #               {'section':       'scores_encoding',
    #                'tutor':         tutor,
    #                'academic_year': academic_year,
    #                'session':       session,
    #                'sessions':      sessions})
