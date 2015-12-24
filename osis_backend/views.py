from django.shortcuts import render

__author__ = 'glamarca'

def page_not_found(request):
    return render(request,'page_not_found.html')

def access_denied(request):
    return render(request,'acces_denied.html')
