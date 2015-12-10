from django.shortcuts import render

def home(request):
    return render(request, "home.html", {})


def assessements(request):
    return render(request, "assessements.html", {})
