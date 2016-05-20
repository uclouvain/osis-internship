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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from base import models as mdl
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.forms import DissertationForm, ManagerDissertationForm, ManagerDissertationRoleForm


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    adviser = Adviser.find_by_person(person)
    return adviser.type == 'MGR'


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_teacher(user):
    person = mdl.person.find_by_user(user)
    adviser = Adviser.find_by_person(person)
    return adviser.type == 'PRF'


################
# VUE GENERALE #
################

@login_required
def dissertations(request):
    # if logged user is not an adviser, create linked adviser
    person = mdl.person.find_by_user(request.user)
    try:
        adviser = Adviser(person=person, available_by_email=False, available_by_phone=False, available_at_office=False)
        adviser.save()
        adviser = Adviser.find_by_person(person)
    except IntegrityError:
        adviser = Adviser.find_by_person(person)
    return render(request, "dissertations.html", {'section': 'dissertations', 'person': person, 'adviser': adviser})


################
# VUES MANAGER #
################

@login_required
@user_passes_test(is_manager)
def manager_dissertations_detail(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    count_dissertation_role = DissertationRole.objects.filter(dissertation=dissertation).count()
    if count_dissertation_role < 1:
        pro = DissertationRole(status='Pro', adviser=dissertation.proposition_dissertation.author, dissertation=dissertation)
        pro.save()
    dissertation_roles = DissertationRole.objects.filter(dissertation=dissertation)
    return render(request, 'manager_dissertations_detail.html',
                  {'dissertation': dissertation, 'adviser': adviser, "dissertation_roles":dissertation_roles})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_edit(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    if request.method == "POST":
        form = ManagerDissertationForm(request.POST, instance=dissertation)
        if form.is_valid():
            dissertation = form.save()
            dissertation.save()
            return redirect('manager_dissertations_detail', pk=dissertation.pk)
    else:
        form = ManagerDissertationForm(instance=dissertation)
    return render(request, 'manager_dissertations_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_jury_new(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    if request.method == "POST":
        form = ManagerDissertationRoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_dissertations_detail', pk=dissertation.pk)
    else:
        form = ManagerDissertationRoleForm(initial={'dissertation': dissertation})

    return render(request, 'manager_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_list(request):
    dissertations = Dissertation.objects.filter(Q(active=True))
    return render(request, 'manager_dissertations_list.html',
                  {'dissertations': dissertations})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_new(request):
    if request.method == "POST":
        form = ManagerDissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_dissertations_list')
    else:
        form = ManagerDissertationForm(initial={'active': True})
        form.fields["proposition_dissertation"].queryset = PropositionDissertation.objects.filter(visibility=True,
                                                                                                  active=True)
    return render(request, 'manager_dissertations_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_search(request):
    dissertations = Dissertation.search(terms=request.GET['search']).filter(Q(active=True))
    return render(request, "manager_dissertations_list.html",
                  {'dissertations': dissertations})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_delete(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.active = False
    dissertation.save()
    return redirect('manager_dissertations_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_submit(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.status = 'DIR_SUBMIT'
    dissertation.save()
    return redirect('manager_dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ok(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.status = 'DIR_OK'
    dissertation.save()
    return redirect('manager_dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ko(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.status = 'DIR_KO'
    dissertation.save()
    return redirect('manager_dissertations_detail', pk=pk)


################
# VUES TEACHER #
################

@login_required
@user_passes_test(is_teacher)
def dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    dissertations = Dissertation.objects.filter(Q(proposition_dissertation__author=adviser) & Q(active=True))
    return render(request, 'dissertations_list.html',
                  {'dissertations': dissertations})


@login_required
@user_passes_test(is_teacher)
def dissertations_new(request):
    if request.method == "POST":
        form = DissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dissertations_list')
    else:
        form = DissertationForm(initial={'active': True})
        form.fields["proposition_dissertation"].queryset = PropositionDissertation.objects.filter(visibility=True,
                                                                                                  active=True)
    return render(request, 'dissertations_edit.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    dissertations = Dissertation.search(terms=request.GET['search']).filter(Q(proposition_dissertation__author=adviser) & Q(active=True))
    return render(request, "dissertations_list.html",
                  {'dissertations': dissertations})


@login_required
@user_passes_test(is_teacher)
def dissertations_detail(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    return render(request, 'dissertations_detail.html',
                  {'dissertation': dissertation, 'adviser': adviser})


@login_required
@user_passes_test(is_teacher)
def dissertations_edit(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    if request.method == "POST":
        form = DissertationForm(request.POST, instance=dissertation)
        if form.is_valid():
            dissertation = form.save()
            dissertation.save()
            return redirect('dissertations_detail', pk=dissertation.pk)
    else:
        form = DissertationForm(instance=dissertation)
    return render(request, 'dissertations_edit.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def dissertations_delete(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.active = False
    dissertation.save()
    return redirect('dissertations_list')


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_submit(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.status = 'DIR_SUBMIT'
    dissertation.save()
    return redirect('dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ok(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.status = 'DIR_OK'
    dissertation.save()
    return redirect('dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ko(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    dissertation.status = 'DIR_KO'
    dissertation.save()
    return redirect('dissertations_detail', pk=pk)
