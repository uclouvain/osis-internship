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
from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from base import models as mdl
from base.views.layout import render
from internship import models as mdl_int
from internship.forms.form_offer_preference import OfferPreferenceForm, OfferPreferenceFormSet
from internship.forms.form_select_speciality import SpecialityForm
from internship.forms.internship import InternshipForm
from internship.views.common import display_errors


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def modification_student(request, cohort_id, student_id, internship_id=-1, speciality_id="-1"):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)
    if int(internship_id) < 1:
        internship = mdl_int.internship.Internship.objects.filter(
            cohort=cohort,
            pk__gte=1
        ).order_by('speciality__name').first()
        internship_id = internship.id
    else:
        internship = mdl_int.internship.Internship.objects.get(pk=internship_id)

    speciality = _get_speciality(internship_id, speciality_id, student)
    if speciality:
        speciality_id = speciality.id

    internships_offers = mdl_int.internship_offer.find_by_speciality(speciality).select_related(
        "organization",
        "speciality",
    )

    offer_preference_formset = _initialize_offer_preference_formset(internships_offers)
    formset = offer_preference_formset()

    if request.method == 'POST':
        formset = offer_preference_formset(request.POST)
        if formset.is_valid():
            messages.add_message(request, messages.SUCCESS, _("Choices saved"), "alert-success")
            _remove_previous_choices(student, internship)
            _save_student_choices(formset, student, internship, speciality, cohort)
        else:
            display_errors(request, formset.errors)

    student_choices = mdl_int.internship_choice.search_by_student_or_choice(
        student=student,
        internship=internship
    ).select_related("organization")

    internships = mdl_int.internship.Internship.objects.filter(cohort=cohort, pk__gte=1)\
        .order_by("speciality__name", "name")\
        .select_related("speciality")

    zipped_data = _prepare_template_data(formset, student_choices, internships_offers, speciality, student,
                                         internship_id)
    information = mdl_int.internship_student_information.find_by_person(student.person, cohort)

    context = {
        "internships": internships,
        "speciality_form": SpecialityForm(cohort=cohort, specialty_id=speciality_id),
        "formset": formset,
        "offers_forms": zipped_data,
        "internship": internship,
        "speciality_id": int(speciality_id),
        "student": student,
        "information": information,
        "cohort": cohort
    }
    return render(request, "internship_modification_student.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def assign_speciality_for_internship(request, cohort_id, student_id, internship_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    speciality_id = None
    if request.method == "POST":
        speciality_form = SpecialityForm(request.POST, cohort=cohort, specialty_id=speciality_id)
        if speciality_form.is_valid():
            speciality_selected = speciality_form.cleaned_data["speciality"]
            speciality_id = speciality_selected.id
    return redirect("specific_internship_student_modification", cohort_id=cohort_id, student_id=student_id,
                    internship_id=internship_id, speciality_id=speciality_id)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def edit_period_places(request, cohort_id, internship_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    internship_offer = get_object_or_404(mdl_int.internship_offer.InternshipOffer, pk=internship_id, cohort=cohort)
    period_places_values = _get_current_period_places(internship_offer)
    context = {
        "internship": internship_offer,
        "period_places": period_places_values,
        'cohort': cohort,
    }
    return render(request, "period_places_edit.html", context)


@login_required
@require_POST
@permission_required('internship.is_internship_manager', raise_exception=True)
def save_period_places(request, cohort_id, internship_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    internship_offer = get_object_or_404(mdl_int.internship_offer.InternshipOffer, pk=internship_id, cohort=cohort)

    periods_dict = _get_dict_of_periods(cohort)
    if not internship_offer:
        return redirect('edit_period_places', cohort_id=cohort.id, internship_id=internship_id)

    _delete_previous_period_places(internship_offer)

    for period_name in periods_dict.keys():
        period_number_places = int(request.POST.get(period_name, 0))
        _save_period_places(internship_offer, periods_dict[period_name], period_number_places)
    mdl_int.period_internship_places.update_maximum_enrollments(internship_offer)

    return redirect('edit_period_places', cohort_id=cohort.id, internship_id=internship_id)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_list(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    internships = mdl_int.internship.Internship.objects.filter(cohort_id=cohort_id)
    context = {
        'cohort': cohort,
        'internships': internships,
    }
    return render(request, 'internship/list.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_new(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)

    inter = mdl_int.internship.Internship(cohort_id=cohort_id)
    form = InternshipForm(request.POST or None, instance=inter)
    if form.is_valid():
        form.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            "{} : {}".format(_('Internship modality created'), inter.name),
            "alert-success"
        )
        return redirect(reverse('internship-list', kwargs={
            'cohort_id': cohort.id,
        }))

    context = {
        'form': form,
        'cohort': cohort,
        'page_title': _('New internship'),
    }
    return render(request, 'internship/internship_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_edit(request, cohort_id, internship_id):
    inter = get_object_or_404(mdl_int.internship.Internship, pk=internship_id, cohort_id=cohort_id)
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)

    form = InternshipForm(data=request.POST or None, instance=inter)

    if form.is_valid():
        form.cohort_id = cohort_id
        form.save()

        return redirect(reverse('internship-list', kwargs={
            'cohort_id': cohort.id,
        }))

    context = {
        'form': form,
        'page_title': _('Edit internship'),
        'cohort': cohort,
    }

    return render(request, 'internship/internship_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_delete(request, cohort_id, internship_id):
    inter = get_object_or_404(mdl_int.internship.Internship, pk=internship_id, cohort_id=cohort_id)
    inter.delete()
    messages.add_message(
        request, messages.SUCCESS, "{} : {}".format(_('Internship modality deleted'), inter.name), "alert-success"
    )
    return redirect(reverse('internship-list', kwargs={
        'cohort_id': cohort_id,
    }))


def set_tabs_name(specialities, student=None):
    """
        Set tab name for the html page base on the speciality
        and eventually the size of the choice of a student for a speciality
        (check if the student have done the correct the number of choice for this speciality)
        Params :
            specialities : the specialities we want to create the tab name
            student : default there is no student, if yes, used to get the number of choice
                        for a speciality for this student
    """
    for speciality in specialities:
        if student:
            size = len(mdl_int.internship_choice.search(speciality=speciality, student=student))
            speciality.size = size
        tab = speciality.name.replace(" ", "")
        speciality.tab = tab


def get_all_specialities(internships):
    """
        Function to create the list of the specialities, delete dpulicated and order alphabetical.
        Param:
            internships : the interships we want to get the speciality
    """
    tab = []
    for internship in internships:
        tab.append(internship.speciality)

    tab = list(OrderedDict.fromkeys(tab))
    return tab


def _prepare_template_data(formset, current_choices, internships_offers, speciality, student, internship_id):
    current_enrollments = mdl_int.internship_enrollment.search_by_student_and_internship(student, internship_id)
    dict_current_choices = _get_dict_current_choices(current_choices)
    dict_current_enrollments = _get_dict_current_enrollments(current_enrollments)
    dict_offers_choices = _get_first_choices_by_organization(speciality, internship_id)
    zipped_data = _zip_data(dict_current_choices, formset, internships_offers, dict_current_enrollments,
                            dict_offers_choices)
    return zipped_data


def _initialize_offer_preference_formset(internships_offers):
    offer_preference_formset = formset_factory(OfferPreferenceForm, formset=OfferPreferenceFormSet,
                                               extra=internships_offers.count(), min_num=internships_offers.count(),
                                               max_num=internships_offers.count(), validate_min=True, validate_max=True)
    return offer_preference_formset


def _get_speciality(internship_id, speciality_id, student):
    if speciality_id == "-1":
        return _find_speciality_of_choices_for_internship(internship_id, student)

    return mdl_int.internship_speciality.get_by_id(speciality_id)


def _find_speciality_of_choices_for_internship(internship_id, student):
    choices = list(mdl_int.internship_choice.search_by_student_or_choice(student, internship_id))
    if choices:
        return choices[0].speciality
    return None


def _get_dict_current_choices(current_choices):
    dict_current_choices = dict()
    for current_choice in current_choices:
        dict_current_choices[(current_choice.organization.id, current_choice.speciality.id)] = current_choice
    return dict_current_choices


def _get_dict_current_enrollments(current_enrollments):
    dict_current_enrollments= dict()
    for enrollment in current_enrollments:
        key = enrollment.internship_offer.id
        if key not in dict_current_enrollments:
            dict_current_enrollments[key] = []
        dict_current_enrollments[key].append(enrollment.period.name)
    return dict_current_enrollments


def _get_first_choices_by_organization(speciality, internship_id):
    list_number_choices = mdl_int.internship_choice.get_number_first_choice_by_organization(speciality, internship_id)
    dict_number_choices_by_organization = dict()
    for number_first_choices in list_number_choices:
        dict_number_choices_by_organization[number_first_choices["organization"]] = \
            number_first_choices["organization__count"]
    return dict_number_choices_by_organization


def _zip_data(dict_current_choices, formset, internships_offers, dict_current_enrollments, dict_offers_choices):
    if not internships_offers:
        return None
    zipped_data = []
    zipped_data_for_offer_selected = []
    elements = _generate_elements(dict_current_choices, dict_current_enrollments, dict_offers_choices, formset,
                                 internships_offers)
    for element in elements:
        if int(element[2]):
            zipped_data_for_offer_selected.append(element)
        else:
            zipped_data.append(element)
    zipped_data_for_offer_selected.sort(key=lambda x: x[2])
    zipped_data_for_offer_selected.extend(zipped_data)
    return zipped_data_for_offer_selected


def _generate_elements(dict_curr_choices, dict_curr_enrollments, dict_offers_choices, formset, internships_offers):
    for offer, form in zip(internships_offers, formset):
        offer_choice = dict_curr_choices.get((offer.organization.id, offer.speciality.id), None)
        offer_value = 0 if not offer_choice else offer_choice.choice
        offer_priority = False if not offer_choice else offer_choice.priority
        offer_enrollments = dict_curr_enrollments.get(offer.id, [])
        number_first_choices = dict_offers_choices.get(offer.organization.id, 0)
        element = (offer, form, str(offer_value), offer_priority, offer_enrollments, number_first_choices)
        yield element


def _remove_previous_choices(student, internship):
    previous_choices = mdl_int.internship_choice.search_by_student_or_choice(student=student, internship=internship)
    if previous_choices:
        previous_choices.delete()
    previous_enrollments = mdl_int.internship_enrollment.search_by_student_and_internship(student=student,
                                                                                          internship=internship)
    if previous_enrollments:
        previous_enrollments.delete()


def _save_student_choices(formset, student, internship, speciality, cohort):
    for form in formset:
        if form.cleaned_data:
            offer_pk = form.cleaned_data["offer"]
            preference_value = int(form.cleaned_data["preference"])
            priority = form.cleaned_data['priority']
            offer = mdl_int.internship_offer.find_by_id(offer_pk)
            if _has_been_selected(preference_value) and _is_correct_speciality(offer, speciality):
                internship_choice = mdl_int.internship_choice.InternshipChoice(student=student,
                                                                               organization=offer.organization,
                                                                               speciality=speciality,
                                                                               choice=preference_value,
                                                                               internship=internship,
                                                                               priority=priority)
                internship_choice.save()
                _save_enrollments(form, offer, student, internship, cohort)


def _save_enrollments(form, offer, student, internship, cohort):
    periods_name = form.cleaned_data.get("periods", [])
    for period_name in periods_name:
        period = mdl_int.period.Period.objects.get(name=period_name, cohort=cohort)
        if not period:
            continue
        enrollment = mdl_int.internship_enrollment. \
            InternshipEnrollment(student=student, internship_offer=offer, place=offer.organization,
                                 period=period, internship=internship)
        enrollment.save()


def _has_been_selected(preference_value):
    return bool(preference_value)


def _is_correct_speciality(offer, speciality):
    return offer.speciality == speciality


def _get_dict_of_periods(cohort):
    periods = mdl_int.period.find_by_cohort(cohort)
    periods_dict = dict()
    for period in periods:
        periods_dict[period.name] = period
    return periods_dict


def _save_period_places(internship_offer, period, number_places):
    if number_places <= 0:
        return

    period_places = mdl_int.period_internship_places.PeriodInternshipPlaces(period=period,
                                                                            internship_offer=internship_offer,
                                                                            number_places=number_places)
    period_places.save()


def _delete_previous_period_places(internship_offer):
    mdl_int.period_internship_places.find_by_internship_offer(internship_offer).delete()


def _get_current_period_places(internship_offer):
    keys = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12']
    periods_places = _get_dict_period_places(internship_offer)
    periods = []
    for key in keys:
        period_place = periods_places.get(key, None)
        number_places = 0
        if period_place:
            number_places = period_place.number_places
        periods.append((key, number_places))
    return periods


def _get_dict_period_places(internship_offer):
    periods_places = mdl_int.period_internship_places.find_by_internship_offer(internship_offer)
    periods_places_dict = dict()
    for period_place in periods_places:
        periods_places_dict[period_place.period.name] = period_place
    return periods_places_dict
