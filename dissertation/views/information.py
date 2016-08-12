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
from dissertation.models.adviser import Adviser, search_adviser
from dissertation.models import adviser
from dissertation.models import dissertation_role
from dissertation.models import faculty_adviser
from base import models as mdl
from dissertation.forms import AdviserForm, ManagerAdviserForm, ManagerAddAdviserForm
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from base.views import layout


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'MGR'


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_teacher(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'PRF'

###########################
#      TEACHER VIEWS      #
###########################


@login_required
@user_passes_test(is_teacher)
def informations(request):
    person = mdl.person.find_by_user(request.user)
    try:
        adv = Adviser(person=person, available_by_email=False, available_by_phone=False, available_at_office=False)
        adv.save()
        adv = adviser.search_by_person(person)
    except IntegrityError:
        adv = adviser.search_by_person(person)

    return layout.render(request, "informations.html", {'adviser': adv,
                                                        'first_name': adv.person.first_name.title(),
                                                        'last_name': adv.person.last_name.title()
                                                        })


@login_required
@user_passes_test(is_teacher)
def informations_detail_stats(request):
    person = mdl.person.find_by_user(request.user)
    try:
        adv = Adviser(person=person, available_by_email=False, available_by_phone=False, available_at_office=False)
        adv.save()
        adv = adviser.search_by_person(person)
    except IntegrityError:
        adv = adviser.search_by_person(person)

    advisers_pro = dissertation_role.search_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro = dissertation_role.count_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')
    tab_offer_count_pro = dissertation_role.get_tab_count_role_by_offer(advisers_pro)

    advisers_copro = dissertation_role.search_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    count_advisers_copro = dissertation_role.count_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    tab_offer_count_copro = dissertation_role.get_tab_count_role_by_offer(advisers_copro)

    advisers_reader = dissertation_role.search_by_adviser_and_role_stats(adv, 'READER')
    count_advisers_reader = dissertation_role.count_by_adviser_and_role_stats(adv, 'READER')
    tab_offer_count_read = dissertation_role.get_tab_count_role_by_offer(advisers_reader)

    return layout.render(request, 'informations_detail_stats.html',
                         {'adviser': adv,
                          'count_advisers_copro': count_advisers_copro,
                          'count_advisers_pro': count_advisers_pro,
                          'count_advisers_reader': count_advisers_reader,
                          'count_advisers_pro_request': count_advisers_pro_request,
                          'tab_offer_count_pro': tab_offer_count_pro,
                          'tab_offer_count_read': tab_offer_count_read,
                          'tab_offer_count_copro': tab_offer_count_copro})


@login_required
@user_passes_test(is_teacher)
def informations_edit(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if request.method == "POST":
        form = AdviserForm(request.POST, instance=adv)
        if form.is_valid():
            adv = form.save(commit=False)
            adv.save()
            return redirect('informations')
    else:
        form = AdviserForm(instance=adv)
    return layout.render(request, "informations_edit.html", {'form': form,
                                                             'first_name': person.first_name.title(),
                                                             'last_name': person.last_name.title(),
                                                             'email': person.email,
                                                             'phone': person.phone,
                                                             'phone_mobile': person.phone_mobile})

###########################
#      MANAGER VIEWS      #
###########################


@login_required
@user_passes_test(is_manager)
def manager_informations(request):
    advisers = adviser.list_teachers()
    return layout.render(request, 'manager_informations_list.html', {'advisers': advisers})


@login_required
@user_passes_test(is_manager)
def manager_informations_add(request):
    if request.method == "POST":
        form = ManagerAddAdviserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_informations')
    else:
        form = ManagerAddAdviserForm(initial={'type': "PRF"})
    return layout.render(request, 'manager_informations_add.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_informations_detail(request, pk):
    adv = get_object_or_404(Adviser, pk=pk)
    return layout.render(request, 'manager_informations_detail.html',
                         {'adviser': adv,
                          'first_name': adv.person.first_name.title(),
                          'last_name': adv.person.last_name.title()})


@login_required
@user_passes_test(is_manager)
def manager_informations_edit(request, pk):
    adv = get_object_or_404(Adviser, pk=pk)
    if request.method == "POST":
        form = ManagerAdviserForm(request.POST, instance=adv)
        if form.is_valid():
            adv = form.save(commit=False)
            adv.save()
            return redirect('manager_informations_detail', pk=adv.pk)
    else:
        form = ManagerAdviserForm(instance=adv)
    return layout.render(request, "manager_informations_edit.html",
                         {'form': form,
                          'first_name': adv.person.first_name.title(),
                          'last_name': adv.person.last_name.title(),
                          'email': adv.person.email,
                          'phone': adv.person.phone,
                          'phone_mobile': adv.person.phone_mobile})


@login_required
@user_passes_test(is_manager)
def manager_informations_search(request):
    advisers = search_adviser(terms=request.GET['search'])
    return layout.render(request, "manager_informations_list.html", {'advisers': advisers})


@login_required
@user_passes_test(is_manager)
def manager_informations_list_request(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    advisers_need_request = dissertation_role.list_teachers_action_needed(offer)

    return layout.render(request, "manager_informations_list_request.html",
                         {'advisers_need_request': advisers_need_request})


@login_required
@user_passes_test(is_manager)
def manager_informations_detail_list(request, pk):
    person = mdl.person.find_by_user(request.user)
    connected_adviser = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(connected_adviser).offer
    adv = get_object_or_404(Adviser, pk=pk)

    adv_list_disserts_pro = dissertation_role.search_by_adviser_and_role_and_offer(adv, 'PROMOTEUR', offer)
    adv_list_disserts_copro = dissertation_role.search_by_adviser_and_role_and_offer(adv, 'CO_PROMOTEUR', offer)
    adv_list_disserts_reader = dissertation_role.search_by_adviser_and_role_and_offer(adv, 'READER', offer)

    return layout.render(request, "manager_informations_detail_list.html",
                         {'adviser': adv,
                          'adviser_list_dissertations': adv_list_disserts_pro,
                          'adviser_list_dissertations_copro': adv_list_disserts_copro,
                          'adviser_list_dissertations_reader': adv_list_disserts_reader})

@login_required
@user_passes_test(is_manager)
def manager_informations_detail_list_wait(request, pk):
    person = mdl.person.find_by_user(request.user)
    connected_adviser = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(connected_adviser).offer
    adv = get_object_or_404(Adviser, pk=pk)
    disserts_role=dissertation_role.search_by_adviser_and_role_and_waiting(adv, offer)

    return layout.render(request, "manager_informations_detail_list_wait.html",
                         {'disserts_role': disserts_role,'adviser':adv})


@login_required
@user_passes_test(is_manager)
def manager_informations_detail_stats(request, pk):
    adv = get_object_or_404(Adviser, pk=pk)

    advisers_pro = dissertation_role.search_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro = dissertation_role.count_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')
    tab_offer_count_pro = dissertation_role.get_tab_count_role_by_offer(advisers_pro)

    advisers_copro = dissertation_role.search_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    count_advisers_copro = dissertation_role.count_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    tab_offer_count_copro = dissertation_role.get_tab_count_role_by_offer(advisers_copro)

    advisers_reader = dissertation_role.search_by_adviser_and_role_stats(adv, 'READER')
    count_advisers_reader = dissertation_role.count_by_adviser_and_role_stats(adv, 'READER')
    tab_offer_count_read = dissertation_role.get_tab_count_role_by_offer(advisers_reader)

    return layout.render(request, 'manager_informations_detail_stats.html',
                         {'adviser': adv,
                          'count_advisers_copro': count_advisers_copro,
                          'count_advisers_pro': count_advisers_pro,
                          'count_advisers_reader': count_advisers_reader,
                          'count_advisers_pro_request': count_advisers_pro_request,
                          'tab_offer_count_pro': tab_offer_count_pro,
                          'tab_offer_count_read': tab_offer_count_read,
                          'tab_offer_count_copro': tab_offer_count_copro})
