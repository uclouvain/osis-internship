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
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from base import models as mdl
from dissertation.models import adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models import faculty_adviser
from dissertation.models.proposition_dissertation import PropositionDissertation, search_proposition_dissertation
from dissertation.models.proposition_role import PropositionRole
from dissertation.forms import PropositionDissertationForm, ManagerPropositionDissertationForm,\
    PropositionRoleForm, ManagerPropositionRoleForm
from django.contrib.auth.decorators import user_passes_test
from base.views import layout


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    adv = adviser.search_by_person(person)
    return adv.type == 'MGR'


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    prop_disserts = PropositionDissertation.objects.filter(Q(active=True) &
                                                           Q(offer_proposition__offer=offer))
    return layout.render(request, 'manager_proposition_dissertations_list.html',
                         {'proposition_dissertations': prop_disserts})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_delete(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    proposition_dissertation.active = False
    proposition_dissertation.save()
    return redirect('manager_proposition_dissertations')


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_detail(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_use = Dissertation.objects.filter(Q(active=True) &
                                            Q(proposition_dissertation=proposition_dissertation)
                                            ).exclude(Q(status='DRAFT')).count()
    percent = count_use * 100 / proposition_dissertation.max_number_student
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=proposition_dissertation).count()
    if count_proposition_role < 1:
        pro = PropositionRole(status='PROMOTEUR', adviser=proposition_dissertation.author,
                              proposition_dissertation=proposition_dissertation)
        pro.save()
    proposition_roles = PropositionRole.objects.filter(proposition_dissertation=proposition_dissertation)
    return layout.render(request, 'manager_proposition_dissertation_detail.html',
                         {'proposition_dissertation': proposition_dissertation,
                          'adviser': adv,
                          'count_use': count_use,
                          'percent': round(percent, 2),
                          'proposition_roles': proposition_roles,
                          'count_proposition_role': count_proposition_role})


@login_required
@user_passes_test(is_manager)
def manage_proposition_dissertation_edit(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    if request.method == "POST":
        form = ManagerPropositionDissertationForm(request.POST, instance=proposition_dissertation)
        if form.is_valid():
            proposition_dissertation = form.save()
            proposition_dissertation.save()
            return redirect('manager_proposition_dissertation_detail', pk=proposition_dissertation.pk)
    else:
        form = ManagerPropositionDissertationForm(instance=proposition_dissertation)
    return layout.render(request, 'manager_proposition_dissertation_edit.html',
                         {'form': form,
                          'types_choices': PropositionDissertation.TYPES_CHOICES,
                          'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                          'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_jury_edit(request, pk):
    proposition_role = get_object_or_404(PropositionRole, pk=pk)
    if request.method == "POST":
        form = ManagerPropositionRoleForm(request.POST, instance=proposition_role)
        if form.is_valid():
            dissertation = form.save()
            dissertation.save()
            return redirect('manager_proposition_dissertation_detail', pk=proposition_role.proposition_dissertation.pk)
    else:
        form = ManagerPropositionRoleForm(instance=proposition_role)
    return layout.render(request, 'manager_proposition_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_jury_new(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=proposition_dissertation).count()
    if count_proposition_role < 5:
        if request.method == "POST":
            form = ManagerPropositionRoleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manager_proposition_dissertation_detail', pk=proposition_dissertation.pk)
        else:
            form = ManagerPropositionRoleForm(initial={'proposition_dissertation': proposition_dissertation})
            return layout.render(request, 'manager_proposition_dissertations_jury_edit.html', {'form': form})
    else:
        return redirect('manager_proposition_dissertation_detail', pk=proposition_dissertation.pk)


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_role_delete(request, pk):
    proposition_role = get_object_or_404(PropositionRole, pk=pk)
    proposition_dissertation = proposition_role.proposition_dissertation
    proposition_role.delete()
    return redirect('manager_proposition_dissertation_detail', pk=proposition_dissertation.pk)


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_new(request):
    if request.method == "POST":
        form = ManagerPropositionDissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_proposition_dissertations')
    else:
        form = ManagerPropositionDissertationForm(initial={'active': True})
    return layout.render(request, 'manager_proposition_dissertation_new.html',
                         {'form': form,
                          'types_choices': PropositionDissertation.TYPES_CHOICES,
                          'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                          'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_search(request):
    prop_disserts = search_proposition_dissertation(terms=request.GET['search']).filter(Q(active=True))
    return layout.render(request, "manager_proposition_dissertations_list.html",
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    prop_disserts = PropositionDissertation.objects.filter((Q(visibility=True) &
                                                                       Q(active=True)) | Q(author=adv))
    return layout.render(request, 'proposition_dissertations_list.html',
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertation_delete(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    proposition_dissertation.active = False
    proposition_dissertation.save()
    return redirect('proposition_dissertations')


@login_required
def proposition_dissertation_detail(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_use = Dissertation.objects.filter(Q(active=True) &
                                            Q(proposition_dissertation=proposition_dissertation)
                                            ).exclude(Q(status='DRAFT')).count()
    percent = count_use * 100 / proposition_dissertation.max_number_student
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=proposition_dissertation).count()
    if count_proposition_role < 1:
        pro = PropositionRole(status='PROMOTEUR', adviser=proposition_dissertation.author,
                              proposition_dissertation=proposition_dissertation)
        pro.save()
    proposition_roles = PropositionRole.objects.filter(proposition_dissertation=proposition_dissertation)
    return layout.render(request, 'proposition_dissertation_detail.html',
                         {'proposition_dissertation': proposition_dissertation,
                          'adviser': adv,
                          'count_use': count_use,
                          'percent': round(percent, 2),
                          'proposition_roles': proposition_roles,
                          'count_proposition_role': count_proposition_role})


@login_required
def proposition_dissertation_edit(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if proposition_dissertation.author == adv:
        if request.method == "POST":
            form = PropositionDissertationForm(request.POST, instance=proposition_dissertation)
            if form.is_valid():
                proposition_dissertation = form.save()
                proposition_dissertation.save()
                return redirect('proposition_dissertation_detail', pk=proposition_dissertation.pk)
        else:
            form = PropositionDissertationForm(instance=proposition_dissertation)
        return layout.render(request, 'proposition_dissertation_edit.html',
                             {'form': form,
                              'types_choices': PropositionDissertation.TYPES_CHOICES,
                              'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                              'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})
    else:
        return layout.render(request, 'proposition_dissertations_list.html',
                             {'proposition_dissertations': proposition_dissertations})


@login_required
def proposition_dissertation_my(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    prop_disserts = PropositionDissertation.objects.filter(Q(author=adv) & Q(active=True))
    return layout.render(request, 'proposition_dissertations_list_my.html',
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertation_new(request):
    if request.method == "POST":
        form = PropositionDissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('proposition_dissertations')
    else:
        person = mdl.person.find_by_user(request.user)
        adv = adviser.search_by_person(person)
        form = PropositionDissertationForm(initial={'author': adv, 'active': True})
    return layout.render(request, 'proposition_dissertation_new.html',
                         {'form': form,
                          'types_choices': PropositionDissertation.TYPES_CHOICES,
                          'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                          'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
def proposition_dissertations_search(request):
    prop_disserts = search_proposition_dissertation(terms=request.GET['search']).filter(
        Q(visibility=True) & Q(active=True))
    return layout.render(request, "proposition_dissertations_list.html",
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertations_jury_edit(request, pk):
    proposition_role = get_object_or_404(PropositionRole, pk=pk)
    if request.method == "POST":
        form = ManagerPropositionRoleForm(request.POST, instance=proposition_role)
        if form.is_valid():
            dissertation = form.save()
            dissertation.save()
            return redirect('proposition_dissertation_detail', pk=proposition_role.proposition_dissertation.pk)
    else:
        form = PropositionRoleForm(instance=proposition_role)
    return layout.render(request, 'proposition_dissertations_jury_edit.html', {'form': form})


@login_required
def proposition_dissertations_jury_new(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=proposition_dissertation).count()
    if count_proposition_role < 5:
        if request.method == "POST":
            form = PropositionRoleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('proposition_dissertation_detail', pk=proposition_dissertation.pk)
        else:
            form = PropositionRoleForm(initial={'proposition_dissertation': proposition_dissertation})
            return layout.render(request, 'proposition_dissertations_jury_edit.html', {'form': form})
    else:
        return redirect('proposition_dissertation_detail', pk=proposition_dissertation.pk)


@login_required
def proposition_dissertations_role_delete(request, pk):
    proposition_role = get_object_or_404(PropositionRole, pk=pk)
    proposition_dissertation = proposition_role.proposition_dissertation
    proposition_role.delete()
    return redirect('proposition_dissertation_detail', pk=proposition_dissertation.pk)
