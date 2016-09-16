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
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from assistant.models import *
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from assistant.forms import *
from base.models import person_address, person
from assistant.models.academic_assistant import find_by_id
from assistant.models.assistant_mandate import find_mandate_by_id, find_mandate_by_academic_assistant
from base.models.person import find_by_user
from base.models import person_address, person
from django.core.exceptions import ObjectDoesNotExist


def user_is_assistant_and_procedure_is_open(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are assistant.
    The procedure must be open"""

    try:
        if user.is_authenticated() and settings.access_to_procedure_is_open():
            return academic_assistant.find_by_person(user.person)
        else:
            return False
    except ObjectDoesNotExist:
        return False


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part1_edit(request, mandate_id):
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    assistant = mandate.assistant
    addresses = person_address.find_by_person(person.find_by_id(assistant.person.id))
    form = AssistantFormPart1(initial={'inscription': assistant.inscription,
                                       'expected_phd_date': assistant.expected_phd_date,
                                       'phd_inscription_date': assistant.phd_inscription_date,
                                       'confirmation_test_date': assistant.confirmation_test_date,
                                       'thesis_date': assistant.thesis_date,
                                       'addresses': addresses,
                                       'supervisor': assistant.supervisor})
    form2 = AssistantFormPart1b(initial={'external_functions': mandate.external_functions,
                                       'external_contract': mandate.external_contract,
                                       'justification': mandate.justification})
    
    return render(request, "assistant_form_part1.html", {'assistant': assistant,
                                                         'mandate': mandate,
                                                         'addresses': addresses,
                                                         'form': form,
                                                         'form2': form2}) 


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part1_save(request, mandate_id):
    """Use to save an assistant form part1."""
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    assistant = mandate.assistant
    addresses = person_address.find_by_person(person.find_by_id(assistant.person.id))
    form = AssistantFormPart1(data=request.POST, instance=assistant)
    form2 = AssistantFormPart1b(data=request.POST, instance=mandate)
    if form.is_valid() and form2.is_valid():
        form.save()
        form2.save()
        return form_part1_edit(request, mandate.id)
    else:
        return render(request, "assistant_form_part1.html", {'assistant': assistant,
                                                     'mandate': mandate,
                                                     'addresses': addresses,
                                                     'form': form,
                                                     'form2': form2})


@login_required
def tutoring_learning_unit_add(request, mandate_id):
    form = TutoringLearningUnitForm(initial={'mandate_id': mandate_id,
                                             'tutoring_learning_unit_year_id': None
                                             })
    return render(request, "tutoring_learning_unit_year.html", {'form': form,
                                                                'mandate_id': mandate_id
                                                                })


@login_required
def tutoring_learning_unit_edit(request, tutoring_learning_unit_id=None):
    edited_learning_unit_year = mdl.tutoring_learning_unit_year.find_by_id(tutoring_learning_unit_id)
    academic_year = edited_learning_unit_year.learning_unit_year.academic_year
    mandate_id = edited_learning_unit_year.mandate_id
    form = TutoringLearningUnitForm(initial={'mandate_id': edited_learning_unit_year.mandate_id,
                                    'tutoring_learning_unit_year_id': edited_learning_unit_year.id,
                                    'learning_unit_year': edited_learning_unit_year.learning_unit_year.acronym,
                                    'sessions_duration': edited_learning_unit_year.sessions_duration,
                                    'sessions_number': edited_learning_unit_year.sessions_number,
                                    'series_number': edited_learning_unit_year.series_number,
                                    'face_to_face_duration': edited_learning_unit_year.face_to_face_duration,
                                    'attendees': edited_learning_unit_year.attendees,
                                    'preparation_duration': edited_learning_unit_year.preparation_duration,
                                    'exams_supervision_duration': edited_learning_unit_year.exams_supervision_duration,
                                    'others_delivery': edited_learning_unit_year.others_delivery,
                                    'academic_year': academic_year.id
                                             })
    return render(request, "tutoring_learning_unit_year.html", {'form': form,
                                                                'mandate_id': mandate_id
                                                                    })


@login_required
def tutoring_learning_unit_save(request, mandate_id):

    form = TutoringLearningUnitForm(data=request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('mandate_learning_units', kwargs={'mandate_id':mandate_id}))
    else:
        return render(request, "tutoring_learning_unit_year.html", {'form': form,
                                                                    'mandate_id': mandate_id})


@login_required
def tutoring_learning_unit_delete(request, tutoring_learning_unit_id):
    learning_unit_year = mdl.tutoring_learning_unit_year.find_by_id(tutoring_learning_unit_id)
    mandate_id = learning_unit_year.mandate_id
    mdl.tutoring_learning_unit_year.find_by_id(tutoring_learning_unit_id).delete()
    return HttpResponseRedirect(reverse('mandate_learning_units', kwargs={'mandate_id':mandate_id}))


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part4_edit(request, mandate_id):
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    person = request.user.person
    assistant = mandate.assistant
    if person != assistant.person or mandate.state != 'TRTS':
        return HttpResponseRedirect(reverse('assistant_mandates'))
    form = AssistantFormPart4(initial={'internships': mandate.internships,
                                       'conferences': mandate.conferences,
                                       'publications': mandate.publications,
                                       'awards': mandate.awards,
                                       'framing': mandate.framing,
                                       'remark': mandate.remark,
                                       }, prefix='mand')
    return render(request, "assistant_form_part4.html", {'assistant': assistant,
                                                         'mandate': mandate,
                                                         'form': form})


def form_part4_save(request, mandate_id):
    """Use to save an assistant form part4."""
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    assistant = mandate.assistant
    person = request.user.person
    if person != assistant.person or mandate.state != 'TRTS':
        return HttpResponseRedirect(reverse('assistant_mandates'))
    elif request.method == 'POST':
        form = AssistantFormPart4(data=request.POST, instance=mandate, prefix='mand')
        if form.is_valid():
            form.save()
            return form_part4_edit(request, mandate.id)
        else:
            return render(request, "assistant_form_part4.html", {'assistant': assistant,
                                                                 'mandate': mandate,
                                                                 'form': form})


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part6_edit(request, mandate_id):
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    person = request.user.person
    assistant = mandate.assistant
    if person != assistant.person or mandate.state != 'TRTS':
        return HttpResponseRedirect(reverse('assistant_mandates'))
    form = AssistantFormPart6(initial={'tutoring_percent': mandate.tutoring_percent,
                                       'service_activities_percent': mandate.service_activities_percent,
                                       'formation_activities_percent': mandate.formation_activities_percent,
                                       'research_percent': mandate.research_percent,
                                       'activities_report_remark': mandate.activities_report_remark
                                       }, prefix='mand')
    return render(request, "assistant_form_part6.html", {'assistant': assistant,
                                                         'mandate': mandate,
                                                         'form': form})


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part6_save(request, mandate_id):
    """Use to save an assistant form part6."""
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    assistant = mandate.assistant
    person = request.user.person
    if person != assistant.person or mandate.state != 'TRTS':
        return HttpResponseRedirect(reverse('assistant_mandates'))
    elif request.method == 'POST':
        form = AssistantFormPart6(data=request.POST, instance=mandate, prefix='mand')
        if form.is_valid():
            if 'validate_and_submit' in request.POST:
                if assistant.supervisor:
                    mandate.state='PHD_SUPERVISOR'
                elif mandate.assistant_type == "TEACHING_ASSISTANT":
                    mandate.state='SUPERVISION'
                else:
                    mandate.state='RESEARCH'
                form.save()
                return HttpResponseRedirect(reverse('assistant_mandates'))
            else:
                form.save()
                return form_part6_edit(request, mandate.id)
        else:
            return render(request, "assistant_form_part6.html", {'assistant': assistant,
                                                             'mandate': mandate,
                                                             'form': form})


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part5_edit(request, mandate_id):
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    person = request.user.person
    assistant = mandate.assistant
    if person != assistant.person or mandate.state != 'TRTS':
        return HttpResponseRedirect(reverse('assistant_mandates'))
    form = AssistantFormPart5(initial={'faculty_representation': mandate.faculty_representation,
                                       'institute_representation': mandate.institute_representation,
                                       'sector_representation': mandate.sector_representation,
                                       'governing_body_representation': mandate.governing_body_representation,
                                       'corsci_representation': mandate.corsci_representation,
                                       'students_service': mandate.students_service,
                                       'infrastructure_mgmt_service': mandate.infrastructure_mgmt_service,
                                       'events_organisation_service': mandate.events_organisation_service,
                                       'publishing_field_service': mandate.publishing_field_service,
                                       'scientific_jury_service': mandate.scientific_jury_service,
                                       'degrees': mandate.degrees,
                                       'formations': mandate.formations
                                       }, prefix='mand')
    return render(request, "assistant_form_part5.html", {'assistant': assistant,
                                                         'mandate': mandate,
                                                         'form': form}) 


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def form_part5_save(request, mandate_id):
    """Use to save an assistant form part5."""
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    assistant = mandate.assistant
    person = request.user.person
    if person != assistant.person or mandate.state != 'TRTS':
        return HttpResponseRedirect(reverse('assistant_mandates'))
    elif request.method == 'POST':
        form = AssistantFormPart5(data=request.POST, instance=mandate, prefix='mand')
        if form.is_valid():
            form.save()
            return form_part5_edit(request, mandate.id)
        else:
            return render(request, "assistant_form_part5.html", {'assistant': assistant,
                                                             'mandate': mandate,
                                                             'form': form}) 
