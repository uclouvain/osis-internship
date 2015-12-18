from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from core.models import Tutor, AcademicYear, AcademicCalendar, SessionExam

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
    academic_year = AcademicCalendar.current_year()
    session = SessionExam.current_session_exam()
    sessions = SessionExam.sessions(tutor, academic_year, session)
    return render(request, "scores_encoding.html",
                  {'section':       'scores_encoding',
                   'tutor':         tutor,
                   'academic_year': academic_year,
                   'session':       session,
                   'sessions':      sessions})
