##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import json

import requests
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.person import Person
from base.models.person_address import PersonAddress
from internship.business.email import send_email
from internship.forms.internship_person_address_form import InternshipPersonAddressForm
from internship.forms.internship_person_form import InternshipPersonForm
from internship.forms.master import MasterForm
from internship.models import master_allocation, internship_master, internship_speciality, organization, cohort
from internship.models.enums import user_account_status
from internship.models.enums.role import Role
from internship.models.enums.user_account_status import UserAccountStatus
from internship.models.internship_master import InternshipMaster
from internship.utils.exporting.masters import export_xls
from internship.views.common import display_errors, get_object_list
from osis_common.decorators.download import set_download_cookie
from osis_common.messaging import message_config


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def masters(request, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    filter_specialty = int(request.GET.get('specialty', 0))
    filter_hospital = int(request.GET.get('hospital', 0))
    filter_name = request.GET.get('name', '')
    filter_role = request.GET.get('role', Role.MASTER.name)

    allocations = master_allocation.search(current_cohort, filter_specialty, filter_hospital, filter_role)
    if filter_name:
        allocations = allocations.filter(master__person__last_name__unaccent__icontains=filter_name) | \
                      allocations.filter(master__person__first_name__unaccent__icontains=filter_name)
    specialties = internship_speciality.find_by_cohort(current_cohort)
    hospitals = organization.find_by_cohort(current_cohort)
    allocations = get_object_list(request, allocations)
    account_status = user_account_status.UserAccountStatus.__members__
    return render(request, "masters.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def create_user_accounts(request, cohort_id):
    selected_masters = InternshipMaster.objects.filter(
        pk__in=request.POST.getlist('selected_master')
    ).select_related('person')

    filter_specialty = int(request.GET.get('specialty', 0))
    filter_hospital = int(request.GET.get('hospital', 0))
    filter_name = request.GET.get('name', '')

    for master in selected_masters:
        if _user_already_exists_for_master(master):
            _send_creation_account_email(master, connected_user=request.user)
            _show_user_already_exists_msg(request, master)
        else:
            _create_master_user_account(request, master)

    return redirect(
        "{url}?{query_params}".format(
            url=reverse('internships_masters',  kwargs={'cohort_id': cohort_id}),
            query_params='hospital={}&specialty={}&name={}'.format(filter_hospital, filter_specialty, filter_name)
        )
    )


def _user_already_exists_for_master(master):
    return master.user_account_status != UserAccountStatus.INACTIVE.name


def _create_master_user_account(request, master):
    if master.person.birth_date:
        response = _create_ldap_user_account(master)
        if response.status_code == 200:
            _send_creation_account_email(master, connected_user=request.user)
            _update_user_account_status(master, request)
        else:
            _display_creation_error_msg(master, request)
    else:
        _display_no_birth_date_error_msg(master, request)


def _display_no_birth_date_error_msg(master, request):
    messages.add_message(
        request, messages.ERROR,
        _('Unable to create a user account for {}: no birth date set').format(master.person),
        "alert-error"
    )


def _display_creation_error_msg(master, request):
    messages.add_message(
        request, messages.ERROR,
        _('An error occured while creating a user account for {}').format(master.person),
        "alert-error"
    )


def _update_user_account_status(master, request):
    if master.user_account_status == UserAccountStatus.INACTIVE.name:
        master.user_account_status = UserAccountStatus.PENDING.name
        master.save()
        messages.add_message(
            request, messages.SUCCESS,
            _('An email for account creation was sent to {}').format(master.person), "alert-success"
        )
    else:
        _show_user_already_exists_msg(request, master)


def _show_user_already_exists_msg(request, master):
    messages.add_message(
        request, messages.WARNING,
        _('User account creation for {} is already pending, an email was sent again').format(master.person),
        "alert-warning"
    )


def _create_ldap_user_account(master):
    response = requests.post(
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            "id": str(master.person.uuid),
            "datenaissance": master.person.birth_date.strftime('%Y%m%d%fZ'),
            "prenom": master.person.first_name,
            "nom": master.person.last_name,
            "email": master.person.email
        }),
        url=settings.LDAP_ACCOUNT_CREATION_URL
    )
    return response


def _send_creation_account_email(master, connected_user=None):
    set_password_link = '{}?email={}'.format(settings.LDAP_ACCOUNT_CONFIGURATION_URL, master.person.email)

    send_email(
        template_references={
            'html': 'internship_create_master_account_email_html',
            'txt': 'internship_create_master_account_email_txt',
        },
        data={
            'template': {
                'set_password_link': set_password_link,
                'score_encoding_link': settings.INTERNSHIP_SCORE_ENCODING_URL
            },
            'subject': {}
        },
        receivers=[
            message_config.create_receiver(
                master.id,
                master.person.email,
                None
            )
        ],
        connected_user=connected_user
    )


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master(request, cohort_id, master_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocated_master = internship_master.get_by_id(master_id)
    allocations = master_allocation.find_by_master(current_cohort, allocated_master)
    allocated_master_address = allocated_master.person.personaddress_set.first() if allocated_master.person else None
    return render(request, "master.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_form(request, cohort_id, master_id=None, allocated_master=None):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    if master_id:
        allocated_master = internship_master.get_by_id(master_id)
        allocations = master_allocation.find_by_master(current_cohort, allocated_master)

    master_form = MasterForm(request.POST or None, instance=allocated_master)
    person = allocated_master.person if allocated_master else None
    if request.POST.get('existing-person-id'):
        person = Person.objects.get(pk=request.POST.get('existing-person-id'))
    person_form = InternshipPersonForm(request.POST or None, instance=person)
    person_address = person.personaddress_set.first() if person else None
    person_address_form = InternshipPersonAddressForm(request.POST or None, instance=person_address)
    specialties = internship_speciality.find_by_cohort(current_cohort)
    hospitals = organization.find_by_cohort(current_cohort)
    roles = Role.choices()

    dynamic_fields = json.dumps(list(person_form.fields.keys()) + list(person_address_form.fields.keys()))

    return render(request, "master_form.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def person_exists(request, cohort_id):
    email = json.loads(request.body.decode("utf-8"))['email']
    person = Person.objects.filter(email=email).first()
    data = model_to_dict(person, exclude=['user', 'managed_entities']) if person else {}
    person_address = PersonAddress.objects.filter(person=person).first()
    if person_address:
        data.update(model_to_dict(person_address, exclude=['id']))
    return JsonResponse(data if person else {'err': 'not found'})


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_delete(request, master_id, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocated_master = internship_master.get_by_id(master_id)
    current_allocations = master_allocation.find_by_master(current_cohort, allocated_master)
    # will only delete current allocations
    if current_allocations:
        current_allocations.delete()
    msg_content = "{} {} : {} {}".format(
        _('Master allocations deleted in'),
        current_cohort,
        allocated_master.person.last_name,
        allocated_master.person.first_name
    ) if allocated_master.person else "{}".format(_('Master deleted'))
    messages.add_message(request, messages.SUCCESS, msg_content, "alert-success")
    return HttpResponseRedirect(reverse('internships_masters', kwargs={'cohort_id': cohort_id,}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def master_save(request, cohort_id):
    current_cohort = shortcuts.get_object_or_404(cohort.Cohort, pk=cohort_id)
    allocated_master = internship_master.get_by_id(request.POST.get("id")) if request.POST.get("id") else None
    form_master = MasterForm(request.POST, instance=allocated_master)
    person = allocated_master.person if allocated_master else None
    if not person and request.POST.get('existing-person-id'):
        person = Person.objects.get(pk=request.POST.get('existing-person-id'))
    form_person = InternshipPersonForm(request.POST, instance=person)
    person_address = person.personaddress_set.first() if person else None
    form_person_address = InternshipPersonAddressForm(request.POST or None, instance=person_address)
    errors = []
    hospital = ""
    if form_master.is_valid() and form_person.is_valid() and form_person_address.is_valid():
        allocated_master = form_master.instance
        if _validate_allocations(request):
            person = form_person.save()
            address = form_person_address.save(commit=False)
            address.person = person
            address.save()
            master = form_master.save()
            master.person = person
            master.save()
            master_allocation.clean_allocations(current_cohort, allocated_master)
            allocations = _build_allocations(request, allocated_master)
            _save_allocations(allocations)
            hospital = _extract_hospital_id(allocations)
        else:
            errors.append(form_master.errors)
            errors.append(form_person.errors)
            errors.append(form_person_address.errors)
            messages.add_message(
                request,
                messages.ERROR,
                _('A master must be affected to at least one hospital or one specialty with a role.'),
                "alert-danger"
            )
    else:
        errors.append(form_master.errors)
        errors.append(form_person.errors)
        errors.append(form_person_address.errors)
        display_errors(request, errors)

    if errors:
        return master_form(request=request, cohort_id=current_cohort.id, allocated_master=allocated_master)

    return HttpResponseRedirect("{}?hospital={}".format(reverse("internships_masters", args=[current_cohort.id]),
                                                        hospital))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
@set_download_cookie
def export_masters(request, cohort_id):
    workbook = export_xls()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=masters.xlsx'
    return response


def _build_allocations(request, allocated_master):
    hospitals = []
    if 'hospital' in request.POST:
        hospitals = request.POST.getlist('hospital')
        hospitals = _clean_empty_strings(hospitals)

    specialties = []
    if 'specialty' in request.POST:
        specialties = request.POST.getlist('specialty')
        specialties = _clean_empty_strings(specialties)

    roles = []
    if 'role' in request.POST:
        roles = request.POST.getlist('role')
        roles = _clean_empty_strings(roles)

    allocations_data = list(zip(hospitals, specialties, roles))

    allocations = []

    for hospital_id, specialty_id, role in allocations_data:
        hospital = organization.get_by_id(hospital_id) if hospital_id else None
        specialty = internship_speciality.get_by_id(specialty_id) if specialty_id else None
        if role:
            allocation = master_allocation.MasterAllocation(
                master=allocated_master,
                organization=hospital,
                specialty=specialty,
                role=role
            )
            allocations.append(allocation)

    return allocations


def _clean_empty_strings(a_list):
    return [x if x != '' else None for x in a_list]


def _save_allocations(allocations):
    for allocation in allocations:
        allocation.save()
        

def _extract_hospital_id(allocations):
    if allocations and allocations[0].organization:
        return allocations[0].organization.id
    else:
        return 0


def _validate_allocations(request):
    hospitals = request.POST.getlist('hospital')
    specialties = request.POST.getlist('specialty')
    roles = request.POST.getlist('role')
    return (hospitals[0] != '' or specialties[0] != '') and roles[0] != ''
