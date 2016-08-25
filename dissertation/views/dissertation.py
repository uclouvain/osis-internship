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
from base import models as mdl
from base.views import layout
from dissertation.models.adviser import Adviser
from dissertation.models import adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models import dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models import dissertation_role
from dissertation.models import dissertation_update
from dissertation.models import faculty_adviser
from dissertation.models import offer_proposition
from dissertation.models import proposition_dissertation
from dissertation.models import proposition_role
from dissertation.forms import ManagerDissertationForm, ManagerDissertationEditForm, ManagerDissertationRoleForm, \
    ManagerDissertationUpdateForm
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
from django.http import HttpResponse
import time


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


#########################
#      GLOBAL VIEW      #
#########################


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


###########################
#      MANAGER VIEWS      #
###########################

@login_required
@user_passes_test(is_manager)
def manager_dissertations_detail(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    count_proposition_role = proposition_role.count_by_dissertation(dissert)
    proposition_roles = proposition_role.search_by_dissertation(dissert)

    if count_proposition_role == 0:
        if count_dissertation_role == 0:
            dissertation_role.add('PROMOTEUR', dissert.proposition_dissertation.author, dissert)
    else:
        if count_dissertation_role == 0:
            for role in proposition_roles:
                dissertation_role.add(role.status, role.adviser, dissert)

    dissertation_roles = dissertation_role.search_by_dissertation(dissert)
    return layout.render(request, 'manager_dissertations_detail.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_roles': dissertation_roles,
                          'count_dissertation_role': count_dissertation_role})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_detail_updates(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    dissertation_updates = dissertation_update.search_by_dissertation(dissert)

    return layout.render(request, 'manager_dissertations_detail_updates.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_updates': dissertation_updates})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_edit(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)

    if request.method == "POST":
        form = ManagerDissertationEditForm(request.POST, instance=dissert)
        if form.is_valid():
            dissert = form.save()
            justification = "manager_edit_dissertation"
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            return redirect('manager_dissertations_detail', pk=dissert.pk)
        else:
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offers)
            form.fields["author"].queryset = mdl.student.find_by_offer(offers)
            form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)
    else:
        form = ManagerDissertationEditForm(instance=dissert)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offers)
        form.fields["author"].queryset = mdl.student.find_by_offer(offers)
        form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)

    return layout.render(request, 'manager_dissertations_edit.html',
                         {'form': form,
                          'defend_periode_choices': Dissertation.DEFEND_PERIODE_CHOICES,
                          'dissert': dissert
                          })


@login_required
@user_passes_test(is_manager)
def manager_dissertations_jury_edit(request, pk):
    dissert_role = get_object_or_404(DissertationRole, pk=pk)
    if request.method == "POST":
        form = ManagerDissertationRoleForm(request.POST, instance=dissert_role)
        if form.is_valid():
            form.save()
            return redirect('manager_dissertations_detail', pk=dissert_role.dissertation.pk)
    else:
        form = ManagerDissertationRoleForm(instance=dissert_role)
    return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_jury_new(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    if count_dissertation_role < 5:
        if request.method == "POST":
            form = ManagerDissertationRoleForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                status = data['status']
                adv = data['adviser']
                diss = data['dissertation']
                justification = "%s %s %s" % ("manager_add_jury", str(status), str(adv))
                dissertation_update.add(request, dissert, dissert.status, justification=justification)
                dissertation_role.add(status, adv, diss)
                return redirect('manager_dissertations_detail', pk=dissert.pk)
        else:
            form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
            return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form,
                                                                                   'dissert': dissert})
    else:
        return redirect('manager_dissertations_detail', pk=dissert.pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    disserts = dissertation.search_by_offer(offers)
    offer_props = offer_proposition.search_by_offer(offers)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    return layout.render(request, 'manager_dissertations_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_new(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    if request.method == "POST":
        form = ManagerDissertationForm(request.POST)
        if form.is_valid():
            dissert = form.save()
            justification = "manager_creation_dissertation"
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            return redirect('manager_dissertations_detail', pk=dissert.pk)
        else:
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offers)
            form.fields["author"].queryset = mdl.student.find_by_offer(offers)
            form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)

    else:
        form = ManagerDissertationForm(initial={'active': True})
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offers)
        form.fields["author"].queryset = mdl.student.find_by_offer(offers)
        form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)
    return layout.render(request, 'manager_dissertations_new.html', {'form': form})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_search(request):
    disserts = dissertation.search(terms=request.GET['search'], active=True)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    offer_props = offer_proposition.search_by_offer(offers)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    xlsx = False

    if 'bt_xlsx' in request.GET:
        filename = "%s%s%s" % ('EXPORT_dissertation_', time.strftime("%Y-%m-%d %H:%M"), '.xlsx')
        workbook = Workbook(encoding='utf-8')
        worksheet1 = workbook.active
        worksheet1.title = "dissertation"
        worksheet1.append(['Date_de_création', 'Students', 'Dissertation_title',
                           'Status', 'Offer_year_start', 'offer_year_start_short', 'promoteur', 'copromoteur',
                           'lecteur1', 'lecteur2'])
        for dissert in disserts:
            pro_name = dissertation_role.get_promoteur_by_dissertation(dissert)
            copro_name = dissertation_role.get_copromoteur_by_dissertation(dissert)
            reader = dissertation_role.search_by_dissertation_and_role(dissert, 'READER')

            if reader:
                reader1_name = str(reader[0].adviser)
                if reader.count() > 1:
                    reader2_name = str(reader[1].adviser)
                else:
                    reader2_name = 'none'
            else:
                reader1_name = 'none'
                reader2_name = 'none'

            worksheet1.append([dissert.creation_date,
                               str(dissert.author),
                               dissert.title,
                               dissert.status,
                               dissert.offer_year_start.title,
                               dissert.offer_year_start.title_short, pro_name, copro_name, reader1_name, reader2_name])

        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
        return response

    else:
        return layout.render(request, "manager_dissertations_list.html",
                                      {'dissertations': disserts,
                                       'show_validation_commission': show_validation_commission,
                                       'show_evaluation_first_year': show_evaluation_first_year,
                                       'xlsx': xlsx})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_delete(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)

    dissert.deactivate()
    dissertation_update.add(request, dissert, dissert.status, justification="manager_set_active_false")

    return redirect('manager_dissertations_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_role_delete(request, pk):
    dissert_role = get_object_or_404(DissertationRole, pk=pk)
    dissert = dissert_role.dissertation
    justification = "%s %s" % ("manager_delete_jury", str(dissert_role))
    dissertation_update.add(request, dissert, dissert.status, justification=justification)
    dissert_role.delete()
    return redirect('manager_dissertations_detail', pk=dissert.pk)


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_submit(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    new_status = dissertation.get_next_status(dissert, "go_forward")

    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.go_forward()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('manager_dissertations_detail', pk=pk)

    else:
        form = ManagerDissertationUpdateForm()

    return layout.render(request, 'manager_dissertations_add_justification.html',
                         {'form': form, 'dissert': dissert, "old_status": old_status, "new_status": new_status})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_submit_list(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    dissert.go_forward()
    dissertation_update.add(request, dissert, old_status)

    return redirect('manager_dissertations_wait_recep_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ok(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    new_status = dissertation.get_next_status(dissert, "accept")

    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.accept()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('manager_dissertations_detail', pk=pk)

    else:
        form = ManagerDissertationUpdateForm()

    return layout.render(request, 'manager_dissertations_add_justification.html',
                         {'form': form, 'dissert': dissert, "old_status": old_status, "new_status": new_status})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_accept_comm_list(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    dissert.accept()
    dissertation_update.add(request, dissert, old_status)

    return redirect('manager_dissertations_wait_comm_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_accept_eval_list(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    dissert.accept()
    dissertation_update.add(request, dissert, old_status)

    return redirect('manager_dissertations_wait_eval_list')


@login_required
@user_passes_test(is_manager)
def manager_dissertations_to_dir_ko(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    new_status = dissertation.get_next_status(dissert, "refuse")

    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.refuse()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('manager_dissertations_detail', pk=pk)

    else:
        form = ManagerDissertationUpdateForm()

    return layout.render(request, 'manager_dissertations_add_justification.html',
                         {'form': form, 'dissert': dissert, "old_status": old_status, "new_status": new_status})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    offer_props = offer_proposition.search_by_offer(offers)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_offer_and_status(offers, "DIR_SUBMIT")

    return layout.render(request, 'manager_dissertations_wait_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_comm_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    offer_props = offer_proposition.search_by_offer(offers)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_offer_and_status(offers, "COM_SUBMIT")

    return layout.render(request, 'manager_dissertations_wait_commission_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_eval_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    offer_props = offer_proposition.search_by_offer(offers)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_offer_and_status(offers, "EVA_SUBMIT")

    return layout.render(request, 'manager_dissertations_wait_eval_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(is_manager)
def manager_dissertations_wait_recep_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offers = faculty_adviser.search_by_adviser(adv)
    offer_props = offer_proposition.search_by_offer(offers)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_offer_and_status(offers, "TO_RECEIVE")

    return layout.render(request, 'manager_dissertations_wait_recep_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


###########################
#      TEACHER VIEWS      #
###########################

@login_required
@user_passes_test(is_teacher)
def dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)

    adviser_list_dissertations = dissertation_role.search_by_adviser_and_role(adv, 'PROMOTEUR')
    adviser_list_dissertations_copro = dissertation_role.search_by_adviser_and_role(adv, 'CO_PROMOTEUR')
    adviser_list_dissertations_reader = dissertation_role.search_by_adviser_and_role(adv, 'READER')

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
    dissert = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    count_proposition_role = proposition_role.count_by_dissertation(dissert)
    proposition_roles = proposition_role.search_by_dissertation(dissert)

    if count_proposition_role == 0:
        if count_dissertation_role == 0:
            dissertation_role.add('PROMOTEUR', dissert.proposition_dissertation.author, dissert)

    else:
        if count_dissertation_role == 0:
            for role in proposition_roles:
                dissertation_role.add(role.status, role.adviser, dissert)

    dissertation_roles = dissertation_role.search_by_dissertation(dissert)
    return layout.render(request, 'dissertations_detail.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_roles': dissertation_roles,
                          'count_dissertation_role': count_dissertation_role})


@login_required
@user_passes_test(is_teacher)
def dissertations_detail_updates(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    dissertation_updates = dissertation_update.search_by_dissertation(dissert)
    return layout.render(request, 'dissertations_detail_updates.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_updates': dissertation_updates})


@login_required
@user_passes_test(is_teacher)
def dissertations_delete(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    dissert.deactivate()
    dissertation_update.add(request, dissert, dissert.status, justification="teacher_set_active_false ")
    return redirect('dissertations_list')


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ok(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    new_status = dissertation.get_next_status(dissert, "accept")

    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.accept()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('dissertations_detail', pk=pk)

    else:
        form = ManagerDissertationUpdateForm()

    return layout.render(request, 'dissertations_add_justification.html',
                         {'form': form, 'dissert': dissert, "old_status": old_status, "new_status": new_status})


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ko(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    new_status = dissertation.get_next_status(dissert, "refuse")

    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.refuse()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('dissertations_detail', pk=pk)

    else:
        form = ManagerDissertationUpdateForm()

    return layout.render(request, 'dissertations_add_justification.html',
                         {'form': form, 'dissert': dissert, "old_status": old_status, "new_status": new_status})


@login_required
@user_passes_test(is_teacher)
def dissertations_wait_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    roles_list_dissertations = dissertation_role.search_by_adviser_and_role_and_status(adv, "PROMOTEUR", "DIR_SUBMIT")

    return layout.render(request, 'dissertations_wait_list.html',
                         {'roles_list_dissertations': roles_list_dissertations})
