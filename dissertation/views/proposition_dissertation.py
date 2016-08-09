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
from base import models as mdl
from dissertation.models import adviser
from dissertation.models import dissertation
from dissertation.models import faculty_adviser
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models import proposition_dissertation
from dissertation.models.proposition_role import PropositionRole
from dissertation.models import proposition_role
from dissertation.forms import PropositionDissertationForm, ManagerPropositionDissertationForm,\
    PropositionRoleForm, ManagerPropositionRoleForm, ManagerPropositionDissertationEditForm
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
from django.contrib.auth.decorators import user_passes_test
from base.views import layout
import time
from django.http import HttpResponse

# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'MGR'

###########################
#      MANAGER VIEWS      #
###########################


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    prop_disserts = proposition_dissertation.search_by_offer(offer)
    return layout.render(request, 'manager_proposition_dissertations_list.html',
                         {'proposition_dissertations': prop_disserts})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_delete(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)
    prop_dissert.deactivate()
    return redirect('manager_proposition_dissertations')


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertation_detail(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_use = dissertation.count_by_proposition(prop_dissert)
    percent = count_use * 100 / prop_dissert.max_number_student
    count_proposition_role = proposition_role.count_by_proposition(prop_dissert)

    if count_proposition_role < 1:
        proposition_role.add('PROMOTEUR', prop_dissert.author, prop_dissert)

    proposition_roles = proposition_role.search_by_proposition(prop_dissert)

    return layout.render(request, 'manager_proposition_dissertation_detail.html',
                         {'proposition_dissertation': prop_dissert,
                          'adviser': adv,
                          'count_use': count_use,
                          'percent': round(percent, 2),
                          'proposition_roles': proposition_roles,
                          'count_proposition_role': count_proposition_role})


@login_required
@user_passes_test(is_manager)
def manage_proposition_dissertation_edit(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)
    if request.method == "POST":
        form = ManagerPropositionDissertationEditForm(request.POST, instance=prop_dissert)
        if form.is_valid():
            prop_dissert = form.save()
            return redirect('manager_proposition_dissertation_detail', pk=prop_dissert.pk)
    else:
        form = ManagerPropositionDissertationEditForm(instance=prop_dissert)
    return layout.render(request, 'manager_proposition_dissertation_edit.html',
                         {'form': form,
                          'author': prop_dissert.author,
                          'types_choices': PropositionDissertation.TYPES_CHOICES,
                          'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                          'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_jury_edit(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)

    if prop_role.proposition_dissertation.author == prop_role.adviser and prop_role.status == 'PROMOTEUR':
        return redirect('manager_proposition_dissertation_detail', pk=prop_role.proposition_dissertation.pk)

    elif request.method == "POST":
        form = ManagerPropositionRoleForm(request.POST, instance=prop_role)
        if form.is_valid():
            form.save()
            return redirect('manager_proposition_dissertation_detail', pk=prop_role.proposition_dissertation.pk)
    else:
        form = ManagerPropositionRoleForm(instance=prop_role)
        return layout.render(request, 'manager_proposition_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_jury_new(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)

    if proposition_role.count_by_proposition(prop_dissert) < 5:
        if request.method == "POST":
            form = ManagerPropositionRoleForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                status = data['status']
                adv = data['adviser']
                prop = data['proposition_dissertation']
                proposition_role.add(status, adv, prop)
                return redirect('manager_proposition_dissertation_detail', pk=prop_dissert.pk)
        else:
            form = ManagerPropositionRoleForm(initial={'proposition_dissertation': prop_dissert})
            return layout.render(request, 'manager_proposition_dissertations_jury_edit.html', {'form': form})
    else:
        return redirect('manager_proposition_dissertation_detail', pk=prop_dissert.pk)


@login_required
@user_passes_test(is_manager)
def manager_proposition_dissertations_role_delete(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)
    prop_dissert = prop_role.proposition_dissertation

    if not (prop_role.proposition_dissertation.author == prop_role.adviser and prop_role.status == 'PROMOTEUR'):
        prop_role.delete()

    return redirect('manager_proposition_dissertation_detail', pk=prop_dissert.pk)


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
    prop_disserts = proposition_dissertation.search(terms=request.GET['search'], active=True)
    if 'bt_xlsx' in request.GET:
        filename = "%s%s%s" % ('EXPORT_dissertation_', time.strftime("%Y-%m-%d %H:%M"), '.xlsx')
        workbook = Workbook(encoding='utf-8')
        worksheet1 = workbook.active
        worksheet1.title = "proposition_dissertation"
        worksheet1.append(['Date_de_création', 'Teatcher', 'Title',
                           'Type', 'Level', 'collaboration', 'max_number_student', 'visibility',
                           'active', 'offer_proposition'])
        for prop_dissert in prop_disserts:
            worksheet1.append([prop_dissert.created_date,
                               str(prop_dissert.author),
                               prop_dissert.title,
                               prop_dissert.type,
                               prop_dissert.level,
                               prop_dissert.collaboration,
                               prop_dissert.max_number_student,
                               prop_dissert.visibility,
                               prop_dissert.active,
                               ''])

        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
        return response

    else:
        return layout.render(request, "manager_proposition_dissertations_list.html",
                         {'proposition_dissertations': prop_disserts})

###########################
#      TEACHER VIEWS      #
###########################


@login_required
def proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    prop_disserts = proposition_dissertation.get_all_for_teacher(adv)
    return layout.render(request, 'proposition_dissertations_list.html',
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertation_delete(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)
    prop_dissert.deactivate()
    return redirect('proposition_dissertations')


@login_required
def proposition_dissertation_detail(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_use = dissertation.count_by_proposition(prop_dissert)
    percent = count_use * 100 / prop_dissert.max_number_student
    count_proposition_role = proposition_role.count_by_proposition(prop_dissert)

    if count_proposition_role < 1:
        proposition_role.add('PROMOTEUR', prop_dissert.author, prop_dissert)

    proposition_roles = proposition_role.search_by_proposition(prop_dissert)

    return layout.render(request, 'proposition_dissertation_detail.html',
                         {'proposition_dissertation': prop_dissert,
                          'adviser': adv,
                          'count_use': count_use,
                          'percent': round(percent, 2),
                          'proposition_roles': proposition_roles,
                          'count_proposition_role': count_proposition_role})


@login_required
def proposition_dissertation_edit(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if prop_dissert.author == adv:
        if request.method == "POST":
            form = PropositionDissertationForm(request.POST, instance=prop_dissert)
            if form.is_valid():
                prop_dissert = form.save()
                return redirect('proposition_dissertation_detail', pk=prop_dissert.pk)
        else:
            form = PropositionDissertationForm(instance=prop_dissert)
        return layout.render(request, 'proposition_dissertation_edit.html',
                             {'form': form,
                              'types_choices': PropositionDissertation.TYPES_CHOICES,
                              'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                              'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES})
    else:
        return layout.render(request, 'proposition_dissertations_list.html',
                             {'proposition_dissertations': proposition_dissertations})


@login_required
def my_dissertation_propositions(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    prop_disserts = proposition_dissertation.get_mine_for_teacher(adv)
    return layout.render(request, 'proposition_dissertations_list_my.html',
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertation_new(request):
    if request.method == "POST":
        form = PropositionDissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('my_dissertation_propositions')
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
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    prop_disserts = proposition_dissertation.search(terms=request.GET['search'],
                                                    active=True, visibility=True, connected_adviser=adv)
    return layout.render(request, "proposition_dissertations_list.html",
                         {'proposition_dissertations': prop_disserts})


@login_required
def proposition_dissertations_jury_edit(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)

    if prop_role.proposition_dissertation.author == prop_role.adviser and prop_role.status == 'PROMOTEUR':
        return redirect('proposition_dissertation_detail', pk=prop_role.proposition_dissertation.pk)

    elif request.method == "POST":
        form = ManagerPropositionRoleForm(request.POST, instance=prop_role)
        if form.is_valid():
            form.save()
            return redirect('proposition_dissertation_detail', pk=prop_role.proposition_dissertation.pk)
    else:
        form = PropositionRoleForm(instance=prop_role)
    return layout.render(request, 'proposition_dissertations_jury_edit.html', {'form': form})


@login_required
def proposition_dissertations_jury_new(request, pk):
    prop_dissert = get_object_or_404(PropositionDissertation, pk=pk)

    if proposition_role.count_by_proposition(prop_dissert) < 5:
        if request.method == "POST":
            form = PropositionRoleForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                status = data['status']
                adv = data['adviser']
                prop = data['proposition_dissertation']
                proposition_role.add(status, adv, prop)
                return redirect('proposition_dissertation_detail', pk=prop_dissert.pk)
        else:
            form = PropositionRoleForm(initial={'proposition_dissertation': prop_dissert})
            return layout.render(request, 'proposition_dissertations_jury_edit.html', {'form': form})
    else:
        return redirect('proposition_dissertation_detail', pk=prop_dissert.pk)


@login_required
def proposition_dissertations_role_delete(request, pk):
    prop_role = get_object_or_404(PropositionRole, pk=pk)
    prop_dissert = prop_role.proposition_dissertation

    if not (prop_role.proposition_dissertation.author == prop_role.adviser and prop_role.status == 'PROMOTEUR'):
        prop_role.delete()

    return redirect('proposition_dissertation_detail', pk=prop_dissert.pk)
