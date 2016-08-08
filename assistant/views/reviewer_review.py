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
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from assistant.models import assistant_mandate, review, mandate_structure
from assistant.models import reviewer
from base.models import  person
from assistant.forms import ReviewForm
from django.core.urlresolvers import reverse
from django.utils import timezone

@login_required
def review_view(request, mandate_id, reviewer_id=None):
    """
    Ouvre en lecture une review pour consultation.

    La variable links permet de gérer l'affichage d'une liste représentant l'avancement du workflow.
    links[0] = superviseur de thèse.
    links[1] = recherche (président d'institut ou délégué).
    links[2] = supervision (doyen de faculté ou délégué).
    links[3] = vice-recteur de secteur ou assistant du vice-recteur de secteur.

    :param mandate_id: pk du mandat auquel la review est liée.
    :param reviewer_id: pk du revieser considéré. Si None, c'est une review faite par un superviseur de thèse
    """
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    this_reviewer = reviewer.find_by_person(person.find_by_user(request.user))
    try:
        current_reviewer = reviewer.find_by_id(reviewer_id)
        current_review = review.find_review_for_mandate_by_role(mandate, current_reviewer.role)
    except:
        current_review = review.find_done_by_supervisor_for_mandate(mandate)
    reviews = review.find_by_mandate(mandate.id)
    links = [[None,False], [None,False], [None,False], [None,False]]
    for rev in reviews:
        if rev.reviewer == None:
            if reviewer_id is None:
                links[0] = [True, True]
            else:
                links[0] = [True, False]
        elif "RESEARCH" in rev.reviewer.role:
            if rev == current_review:
                links[1] = [rev.reviewer.id, True]
            else:
                links[1] = [rev.reviewer.id, False]
        elif "SUPERVISION" in rev.reviewer.role:
            if rev == current_review:
                links[2] = [rev.reviewer.id, True]
            else:
                links[2] = [rev.reviewer.id, False]
        elif "SECTOR_VICE_RECTOR" in rev.reviewer.role:
            if rev == current_review:
                links[3] = [rev.reviewer.id, True]
            else:
                links[3] = [rev.reviewer.id, False, rev.status]
    assistant = mandate.assistant
    return render(request, 'review_view.html', {'review': current_review,
                                                'role': this_reviewer.role,
                                                'links': links,
                                                'mandate_id': mandate.id,
                                                'mandate_state': mandate.state,
                                                'assistant': assistant,
                                                'year': mandate.academic_year.year +1})

@login_required
def review_edit(request, mandate_id):
    """
    Edition d'une review. Si elle n'existe pas encore, elle est crée avant édition.
    Si l'utilisateur connecté ne peut pas éditer la review, on vérifie s'il est phd_supervisor.
    Si oui et que l'état du mandat (state) le justifie, on édite la review ou une nouvelle est créée si
    elle n'existe pas.

    La variable links permet de gérer l'affichage d'une liste représentant l'avancement du workflow.
    links[0] = superviseur de thèse.
    links[1] = recherche (président d'institut ou délégué).
    links[2] = supervision (doyen de faculté ou délégué).
    links[3] = vice-recteur de secteur ou assistant du vice-recteur de secteur.

    :param mandate_id: pk du mandat auquel la review est liée.
    :return:
    """
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    current_reviewer = None
    try:
        current_reviewer = reviewer.canEditReview(reviewer.find_by_person(person.find_by_user(request.user)).
                                                  id, mandate_id)
        delegate_role = current_reviewer.role + "_ASSISTANT"
        existing_review = review.find_review_for_mandate_by_role(mandate, delegate_role)
        if existing_review is None:
            existing_review, created = review.Review.objects.get_or_create(
                mandate=mandate,
                reviewer=current_reviewer,
                status='IN_PROGRESS'
            )
    except:
        if mandate.assistant.supervisor == person.find_by_user(request.user) and mandate.state == "PHD_SUPERVISOR":
            try:
                review.find_done_by_supervisor_for_mandate(mandate)
                return HttpResponseRedirect(reverse("assistants_home"))
            except:
                existing_review, created = review.Review.objects.get_or_create(
                    mandate=mandate,
                    reviewer=None,
                    status='IN_PROGRESS'
                )
        else:
            return HttpResponseRedirect(reverse('assistants_home'))
    previous_mandates = assistant_mandate.find_before_year_for_assistant(mandate.academic_year.year, mandate.assistant)
    reviews = review.find_by_mandate(mandate).filter(status = "DONE")
    links = [None,None,None,None]
    for rev in reviews:
        if rev.reviewer == None:
            links[0]='True'
        elif "RESEARCH" in rev.reviewer.role:
            links[1] = rev.reviewer.id
        elif "SUPERVISION" in rev.reviewer.role:
            links[2] = rev.reviewer.id
        elif "SECTOR_VICE_RECTOR" in rev.reviewer.role:
            links[3] = rev.reviewer.id
    try:
        role = current_reviewer.role
    except:
        role="PHD_SUPERVISOR"
    assistant = mandate.assistant
    form = ReviewForm(initial={'mandate': mandate,
                               'reviewer': existing_review.reviewer,
                               'status': existing_review.status,
                               'advice': existing_review.advice,
                               'changed': timezone.now,
                               'confidential': existing_review.confidential,
                               'remark': existing_review.remark,
                               'justification': existing_review.justification
                                }, prefix="rev", instance=existing_review)
    return render(request, 'review_form.html', {'review': existing_review,
                                                'role': role,
                                                'year': mandate.academic_year.year +1,
                                                'absences': mandate.absences,
                                                'comment': mandate.comment,
                                                'mandate_id': mandate.id,
                                                'previous_mandates': previous_mandates,
                                                'assistant': assistant,
                                                'links': links,
                                                'form': form})

@login_required
def review_save(request, review_id, mandate_id):
    """
    Sauvegarde de la review.
    Si formulaire VALIDE par l'utilisateur, passage à l'étape suivante dans le workflow : mandate.state.
    :param review_id: pk de la review à sauvegarder
    :param mandate_id: pk du mandat auquel la review est liée
    """
    rev = review.find_by_id(review_id)
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    form = ReviewForm(data=request.POST, instance=rev, prefix='rev')
    if form.is_valid():
        current_review = form.save(commit=False)
        if 'validate_and_submit' in request.POST:
            current_review.status = "DONE"
            current_review.save()
            if mandate.state == "PHD_SUPERVISOR":
                if mandate_structure.find_by_mandate_and_type(mandate, 'INSTITUTE'):
                    mandate.state = "RESEARCH"
                elif mandate_structure.find_by_mandate_and_part_of_type(mandate, 'INSTITUTE'):
                    mandate.state = "RESEARCH"
                else:
                    mandate.state = "SUPERVISION"
            elif mandate.state == "RESEARCH":
                mandate.state = "SUPERVISION"
            elif mandate.state == "SUPERVISION":
                mandate.state = "VICE_RECTOR"
            elif mandate.state == "VICE_RECTOR":
                mandate.state = "DONE"
            mandate.save()
            if current_review.reviewer is not None:
                return HttpResponseRedirect(reverse("reviewer_mandates_list"))
            else:
                return HttpResponseRedirect(reverse("review_view", kwargs={'mandate_id':mandate_id}))
        elif 'save' in request.POST:
            current_review.status = "IN_PROGRESS"
            current_review.save()
            return review_edit(request, mandate_id)
    else:
        return render(request, "review_form.html", {'review': rev,
                                                'role': mandate.state,
                                                'year': mandate.academic_year.year +1,
                                                'absences': mandate.absences,
                                                'comment': mandate.comment,
                                                'mandate_id': mandate.id,
                                                'form': form})
