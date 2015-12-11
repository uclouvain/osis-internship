from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

def home(request):
    return render(request, "home.html", {})

@login_required
def assessements(request):
    return render(request, "assessements.html", {'section': 'assessements'})
