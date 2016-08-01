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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from base import models as mdl
from base.models.offer_year import OfferYear
from base.models.student import Student
from base.views import layout
from dissertation.models.adviser import Adviser
from dissertation.models import adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models import dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models import dissertation_role
from dissertation.models.dissertation_update import DissertationUpdate
from dissertation.models import faculty_adviser
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models import offer_proposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models import proposition_dissertation
from dissertation.models.proposition_role import PropositionRole
from dissertation.models import proposition_role
from dissertation.models import dissertation_update
from dissertation.forms import ManagerDissertationForm, ManagerDissertationEditForm, ManagerDissertationRoleForm
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
from django.http import HttpResponse
import time


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


# Used to insert update log
def insert_update(request, dissertation, old_status):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    update = DissertationUpdate()
    update.status_from = old_status
    update.status_to = dissertation.status
    update.justification = adv.type + "_set_to_" + dissertation.status
    update.person = person
    update.dissertation = dissertation
    update.save()

##########################
#      VUE GENERALE      #
##########################


@login_required
def dissertations(request):
    # if logged user is not an adviser, create linked adviser
    person = mdl.person.find_by_user(request.user)
    try:
        adv = Adviser(person=person, available_by_email=False, available_by_phone=False, available_at_office=False)
        adv.save()
        adv = adviser.search_by_person(person)
    except IntegrityError:
        adv = adviser.search_by_person(person)

    count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')

    return layout.render(request, "dissertations.html",
                         {'section': 'dissertations',
                          'person': person,
                          'adviser': adv,
                          'count_advisers_pro_request': count_advisers_pro_request})


##########################
#      VUES MANAGER      #
##########################

@login_required
@user_passes_test(is_manager)
def manager_dissertations_detail(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissertation)
    count_proposition_role = proposition_role.count_by_dissertation(dissertation)
    proposition_roles = proposition_role.search_by_dissertation(dissertation)

    if count_proposition_role == 0:
        if count_dissertation_role == 0:
            dissertation_role.add('PROMOTEUR', dissertation.proposition_dissertation.author, dissertation)
    else:
        if count_dissertation_role == 0:
            for role in proposition_roles:
                dissertation_role.add(role.status, role.adviser, dissertation)

    dissertation_roles = dissertation_role.search_by_dissertation(dissertation)
    return layout.render(request, 'manager_dissertations_detail.html',
                         {'dissertation': dissertation,
                          'adviser': adv,
                          'dissertation_roles': dissertation_roles,
                          'count_dissertation_role': count_dissertation_role})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_detail_updates(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    dissertation_updates = dissertation_update.search_by_dissertation(dissertation)

    return layout.render(request, 'manager_dissertations_detail_updates.html',
                         {'dissertation': dissertation,
                          'adviser': adv,
                          'dissertation_updates': dissertation_updates})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_edit(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer

    if request.method == "POST":
        form = ManagerDissertationEditForm(request.POST, instance=dissertation)
        if form.is_valid():
            dissertation = form.save()
            dissertation.save()
            return redirect('manager_dissertations_detail', pk=dissertation.pk)
        else:
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offer)
            form.fields["author"].queryset = mdl.student.find_by_offer(offer)
            form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offer)
    else:
        form = ManagerDissertationEditForm(instance=dissertation)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offer)
        form.fields["author"].queryset = mdl.student.find_by_offer(offer)
        form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offer)

    return layout.render(request, 'manager_dissertations_edit.html',
                         {'form': form, 'defend_periode_choices': Dissertation.DEFEND_PERIODE_CHOICES})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_jury_edit(request, pk):
    dissert_role = get_object_or_404(DissertationRole, pk=pk)
    if request.method == "POST":
        form = ManagerDissertationRoleForm(request.POST, instance=dissert_role)
        if form.is_valid():
            dissertation = form.save()
            dissertation.save()
            return redirect('manager_dissertations_detail', pk=dissert_role.dissertation.pk)
    else:
        form = ManagerDissertationRoleForm(instance=dissert_role)
    return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_jury_new(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissertation)
    if count_dissertation_role < 5:
        if request.method == "POST":
            form = ManagerDissertationRoleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manager_dissertations_detail', pk=dissertation.pk)
        else:
            form = ManagerDissertationRoleForm(initial={'dissertation': dissertation})
            return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form})
    else:
        return redirect('manager_dissertations_detail', pk=dissertation.pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    disserts = dissertation.search_by_offer(offer)
    offer_prop = offer_proposition.search_by_offer(offer)
    return layout.render(request, 'manager_dissertations_list.html', {'dissertations': disserts,
                                                                      'offer_proposition': offer_prop})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_print(request):
    disserts = dissertation.search(terms=request.GET['search'], active=True)
    wb = Workbook(encoding='utf-8')
    dest_filename = 'IMPORT_dissertaion_.xlsx'
    ws1 = wb.active
    ws1.title = "dissertation"
    for dissert in disserts:
        queryset = DissertationRole.objects.filter(Q(dissertation=dissert))
        queryset_pro = queryset.object.filter(Q(status='PROMOTEUR'))
        queryset_copro = queryset.object.filter(Q(status='CO_PROMOTEUR'))
        queryset_reader = queryset.object.filter(Q(status='READER'))
        ws1.append([dissert.creation_date, dissert.author.student.person.first_name,
                    dissert.author.student.person.middle_name, dissert.author.student.person.last_name,
                    dissert.author.student.person.global_id, dissert.title,
                    dissert.status, dissert.offer_year_start, queryset_pro.adviser, queryset_copro.adviser,
                    queryset_reader[0].adviser, queryset_reader[1].adviser])
    response = HttpResponse(save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
    return response


@login_required
@user_passes_test(is_manager)
def manager_dissertations_new(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    if request.method == "POST":
        form = ManagerDissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_dissertations_list')
        else:
            form.fields["proposition_dissertation"].queryset = \
                PropositionDissertation.objects.filter(visibility=True,
                                                       active=True,
                                                       offer_proposition__offer=offer)
            form.fields["author"].queryset = \
                Student.objects.filter(offerenrollment__offer_year__offer=offer)
            form.fields["offer_year_start"].queryset = \
                OfferYear.objects.filter(offer=offer)

    else:
        form = ManagerDissertationForm(initial={'active': True})
        form.fields["proposition_dissertation"].queryset = \
            PropositionDissertation.objects.filter(visibility=True,
                                                   active=True,
                                                   offer_proposition__offer=offer)
        form.fields["author"].queryset = \
            Student.objects.filter(offerenrollment__offer_year__offer=offer)
        form.fields["offer_year_start"].queryset = \
            OfferYear.objects.filter(offer=offer)
    return layout.render(request, 'manager_dissertations_new.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_search(request):
    disserts = dissertation.search(terms=request.GET['search'], active=True)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    offer_proposition = OfferProposition.objects.get(offer=offer)
    xlsx = False
    reader1_name = ''
    reader2_name = ''
    copro_name = ''
    pro_name = ''

    if 'bt_xlsx' in request.GET:

        filename = 'IMPORT_dissertation_' + time.strftime("%Y-%m-%d %H:%M") + '.xlsx'
        wb = Workbook(encoding='utf-8')
        ws1 = wb.active
        ws1.title = "dissertation"
        ws1.append(['Date_de_création', 'Students', 'Dissertation_title',
                    'Status', 'Offer_year_start', 'offer_year_start_short', 'promoteur', 'copromoteur', 'lecteur1',
                    'lecteur2'])
        for dissert in disserts:
            queryset = DissertationRole.objects.filter(Q(dissertation=dissert))
            queryset_pro = queryset.filter(Q(status='PROMOTEUR'))
            queryset_copro = queryset.filter(Q(status='CO_PROMOTEUR'))
            queryset_reader = queryset.filter(Q(status='READER'))

            if queryset_pro.count() > 0:
                pro_name = str(queryset_pro[0].adviser)
            else:
                pro_name = 'none'

            if queryset_copro.count() > 0:
                copro_name = str(queryset_copro[0].adviser)
            else:
                copro_name = 'none'
            if queryset_reader.count() > 0:
                reader1_name = str(queryset_reader[0].adviser)
                if queryset_reader.count() > 1:
                    reader2_name = str(queryset_reader[1].adviser)
                else:
                    reader2_name = 'none'
            else:
                reader1_name = 'none'

            ws1.append([dissert.creation_date,
                        str(dissert.author),
                        dissert.title,
                        dissert.status,
                        dissert.offer_year_start.title,
                        dissert.offer_year_start.title_short, pro_name, copro_name, reader1_name, reader2_name])

        response = HttpResponse(save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "attachment; filename=" + filename
        return response
    return layout.render(request, "manager_dissertations_list.html",
                         {'dissertations': dissertations,
                          'offer_proposition': offer_proposition,
                          'xlsx': xlsx})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_delete(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    dissert.active = False
    dissert.save()
    # create update log
    update = DissertationUpdate()
    update.status_from = dissert.status
    update.status_to = dissert.status
    update.justification = "manager_set_active_false"
    update.person = mdl.person.find_by_user(request.user)
    update.dissertation = dissert
    update.save()
    return redirect('manager_dissertations_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_role_delete(request, pk):
    dissert_role = get_object_or_404(DissertationRole, pk=pk)
    dissertation = dissert_role.dissertation
    dissert_role.delete()
    return redirect('manager_dissertations_detail', pk=dissertation.pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_submit(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    old_status = dissertation.status

    if dissertation.status == 'DRAFT' or dissertation.status == 'DIR_KO':
        dissertation.status = 'DIR_SUBMIT'
        dissertation.save()
    elif dissertation.status == 'TO_RECEIVE':
        dissertation.status = 'TO_DEFEND'
        dissertation.save()
    elif dissertation.status == 'TO_DEFEND':
        dissertation.status = 'DEFENDED'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('manager_dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_submit_list(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    old_status = dissertation.status

    if dissertation.status == 'DRAFT' or dissertation.status == 'DIR_KO':
        dissertation.status = 'DIR_SUBMIT'
        dissertation.save()
    elif dissertation.status == 'TO_RECEIVE':
        dissertation.status = 'TO_DEFEND'
        dissertation.save()
    elif dissertation.status == 'TO_DEFEND':
        dissertation.status = 'DEFENDED'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('manager_dissertations_wait_recep_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ok(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    offer_proposition = OfferProposition.objects.get(offer=dissertation.offer_year_start.offer)
    old_status = dissertation.status

    if offer_proposition.validation_commission_exists and dissertation.status == 'DIR_SUBMIT':
        dissertation.status = 'COM_SUBMIT'
        dissertation.save()
    elif offer_proposition.evaluation_first_year and (
                    dissertation.status == 'DIR_SUBMIT' or dissertation.status == 'COM_SUBMIT'):
        dissertation.status = 'EVA_SUBMIT'
        dissertation.save()
    elif dissertation.status == 'EVA_SUBMIT':
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()
    elif dissertation.status == 'DEFENDED':
        dissertation.status = 'ENDED_WIN'
        dissertation.save()
    else:
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('manager_dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ok_comm_list(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    offer_proposition = OfferProposition.objects.get(offer=dissertation.offer_year_start.offer)
    old_status = dissertation.status

    if offer_proposition.validation_commission_exists and dissertation.status == 'DIR_SUBMIT':
        dissertation.status = 'COM_SUBMIT'
        dissertation.save()
    elif offer_proposition.evaluation_first_year and (
                    dissertation.status == 'DIR_SUBMIT' or dissertation.status == 'COM_SUBMIT'):
        dissertation.status = 'EVA_SUBMIT'
        dissertation.save()
    elif dissertation.status == 'EVA_SUBMIT':
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()
    elif dissertation.status == 'DEFENDED':
        dissertation.status = 'ENDED_WIN'
        dissertation.save()
    else:
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('manager_dissertations_wait_comm_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ok_eval_list(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    offer_proposition = OfferProposition.objects.get(offer=dissertation.offer_year_start.offer)
    old_status = dissertation.status

    if offer_proposition.validation_commission_exists and dissertation.status == 'DIR_SUBMIT':
        dissertation.status = 'COM_SUBMIT'
        dissertation.save()
    elif offer_proposition.evaluation_first_year and (
                    dissertation.status == 'DIR_SUBMIT' or dissertation.status == 'COM_SUBMIT'):
        dissertation.status = 'EVA_SUBMIT'
        dissertation.save()
    elif dissertation.status == 'EVA_SUBMIT':
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()
    elif dissertation.status == 'DEFENDED':
        dissertation.status = 'ENDED_WIN'
        dissertation.save()
    else:
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('manager_dissertations_wait_eval_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ko(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    old_status = dissertation.status

    if dissertation.status == 'DIR_SUBMIT':
        dissertation.status = 'DIR_KO'
        dissertation.save()
    elif dissertation.status == 'COM_SUBMIT':
        dissertation.status = 'COM_KO'
        dissertation.save()
    elif dissertation.status == 'EVA_SUBMIT':
        dissertation.status = 'EVA_KO'
        dissertation.save()
    elif dissertation.status == 'DEFENDED':
        dissertation.status = 'ENDED_LOS'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('manager_dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    offer_proposition = OfferProposition.objects.get(offer=offer)
    disserts = Dissertation.objects.filter(Q(offer_year_start__offer=offer) & Q(status="DIR_SUBMIT"))
    return layout.render(request, 'manager_dissertations_wait_list.html',
                         {'dissertations': disserts,
                          'offer_proposition': offer_proposition})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_comm_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    offer_proposition = OfferProposition.objects.get(offer=offer)
    disserts = Dissertation.objects.filter(Q(offer_year_start__offer=offer) & Q(status="COM_SUBMIT"))
    return layout.render(request, 'manager_dissertations_wait_commission_list.html',
                         {'dissertations': disserts,
                          'offer_proposition': offer_proposition})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_eval_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    offer_proposition = OfferProposition.objects.get(offer=offer)
    disserts = Dissertation.objects.filter(Q(offer_year_start__offer=offer) & Q(status="EVA_SUBMIT"))
    return layout.render(request, 'manager_dissertations_wait_eval_list.html',
                         {'dissertations': disserts,
                          'offer_proposition': offer_proposition})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_recep_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer = faculty_adviser.search_by_adviser(adv).offer
    offer_proposition = OfferProposition.objects.get(offer=offer)
    disserts = Dissertation.objects.filter(Q(offer_year_start__offer=offer) & Q(status="TO_RECEIVE"))
    return layout.render(request, 'manager_dissertations_wait_recep_list.html',
                         {'dissertations': disserts,
                          'offer_proposition': offer_proposition})


##########################
#      VUES TEACHER      #
##########################

@login_required
@user_passes_test(is_teacher)
def dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    queryset = DissertationRole.objects.all()
    adviser_list_dissertations = queryset.filter(Q(status='PROMOTEUR') &
                                                 Q(adviser__pk=adv.pk) &
                                                 Q(dissertation__active=True)).exclude(
        Q(dissertation__status='DRAFT'))
    adviser_list_dissertations = adviser_list_dissertations.order_by('dissertation__status',
                                                                     'dissertation__author__person__last_name',
                                                                     'dissertation__author__person__first_name')
    adviser_list_dissertations_copro = queryset.filter(Q(status='CO_PROMOTEUR') &
                                                       Q(adviser__pk=adv.pk) &
                                                       Q(dissertation__active=True)).exclude(
        Q(dissertation__status='DRAFT'))
    adviser_list_dissertations_copro = \
        adviser_list_dissertations_copro.order_by('dissertation__status',
                                                  'dissertation__author__person__last_name',
                                                  'dissertation__author__person__first_name')
    adviser_list_dissertations_reader = queryset.filter(Q(status='READER') &
                                                        Q(adviser__pk=adv.pk) &
                                                        Q(dissertation__active=True)).exclude(
        Q(dissertation__status='DRAFT'))
    adviser_list_dissertations_reader = \
        adviser_list_dissertations_reader.order_by('dissertation__status',
                                                   'dissertation__author__person__last_name',
                                                   'dissertation__author__person__first_name')
    return layout.render(request, "dissertations_list.html",
                         {'adviser': adv,
                          'adviser_list_dissertations': adviser_list_dissertations,
                          'adviser_list_dissertations_copro': adviser_list_dissertations_copro,
                          'adviser_list_dissertations_reader': adviser_list_dissertations_reader})


@login_required
@user_passes_test(is_teacher)
def dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    disserts = dissertation.search_by_proposition_author(terms=request.GET['search'],
                                                         active=True,
                                                         proposition_author=adv)
    return layout.render(request, "dissertations_list.html", {'dissertations': disserts})


@login_required
@user_passes_test(is_teacher)
def dissertations_detail(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_dissertation_role = DissertationRole.objects.filter(dissertation=dissertation).count()
    count_proposition_role = PropositionRole.objects \
        .filter(proposition_dissertation=dissertation.proposition_dissertation).count()
    proposition_roles = PropositionRole.objects.filter(proposition_dissertation=dissertation.proposition_dissertation)
    if count_proposition_role == 0:
        if count_dissertation_role == 0:
            pro = DissertationRole(status='PROMOTEUR',
                                   adviser=dissertation.proposition_dissertation.author,
                                   dissertation=dissertation)
            pro.save()
    else:
        if count_dissertation_role == 0:
            for prop_role in proposition_roles:
                jury = DissertationRole(status=prop_role.status,
                                        adviser=prop_role.adviser,
                                        dissertation=dissertation)
                jury.save()
    dissertation_roles = DissertationRole.objects.filter(dissertation=dissertation)
    return layout.render(request, 'dissertations_detail.html',
                         {'dissertation': dissertation,
                          'adviser': adv,
                          'dissertation_roles': dissertation_roles,
                          'count_dissertation_role': count_dissertation_role})


@login_required
@user_passes_test(is_teacher)
def dissertations_detail_updates(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    dissertation_updates = DissertationUpdate.objects.filter(dissertation=dissertation).order_by('created')
    return layout.render(request, 'dissertations_detail_updates.html',
                         {'dissertation': dissertation,
                          'adviser': adv,
                          'dissertation_updates': dissertation_updates})


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
    old_status = dissertation.status
    dissertation.status = 'DIR_SUBMIT'
    dissertation.save()
    insert_update(request, dissertation, old_status)
    return redirect('dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ok(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    old_status = dissertation.status
    offer_proposition = OfferProposition.objects.get(offer=dissertation.offer_year_start.offer)
    if offer_proposition.validation_commission_exists and dissertation.status == 'DIR_SUBMIT':
        dissertation.status = 'COM_SUBMIT'
        dissertation.save()
    elif offer_proposition.evaluation_first_year and (
                    dissertation.status == 'DIR_SUBMIT' or dissertation.status == 'COM_SUBMIT'):
        dissertation.status = 'EVA_SUBMIT'
        dissertation.save()
    elif dissertation.status == 'EVA_SUBMIT':
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()
    elif dissertation.status == 'DEFENDED':
        dissertation.status = 'ENDED_WIN'
        dissertation.save()
    else:
        dissertation.status = 'TO_RECEIVE'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ko(request, pk):
    dissertation = get_object_or_404(Dissertation, pk=pk)
    old_status = dissertation.status
    if dissertation.status == 'DIR_SUBMIT':
        dissertation.status = 'DIR_KO'
        dissertation.save()
    elif dissertation.status == 'COM_SUBMIT':
        dissertation.status = 'COM_KO'
        dissertation.save()
    elif dissertation.status == 'EVA_SUBMIT':
        dissertation.status = 'EVA_KO'
        dissertation.save()
    elif dissertation.status == 'DEFENDED':
        dissertation.status = 'ENDED_LOS'
        dissertation.save()

    insert_update(request, dissertation, old_status)
    return redirect('dissertations_detail', pk=pk)


@login_required
@user_passes_test(is_teacher)
def dissertations_wait_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)

    queryset = DissertationRole.objects.all()
    roles_list_dissertations = queryset.filter(Q(status='PROMOTEUR') &
                                               Q(adviser__pk=adv.pk) &
                                               Q(dissertation__active=True) &
                                               Q(dissertation__status="DIR_SUBMIT"))
    roles_list_dissertations = roles_list_dissertations.order_by(
                                                    'dissertation__author__person__last_name',
                                                    'dissertation__author__person__first_name')
    return layout.render(request, 'dissertations_wait_list.html',
                         {'roles_list_dissertations': roles_list_dissertations})
