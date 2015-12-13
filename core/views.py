from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from core.models import Tutor, AcademicYear, SessionExam

def home(request):
    return render(request, "home.html", {})

@login_required
def studies(request):
    return render(request, "studies.html", {})

@login_required
def assessements(request):
    return render(request, "assessements.html", {})

@login_required
def scores_encoding(request):
    tutor = Tutor.find_by_user(request.user)
    academic_year = AcademicYear.current_year()
    upcomming_session = SessionExam.upcomming_session()
    sessions = SessionExam.sessions()
    return render(request, "scores_encoding.html",
                  {'section': 'assessements',
                   'tutor': tutor,
                   'academic_year': academic_year,
                   'session': upcomming_session,
                   'sessions': sessions})
