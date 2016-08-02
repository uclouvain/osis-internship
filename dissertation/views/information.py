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
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models import dissertation_role
from dissertation.models import faculty_adviser
from base import models as mdl
from dissertation.forms import AdviserForm, ManagerAdviserForm, ManagerAddAdviserForm
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from base.views import layout


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    adv = adviser.search_by_person(person)
    return adv.type == 'MGR'


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_teacher(user):
    person = mdl.person.find_by_user(user)
    adv = adviser.search_by_person(person)
    return adv.type == 'PRF'

##########################
#      VUES TEACHER      #
##########################


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
    tab_offer_count_pro = {}
    for dissertaion_role_pro in advisers_pro:
        if dissertaion_role_pro.dissertation.offer_year_start.offer.title in tab_offer_count_pro:
            tab_offer_count_pro[dissertaion_role_pro.dissertation.offer_year_start.offer.title] = \
                tab_offer_count_pro[str(dissertaion_role_pro.dissertation.offer_year_start.offer.title)] + 1
        else:
            tab_offer_count_pro[dissertaion_role_pro.dissertation.offer_year_start.offer.title] = 1

    advisers_copro = dissertation_role.search_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    count_advisers_copro = dissertation_role.count_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    tab_offer_count_copro = {}
    for dissertaion_role_copro in advisers_copro:
        if dissertaion_role_copro.dissertation.offer_year_start.offer.title in tab_offer_count_copro:
            tab_offer_count_copro[dissertaion_role_copro.dissertation.offer_year_start.offer.title] = \
                tab_offer_count_copro[str(dissertaion_role_copro.dissertation.offer_year_start.offer.title)] + 1
        else:
            tab_offer_count_copro[dissertaion_role_copro.dissertation.offer_year_start.offer.title] = 1

    advisers_reader = dissertation_role.search_by_adviser_and_role_stats(adv, 'READER')
    count_advisers_reader = dissertation_role.count_by_adviser_and_role_stats(adv, 'READER')
    tab_offer_count_read = {}
    for dissertaion_role_read in advisers_reader:
        if dissertaion_role_read.dissertation.offer_year_start.offer.title in tab_offer_count_read:
            tab_offer_count_read[dissertaion_role_read.dissertation.offer_year_start.offer.title] = \
                tab_offer_count_read[str(dissertaion_role_read.dissertation.offer_year_start.offer.title)] + 1
        else:
            tab_offer_count_read[dissertaion_role_read.dissertation.offer_year_start.offer.title] = 1

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

##########################
#      VUES MANAGER      #
##########################


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
    adviser_co = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adviser_co).offer
    adv = get_object_or_404(Adviser, pk=pk)
    queryset = DissertationRole.objects.all()
    adviser_list_dissertations = queryset.filter(Q(status='PROMOTEUR') &
                                                 Q(adviser__pk=pk) &
                                                 Q(dissertation__offer_year_start__offer=offer) &
                                                 Q(dissertation__active=True)).exclude(
                                                        Q(dissertation__status='DRAFT'))
    adviser_list_dissertations = adviser_list_dissertations.order_by('dissertation__status')

    adviser_list_dissertations_copro = queryset.filter(Q(status='CO_PROMOTEUR') &
                                                       Q(adviser__pk=pk) &
                                                       Q(dissertation__offer_year_start__offer=offer) &
                                                       Q(dissertation__active=True)).exclude(
                                                        Q(dissertation__status='DRAFT'))
    adviser_list_dissertations_copro = adviser_list_dissertations_copro.order_by('dissertation__status')

    adviser_list_dissertations_reader = queryset.filter(Q(status='READER') &
                                                        Q(adviser__pk=pk) &
                                                        Q(dissertation__offer_year_start__offer=offer) &
                                                        Q(dissertation__active=True)).exclude(
                                                        Q(dissertation__status='DRAFT'))
    adviser_list_dissertations_reader = adviser_list_dissertations_reader.order_by('dissertation__status')

    return layout.render(request, "manager_informations_detail_list.html",
                         {'adviser': adv,
                          'adviser_list_dissertations': adviser_list_dissertations,
                          'adviser_list_dissertations_copro': adviser_list_dissertations_copro,
                          'adviser_list_dissertations_reader': adviser_list_dissertations_reader})


@login_required
@user_passes_test(is_manager)
def manager_informations_detail_stats(request, pk):
    adv = get_object_or_404(Adviser, pk=pk)
    queryset = DissertationRole.objects.all()
    count_advisers = queryset.filter(Q(adviser=adv) & Q(dissertation__active=True)).count()
    count_advisers_pro = queryset.filter(
        Q(adviser=adv) & Q(status='PROMOTEUR') &
        Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                              Q(dissertation__status='ENDED') |
                                              Q(dissertation__status='DEFENDED')).count()

    count_advisers_pro_request = queryset.filter(
        Q(adviser=adv) & Q(status='PROMOTEUR') &
        Q(dissertation__status='DIR_SUBMIT') & Q(dissertation__active=True)).count()

    advisers_copro = queryset.filter(
        Q(adviser=adv) & Q(status='CO_PROMOTEUR') &
        Q(dissertation__active=True)).exclude(
        Q(dissertation__status='DRAFT') | Q(dissertation__status='ENDED') |
        Q(dissertation__status='DEFENDED'))
    count_advisers_copro = advisers_copro.count()
    tab_offer_count_copro = {}
    # iterates dissertation_role where adviser is co_promo exluding DRAFT-ENDED-DEFENDED dissertations
    for dissertaion_role_copro in advisers_copro:
        if dissertaion_role_copro.dissertation.offer_year_start.offer.title in tab_offer_count_copro:
            tab_offer_count_copro[dissertaion_role_copro.dissertation.offer_year_start.offer.title] = \
                tab_offer_count_copro[str(dissertaion_role_copro.dissertation.offer_year_start.offer.title)] + 1
        else:
            tab_offer_count_copro[dissertaion_role_copro.dissertation.offer_year_start.offer.title] = 1
    advisers_reader = queryset.filter(Q(adviser=adv) &
                                      Q(status='READER') &
                                      Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                                                            Q(dissertation__status='ENDED') |
                                                                            Q(dissertation__status='DEFENDED'))
    count_advisers_reader = advisers_reader.count()
    tab_offer_count_read = {}
    for dissertaion_role_read in advisers_reader:
        if dissertaion_role_read.dissertation.offer_year_start.offer.title in tab_offer_count_read:
            tab_offer_count_read[dissertaion_role_read.dissertation.offer_year_start.offer.title] = \
                tab_offer_count_read[str(dissertaion_role_read.dissertation.offer_year_start.offer.title)] + 1
        else:
            tab_offer_count_read[dissertaion_role_read.dissertation.offer_year_start.offer.title] = 1
    advisers_pro = queryset.filter(Q(adviser=adv) &
                                   Q(status='PROMOTEUR') &
                                   Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                                                         Q(dissertation__status='ENDED') |
                                                                         Q(dissertation__status='DEFENDED'))
    tab_offer_count_pro = {}
    for dissertaion_role_pro in advisers_pro:
        if dissertaion_role_pro.dissertation.offer_year_start.offer.title in tab_offer_count_pro:
            tab_offer_count_pro[dissertaion_role_pro.dissertation.offer_year_start.offer.title] = \
                tab_offer_count_pro[str(dissertaion_role_pro.dissertation.offer_year_start.offer.title)] + 1
        else:
            tab_offer_count_pro[dissertaion_role_pro.dissertation.offer_year_start.offer.title] = 1
    return layout.render(request, 'manager_informations_detail_stats.html',
                         {'adviser': adv,
                          'count_advisers': count_advisers,
                          'count_advisers_copro': count_advisers_copro,
                          'count_advisers_pro': count_advisers_pro,
                          'count_advisers_reader': count_advisers_reader,
                          'count_advisers_pro_request': count_advisers_pro_request,
                          'tab_offer_count_pro': tab_offer_count_pro,
                          'tab_offer_count_read': tab_offer_count_read,
                          'tab_offer_count_copro': tab_offer_count_copro})
