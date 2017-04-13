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
from base import models as mdl
from base.views import layout
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models import adviser, dissertation, dissertation_document_file, dissertation_role,\
    dissertation_update, faculty_adviser, offer_proposition, proposition_dissertation, proposition_role
from dissertation.forms import ManagerDissertationForm, ManagerDissertationEditForm, ManagerDissertationRoleForm, \
    ManagerDissertationUpdateForm, AdviserForm
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
from django.http import HttpResponse
import time


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'MGR' if this_adviser else False


# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_teacher(user):
    person = mdl.person.find_by_user(user)
    this_adviser = adviser.search_by_person(person)
    return this_adviser.type == 'PRF' if this_adviser else False


#########################
#      GLOBAL VIEW      #
#########################


@login_required
def dissertations(request):
    person = mdl.person.find_by_user(request.user)

    if mdl.student.find_by_person(person) and not \
            mdl.tutor.find_by_person(person) and not \
            adviser.find_by_person(person):
            return redirect('home')

    elif adviser.find_by_person(person):
        adv = adviser.search_by_person(person)
        count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')

        return layout.render(request, "dissertations.html",
                             {'section': 'dissertations',
                              'person': person,
                              'adviser': adv,
                              'count_advisers_pro_request': count_advisers_pro_request})
    else:
        if request.method == "POST":
            form = AdviserForm(request.POST)
            if form.is_valid():
                adv = Adviser(person=person, available_by_email=False, available_by_phone=False,
                              available_at_office=False)
                adv.save()
                adv = adviser.search_by_person(person)
                count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')

                return layout.render(request, "dissertations.html",
                                     {'section': 'dissertations',
                                      'person': person,
                                      'adviser': adv,
                                      'count_advisers_pro_request': count_advisers_pro_request})
        else:
            form = AdviserForm()
            return layout.render(request, 'dissertations_welcome.html', {'form': form})


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
    offer_prop = offer_proposition.get_by_dissertation(dissert)
    files = dissertation_document_file.find_by_dissertation(dissert)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role == 0:
        if count_dissertation_role == 0:
            justification = "%s %s %s" % ("auto_add_jury", 'PROMOTEUR', str(dissert.proposition_dissertation.author))
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissertation_role.add('PROMOTEUR', dissert.proposition_dissertation.author, dissert)
    else:
        if count_dissertation_role == 0:
            for role in proposition_roles:
                justification = "%s %s %s" % ("auto_add_jury", role.status, str(role.adviser))
                dissertation_update.add(request, dissert, dissert.status, justification=justification)
                dissertation_role.add(role.status, role.adviser, dissert)
    if dissert.status == "DRAFT":
        jury_manager_visibility = True
        jury_manager_can_edit = False
        jury_manager_message = 'manager_jury_draft'
        jury_teacher_visibility = False
        jury_teacher_can_edit = False
        jury_teacher_message = 'teacher_jury_draft'
        jury_student_visibility = True
        jury_student_can_edit = offer_prop.student_can_manage_readers
        if jury_student_can_edit:
            jury_student_message = 'student_jury_draft_can_edit_param'
        else:
            jury_student_message = 'student_jury_draft_no_edit_param'
    else:
        jury_manager_visibility = True
        jury_manager_can_edit = True
        jury_manager_message = 'manager_jury_editable'
        jury_teacher_visibility = True
        jury_teacher_can_edit = offer_prop.adviser_can_suggest_reader
        if jury_teacher_can_edit:
            jury_teacher_message = 'teacher_jury_visible_editable_parameter'
        else:
            jury_teacher_message = 'teacher_jury_visible_not_editable_parameter'
        jury_student_visibility = offer_prop.in_periode_jury_visibility
        jury_student_can_edit = False
        if jury_student_visibility:
            jury_student_message = 'student_jury_visible_dates'
        else:
            jury_student_message = 'student_jury_invisible_dates'
    dissertation_roles = dissertation_role.search_by_dissertation(dissert)
    return layout.render(request, 'manager_dissertations_detail.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_roles': dissertation_roles,
                          'count_dissertation_role': count_dissertation_role,
                          'jury_manager_visibility': jury_manager_visibility,
                          'jury_manager_can_edit': jury_manager_can_edit,
                          'jury_manager_message': jury_manager_message,
                          'jury_teacher_visibility': jury_teacher_visibility,
                          'jury_teacher_can_edit': jury_teacher_can_edit,
                          'jury_teacher_message': jury_teacher_message,
                          'jury_student_visibility': jury_student_visibility,
                          'jury_student_can_edit': jury_student_can_edit,
                          'jury_student_message': jury_student_message,
                          'filename': filename})


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
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
            form.fields["author"].queryset = mdl.student.find_by_offer(offers)
            form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)
    else:
        form = ManagerDissertationEditForm(instance=dissert)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
        form.fields["author"].queryset = mdl.student.find_by_offer(offers)
        form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)

    return layout.render(request, 'manager_dissertations_edit.html',
                         {'form': form,
                          'dissert': dissert,
                          'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES})


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
    if count_dissertation_role < 4 and dissert.status != 'DRAFT':
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
        else:
            form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
        return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form, 'dissert': dissert})
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
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
            form.fields["author"].queryset = mdl.student.find_by_offer(offers)
            form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)

    else:
        form = ManagerDissertationForm(initial={'active': True})
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
        form.fields["author"].queryset = mdl.student.find_by_offer(offers)
        form.fields["offer_year_start"].queryset = mdl.offer_year.find_by_offer(offers)
    return layout.render(request, 'manager_dissertations_new.html',
                         {'form': form,
                          'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES})


def generate_xls(disserts):
    workbook = Workbook(encoding='utf-8')
    worksheet1 = workbook.active
    worksheet1.title = "dissertations"
    worksheet1.append(['Creation_date',
                       'Student',
                       'Title',
                       'Status',
                       'Year + Program Start',
                       'Defend Year',
                       'Promotor',
                       'Co-promotor',
                       'Reader 1',
                       'Reader 2',
                       'Description'
                       ])
    for dissert in disserts:
        pro_name = dissertation_role.get_promoteur_by_dissertation_str(dissert)
        copro_name = dissertation_role.get_copromoteur_by_dissertation(dissert)
        readers = dissertation_role.search_by_dissertation_and_role(dissert, 'READER')
        defend_year = dissert.defend_year if dissert.defend_year else 'not_set'
        description = dissert.description if dissert.description else 'not_set'

        readers_count = readers.count()
        reader1_name = str(readers[0].adviser) if readers_count > 0 else 'none'
        reader2_name = str(readers[1].adviser) if readers_count > 1 else 'none'

        worksheet1.append([dissert.creation_date,
                           str(dissert.author),
                           dissert.title,
                           dissert.status,
                           str(dissert.offer_year_start),
                           defend_year,
                           pro_name,
                           copro_name,
                           reader1_name,
                           reader2_name,
                           description
                           ])
    return save_virtual_workbook(workbook)


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

    if 'bt_xlsx' in request.GET:
        xls = generate_xls(disserts)
        filename = 'dissertations_{}.xlsx'.format(time.strftime("%Y-%m-%d_%H:%M"))
        response = HttpResponse(xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
        return response

    else:
        return layout.render(request, "manager_dissertations_list.html",
                                      {'dissertations': disserts,
                                       'show_validation_commission': show_validation_commission,
                                       'show_evaluation_first_year': show_evaluation_first_year
                                       })


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
    if dissert.status != 'DRAFT':
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
    status_dict = dict(dissertation.STATUS_CHOICES)
    new_status_display = status_dict[new_status]

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
                         {'form': form, 'dissert': dissert, 'new_status_display': new_status_display})


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
    status_dict = dict(dissertation.STATUS_CHOICES)
    new_status_display = status_dict[new_status]

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
                         {'form': form, 'dissert': dissert, 'new_status_display': new_status_display})


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
    status_dict = dict(dissertation.STATUS_CHOICES)
    new_status_display = status_dict[new_status]

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
                         {'form': form, 'dissert': dissert, 'new_status_display': new_status_display})


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
    adviser_list_dissertations_accompanist = dissertation_role.search_by_adviser_and_role(adv, 'ACCOMPANIST')
    adviser_list_dissertations_internship = dissertation_role.search_by_adviser_and_role(adv, 'INTERNSHIP')

    return layout.render(request, "dissertations_list.html",
                         {'adviser': adv,
                          'adviser_list_dissertations': adviser_list_dissertations,
                          'adviser_list_dissertations_copro': adviser_list_dissertations_copro,
                          'adviser_list_dissertations_reader': adviser_list_dissertations_reader,
                          'adviser_list_dissertations_accompanist': adviser_list_dissertations_accompanist,
                          'adviser_list_dissertations_internship': adviser_list_dissertations_internship
                          })


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

    if dissertation_role.count_by_adviser_dissertation(adv, dissert) < 1:
        return redirect('dissertations_list')
    
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    count_proposition_role = proposition_role.count_by_dissertation(dissert)
    proposition_roles = proposition_role.search_by_dissertation(dissert)
    offer_prop = offer_proposition.get_by_dissertation(dissert)
    files = dissertation_document_file.find_by_dissertation(dissert)
    filename = ""
    promotors_count = dissertation_role.count_by_status_dissertation('PROMOTEUR', dissert)
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role == 0:
        if count_dissertation_role == 0:
            justification = "%s %s %s" % ("auto_add_jury", 'PROMOTEUR', str(dissert.proposition_dissertation.author))
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissertation_role.add('PROMOTEUR', dissert.proposition_dissertation.author, dissert)

    else:
        if count_dissertation_role == 0:
            for role in proposition_roles:
                justification = "%s %s %s" % ("auto_add_jury", role.status, str(role.adviser))
                dissertation_update.add(request, dissert, dissert.status, justification=justification)
                dissertation_role.add(role.status, role.adviser, dissert)

    dissertation_roles = dissertation_role.search_by_dissertation(dissert)
    return layout.render(request, 'dissertations_detail.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_roles': dissertation_roles,
                          'count_dissertation_role': count_dissertation_role,
                          'offer_prop': offer_prop,
                          'promotors_count': promotors_count,
                          'filename': filename})


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
    status_dict = dict(dissertation.STATUS_CHOICES)
    new_status_display = status_dict[new_status]

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
                         {'form': form, 'dissert': dissert, 'new_status_display': new_status_display})


@login_required
@user_passes_test(is_teacher)
def dissertations_to_dir_ko(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    old_status = dissert.status
    new_status = dissertation.get_next_status(dissert, "refuse")
    status_dict = dict(dissertation.STATUS_CHOICES)
    new_status_display = status_dict[new_status]

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
                         {'form': form, 'dissert': dissert, 'new_status_display': new_status_display})


@login_required
@user_passes_test(is_teacher)
def dissertations_wait_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    roles_list_dissertations = dissertation_role.search_by_adviser_and_role_and_status(adv, "PROMOTEUR", "DIR_SUBMIT")

    return layout.render(request, 'dissertations_wait_list.html',
                         {'roles_list_dissertations': roles_list_dissertations})


def can_delete_role(dissert, dissert_role):
    promotors_count = dissertation_role.count_by_status_dissertation('PROMOTEUR', dissert)
    return dissert_role.status != 'PROMOTEUR' or promotors_count > 1


@login_required
@user_passes_test(is_teacher)
def dissertations_role_delete(request, pk):
    dissert_role = get_object_or_404(DissertationRole, pk=pk)
    dissert = dissert_role.dissertation
    offer_prop = offer_proposition.get_by_dissertation(dissert)
    if offer_prop.adviser_can_suggest_reader and can_delete_role(dissert, dissert_role):
        justification = "%s %s" % ("teacher_delete_jury", str(dissert_role))
        dissertation_update.add(request, dissert, dissert.status, justification=justification)
        dissert_role.delete()
    return redirect('dissertations_detail', pk=dissert.pk)


@login_required
@user_passes_test(is_teacher)
def dissertations_jury_new(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    offer_prop = offer_proposition.get_by_dissertation(dissert)
    if count_dissertation_role < 4 and offer_prop.adviser_can_suggest_reader:
        if request.method == "POST":
            form = ManagerDissertationRoleForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                status = data['status']
                adv = data['adviser']
                diss = data['dissertation']
                justification = "%s %s %s" % ("teacher_add_jury", str(status), str(adv))
                dissertation_update.add(request, dissert, dissert.status, justification=justification)
                dissertation_role.add(status, adv, diss)
                return redirect('dissertations_detail', pk=dissert.pk)
            else:
                form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
        else:
            form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
        return layout.render(request, 'dissertations_jury_edit.html', {'form': form, 'dissert': dissert})
    else:
        return redirect('dissertations_detail', pk=dissert.pk)

