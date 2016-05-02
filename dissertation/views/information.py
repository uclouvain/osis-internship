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
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from pprint import pprint
from dissertation.models.adviser import Adviser
from base import models as mdl
from dissertation.forms import AdviserForm

@login_required
def informations(request):
    person = mdl.person.find_by_user(request.user)
    try:
        p = Adviser(person=person, email_accept=False, phone_accept=False, office_accept=False)
        p.save()
        adviser = Adviser.find_by_person(person)
    except :
        adviser = Adviser.find_by_person(person)
    return render(request, "informations.html", {'person':person,'adviser': adviser})

@login_required
def informations_edit(request):
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    if request.method == "POST":
        form = AdviserForm(request.POST, instance=adviser)
        if form.is_valid():
            adviser = form.save(commit=False)
            adviser.save()
            return redirect('informations')
    else:
        form = AdviserForm(instance=adviser)
    return render(request, "informations_edit.html", {'form':form,'person':person})

@login_required
def manager_informations(request):
    advisers = Adviser.find_all().filter(type='PRF')
    return render(request, 'manager_informations.html', {'advisers': advisers})
