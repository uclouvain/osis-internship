##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import re
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from base.models import person, entity_version
from base.models.enums import entity_type
from assistant.forms import ReviewForm
from assistant.models import assistant_mandate, review, mandate_entity, tutoring_learning_unit_year
from assistant.models import reviewer, settings, assistant_document_file
from assistant.models.enums import review_status, assistant_mandate_state, reviewer_role, document_type


def user_is_reviewer_and_procedure_is_open(user):
    try:
        if user.is_authenticated() and settings.access_to_procedure_is_open():
            return reviewer.find_by_person(user.person)
        else:
            return False
    except ObjectDoesNotExist:
        return False


@user_passes_test(user_is_reviewer_and_procedure_is_open, login_url='access_denied')
def review_view(request):
    mandate_id = request.POST.get("mandate_id")
    role = request.POST.get("role")
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    current_reviewer = reviewer.find_by_person(request.user.person)
    entity = entity_version.get_last_version(current_reviewer.entity)
    current_role = current_reviewer.role
    if role == reviewer_role.PHD_SUPERVISOR:
        try:
            current_review = review.find_done_by_supervisor_for_mandate(mandate)
        except ObjectDoesNotExist:
            current_review = None
    else:
        current_review = review.find_review_for_mandate_by_role(mandate, role)
    assistant = mandate.assistant
    menu = generate_reviewer_menu_tabs(current_role, mandate, role)
    return render(request, 'review_view.html', {'review': current_review,
                                                'role': current_role,
                                                'menu': menu,
                                                'menu_type': 'reviewer_menu',
                                                'mandate_id': mandate.id,
                                                'mandate_state': mandate.state,
                                                'current_reviewer': current_reviewer,
                                                'entity': entity,
                                                'assistant': assistant,
                                                'year': mandate.academic_year.year + 1
                                                })


@user_passes_test(user_is_reviewer_and_procedure_is_open, login_url='access_denied')
def review_edit(request):
    mandate_id = request.POST.get("mandate_id")
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    current_reviewer = reviewer.can_edit_review(
        reviewer.find_by_person(person.find_by_user(request.user)).id, mandate_id
    )
    entity = entity_version.get_last_version(current_reviewer.entity)
    delegate_role = current_reviewer.role + "_ASSISTANT"
    existing_review = review.find_review_for_mandate_by_role(mandate, delegate_role)
    if existing_review is None:
        existing_review, created = review.Review.objects.get_or_create(
            mandate=mandate,
            reviewer=current_reviewer,
            status=review_status.IN_PROGRESS
        )
    previous_mandates = assistant_mandate.find_before_year_for_assistant(mandate.academic_year.year, mandate.assistant)
    role = current_reviewer.role
    menu = generate_reviewer_menu_tabs(role, mandate, role)
    assistant = mandate.assistant
    form = ReviewForm(initial={'mandate': mandate,
                               'reviewer': existing_review.reviewer,
                               'status': existing_review.status,
                               'advice': existing_review.advice,
                               'changed': timezone.now,
                               'confidential': existing_review.confidential,
                               'remark': existing_review.remark
                               }, prefix="rev", instance=existing_review)
    return render(request, 'review_form.html', {'review': existing_review,
                                                'role': role,
                                                'year': mandate.academic_year.year + 1,
                                                'absences': mandate.absences,
                                                'comment': mandate.comment,
                                                'mandate_id': mandate.id,
                                                'previous_mandates': previous_mandates,
                                                'assistant': assistant,
                                                'current_reviewer': current_reviewer,
                                                'entity': entity,
                                                'menu': menu,
                                                'menu_type': 'reviewer_menu',
                                                'form': form})


@user_passes_test(user_is_reviewer_and_procedure_is_open, login_url='access_denied')
def review_save(request):
    mandate_id = request.POST.get("mandate_id")
    review_id = request.POST.get("review_id")
    rev = review.find_by_id(review_id)
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    current_reviewer = reviewer.can_edit_review(reviewer.find_by_person(person.find_by_user(request.user)).id,
                                                mandate_id)
    form = ReviewForm(data=request.POST, instance=rev, prefix='rev')
    previous_mandates = assistant_mandate.find_before_year_for_assistant(mandate.academic_year.year, mandate.assistant)
    role = current_reviewer.role
    entity = entity_version.get_last_version(current_reviewer.entity)
    menu = generate_reviewer_menu_tabs(role, mandate, role)
    if form.is_valid():
        current_review = form.save(commit=False)
        if 'validate_and_submit' in request.POST:
            current_review.status = review_status.DONE
            current_review.save()
            if mandate.state == assistant_mandate_state.PHD_SUPERVISOR:
                if mandate_entity.find_by_mandate_and_type(mandate, entity_type.INSTITUTE):
                    mandate.state = assistant_mandate_state.RESEARCH
                elif mandate_entity.find_by_mandate_and_type(mandate, entity_type.POLE):
                    mandate.state = assistant_mandate_state.RESEARCH
                else:
                    mandate.state = assistant_mandate_state.SUPERVISION
            elif mandate.state == assistant_mandate_state.RESEARCH:
                mandate.state = assistant_mandate_state.SUPERVISION
            elif mandate.state == assistant_mandate_state.SUPERVISION:
                mandate.state = assistant_mandate_state.VICE_RECTOR
            elif mandate.state == assistant_mandate_state.VICE_RECTOR:
                mandate.state = assistant_mandate_state.DONE
            mandate.save()
            if current_review.reviewer is not None:
                return HttpResponseRedirect(reverse("reviewer_mandates_list"))
            else:
                return HttpResponseRedirect(reverse("phd_supervisor_assistants_list"))
        elif 'save' in request.POST:
            current_review.status = review_status.IN_PROGRESS
            current_review.save()
            return review_edit(request)
    else:
        return render(request, "review_form.html", {'review': rev,
                                                    'role': mandate.state,
                                                    'year': mandate.academic_year.year + 1,
                                                    'absences': mandate.absences,
                                                    'comment': mandate.comment,
                                                    'mandate_id': mandate.id,
                                                    'previous_mandates': previous_mandates,
                                                    'assistant': mandate.assistant,
                                                    'entity': entity,
                                                    'menu': menu,
                                                    'menu_type': 'reviewer_menu',
                                                    'form': form})


@user_passes_test(user_is_reviewer_and_procedure_is_open, login_url='access_denied')
def pst_form_view(request):
    mandate_id = request.POST.get("mandate_id")
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    current_reviewer = reviewer.find_by_person(request.user.person)
    current_role = current_reviewer.role
    entity = entity_version.get_last_version(current_reviewer.entity)
    learning_units = tutoring_learning_unit_year.find_by_mandate(mandate)
    phd_files = assistant_document_file.find_by_assistant_mandate_and_description(mandate,
                                                                                  document_type.PHD_DOCUMENT)
    research_files = assistant_document_file.find_by_assistant_mandate_and_description(mandate,
                                                                                       document_type.RESEARCH_DOCUMENT)
    tutoring_files = assistant_document_file.find_by_assistant_mandate_and_description(mandate,
                                                                                       document_type.TUTORING_DOCUMENT)
    assistant = mandate.assistant
    menu = generate_reviewer_menu_tabs(current_role, mandate, None)
    return render(request, 'pst_form_view.html', {'menu': menu,
                                                  'menu_type': 'reviewer_menu',
                                                  'mandate_id': mandate.id,
                                                  'assistant': assistant, 'mandate': mandate,
                                                  'learning_units': learning_units,
                                                  'entity': entity,
                                                  'phd_files': phd_files,
                                                  'research_files': research_files,
                                                  'tutoring_files': tutoring_files,
                                                  'current_reviewer': current_reviewer,
                                                  'role': current_role,
                                                  'year': mandate.academic_year.year + 1})


def generate_reviewer_menu_tabs(role, mandate, active_item: None):
    if active_item:
        active_item = re.sub('_ASSISTANT', '', active_item)
    menu = []
    mandate_states = {}
    if mandate.assistant.supervisor:
        mandate_states.update({assistant_mandate_state.PHD_SUPERVISOR: 1})
    if mandate_entity.find_by_mandate_and_type(mandate, entity_type.INSTITUTE):
        mandate_states.update({assistant_mandate_state.RESEARCH: 2,
                               assistant_mandate_state.SUPERVISION: 3,
                               assistant_mandate_state.VICE_RECTOR: 4})
    else:
        mandate_states.update({assistant_mandate_state.SUPERVISION: 3,
                               assistant_mandate_state.VICE_RECTOR: 4})
    try:
        latest_review_done = review.find_review_for_mandate_by_role(mandate, role)
        review_is_done = latest_review_done.status == review_status.DONE
    except:
        review_is_done = False
    for state, order in sorted(mandate_states.items()):
        if state == assistant_mandate_state.VICE_RECTOR and role != reviewer_role.VICE_RECTOR \
                and role != reviewer_role.VICE_RECTOR_ASSISTANT:
            break
        if state in role and review_is_done is False:
            if active_item == state:
                menu.append({'item': state, 'class': 'active', 'action': 'edit'})
            else:
                menu.append({'item': state, 'class': '', 'action': 'edit'})
        if mandate.state == state:
            break
        elif active_item == state:
            menu.append({'item': state, 'class': 'active', 'action': 'view'})
        else:
            menu.append({'item': state, 'class': '', 'action': 'view'})
    return menu
