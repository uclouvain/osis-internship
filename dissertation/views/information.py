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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation_role import DissertationRole
from base import models as mdl
from dissertation.forms import AdviserForm, ManagerAdviserForm
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError


def is_manager(user):
    person = mdl.person.find_by_user(user)
    adviser = Adviser.find_by_person(person)
    return adviser.type == 'MGR'


@login_required
def informations(request):
    person = mdl.person.find_by_user(request.user)
    try:
        adviser = Adviser(person=person, available_by_email=False, available_by_phone=False, available_at_office=False)
        adviser.save()
    except IntegrityError:
        adviser = Adviser.find_by_person(person)

    count_advisers = DissertationRole.objects.filter(adviser=adviser).count()
    return render(request, "informations.html", {'adviser': adviser, 'count_advisers':count_advisers})


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
    count_advisers = DissertationRole.objects.filter(adviser=adviser).count()
    return render(request, "informations_edit.html", {'form': form, 'person': person, 'count_advisers':count_advisers})


@login_required
@user_passes_test(is_manager)
def manager_informations(request):
    advisers = Adviser.find_all().filter(type='PRF')
    return render(request, 'manager_informations_list.html', {'advisers': advisers})


@login_required
@user_passes_test(is_manager)
def manager_informations_detail(request, pk):
    adviser = get_object_or_404(Adviser, pk=pk)
    count_advisers = DissertationRole.objects.filter(adviser=adviser).count()
    return render(request, 'manager_informations_detail.html', {'adviser': adviser, 'count_advisers':count_advisers})


@login_required
@user_passes_test(is_manager)
def manager_informations_edit(request, pk):
    adviser = get_object_or_404(Adviser, pk=pk)

    if request.method == "POST":
        form = ManagerAdviserForm(request.POST, instance=adviser)
        if form.is_valid():
            adviser = form.save(commit=False)
            adviser.save()
            return redirect('manager_informations')
    else:
        form = AdviserForm(instance=adviser)
    count_advisers = DissertationRole.objects.filter(adviser=adviser).count()
    return render(request, "manager_informations_edit.html", {'adviser': adviser, 'form': form, 'count_advisers':count_advisers})


@login_required
@user_passes_test(is_manager)
def manager_information_search(request):
    advisers = Adviser.search(terms=request.GET['search'])
    return render(request, "manager_informations_list.html", {'advisers': advisers})
