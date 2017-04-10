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
from math import acos, cos, degrees, radians, sin

from collections import OrderedDict
from operator import itemgetter

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, redirect, render, get_list_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from base import models as mdl
from internship import models as mdl_internship
from internship.forms.form_offer_preference import (OfferPreferenceForm,
                                                    OfferPreferenceFormSet)
from internship.forms.form_select_speciality import SpecialityForm
from internship.forms.internship import InternshipForm
from internship.models.cohort import Cohort
from internship.models.internship import Internship
from internship.models.internship_offer import InternshipOffer


def calc_dist(lat_a, long_a, lat_b, long_b):
    """
        Function to compute the distance between two points.
        Params:
            lat_a : the latitude of the first adress
            long_a : the longitude of the first adress
            lat_b : the latitude of the second adress
            long_b : the longitude of the second adress
        Transform the params in radians then compute the sin and cos
        then transform it in miles or kilometers.
        Based on :
            https://gmigdos.wordpress.com/2010/03/31/python-calculate-the-distance-between-2-points-given-their-coordinates/
    """
    if lat_a == lat_b and long_a == long_b:
        # If there is the same adress, there is a chance to have a bug/crash
        # So it return 100 meters of distance
        return 0.1
    else:
        lat_a = radians(float(lat_a))
        lat_b = radians(float(lat_b))
        long_a = float(long_a)
        long_b = float(long_b)
        long_diff = radians(long_a - long_b)
        distance = (sin(lat_a) * sin(lat_b) +
                    cos(lat_a) * cos(lat_b) * cos(long_diff))
        # For distance in miles use this
        # return (degrees(acos(distance)) * 69.09)
        # For distance in kilometers use this
        return (degrees(acos(distance)) * 69.09)/0.621371


def work_dist(student, organizations):
    """
        Function to get the distances between the student and all organization in the DB, sorted asc
        Params:
            student : the student we want to get the latitude and longitude of
            organizations : the organizations in the DB, to compute their latitude/longitude with the student's
    """
    # Find the student's informations
    student_informations = mdl_internship.internship_student_information.search(person__last_name=student.person.last_name, person__first_name=student.person.first_name)

    distance_student_organization = {}
    # For each organization in the list find the informations
    for organization in organizations :
        organization_informations = mdl_internship.organization_address.search(organization = organization)
        # If the latitude is not a fake number, compute the distance between the student and the organization
        if organization_informations[0].latitude != 999 :
            distance = calc_dist(student_informations[0].latitude, student_informations[0].longitude,
                                 organization_informations[0].latitude, organization_informations[0].longitude)
            distance_student_organization[int(organization.reference)] = distance

    # Sort the distance
    distance_student_organization = sorted(distance_student_organization.items(), key=itemgetter(1))
    return distance_student_organization


def get_number_choices(internships):
    """
        Set new variables for the param, the number of the first and other choice for one internship
        Params :
            internships : the internships we want to compute the number of choices
    """
    for internship in internships:
        number_first_choice = len(mdl_internship.internship_choice.search(organization = internship.organization,
                                                            speciality__acronym = internship.speciality.acronym,
                                                           choice=1))
        number_other_choice = len(mdl_internship.internship_choice.search_other_choices(organization = internship.organization,
                                                            speciality__acronym = internship.speciality.acronym))
        internship.number_first_choice = number_first_choice
        internship.number_other_choice = number_other_choice

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
        if student :
            size = len(mdl_internship.internship_choice.search(speciality=speciality, student=student))
            speciality.size = size
        tab = speciality.name.replace(" ", "")
        speciality.tab = tab

def get_selectable(internships):
    """
        Function to check if the internships are selectable.
        Return the status of the first internship.
        If there is no internship, return True
    """
    if len(internships) > 0:
        return internships[0].selectable
    else:
        return True

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


def get_all_organizations(internships):
    """
        Function to create the options for the organizations selection list, delete duplicated
        Param:
            internships : the interships we want to get the organization
    """
    tab = []
    for internship in internships:
        tab.append(internship.organization)
    tab = list(set(tab))
    return tab


def rebuild_the_lists(preference_list, speciality_list, organization_list, internship_choice_tab=None):
    """
        Look over each value of the preference list
        If the value is 0, the student doesn't choice this organization or speciality
        So their value is 0
        Params :
            preference_list, speciality_list, organization_list, internship_choice_tab :
            The list to check the choices
    """
    index = 0
    for r in preference_list:
        if r == "0":
            speciality_list[index] = 0
            organization_list[index] = 0
            if internship_choice_tab:
                internship_choice_tab[index] = 0
        index += 1


def delete_dublons_keep_order(seq):
    """
        Function to delete the dublons of any list and keep the order of the list.
        Param:
            seq : the list where there is dublons
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def sort_internships(sort_internships):
    """
        Function to sort internships by the organization's reference.
        Params :
            sort_internships : the list of internships to be sorted
        Extract the ref of the organization, sort based in integer (the ref are in string),
        delete the dublons recreat the list of internship base of the organization reference
    """
    tab = []
    number_ref = []
    for sort_internship in sort_internships:
        if sort_internship is not None:
            number_ref.append(sort_internship.organization.reference)
    number_ref=sorted(number_ref, key=int)
    number_ref=delete_dublons_keep_order(number_ref)
    for i in number_ref:
        internships = mdl_internship.internship_offer.search(organization__reference=i)
        for internship in internships:
            tab.append(internship)
    return tab


def set_student_choices_list(query,student_choice):
    """
        Function to set the list of the student's choices
        Params :
            query : the list of all internships
            student_choice : the list of the internships choose by the student
        Check if the internships and the choice are the same,
        if yes put the param of the max enrollments and if there are selectable.
        Then delete the internships in the list of the list of all internships
        (because it's all ready in the choices list wich it display first)
    """
    index = 0
    for choice in student_choice:
        for internship in query:
            if internship.organization == choice.organization and \
                            internship.speciality == choice.speciality:
                choice.maximum_enrollments = internship.maximum_enrollments
                choice.selectable = internship.selectable
                query[index] = 0
            index += 1
        query = [x for x in query if x != 0]
        index = 0
    query = [x for x in query if x != 0]
    return query


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_modification_student(request, cohort_id, student_id, internship_id=-1, speciality_id="-1"):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)

    if int(internship_id) < 1:
        internship = mdl_internship.internship.Internship.objects.filter(cohort=cohort, pk__gte=1).first()
    else:
        internship = mdl_internship.internship.Internship.objects.get(pk=internship_id)

    speciality = get_speciality(internship_id, speciality_id, student)
    if speciality:
        speciality_id = speciality.id

    internships_offers = mdl_internship.internship_offer.find_by_speciality(speciality)

    offer_preference_formset = initialize_offer_preference_formset(internships_offers)
    formset = offer_preference_formset()

    if request.method == 'POST':
        formset = offer_preference_formset(request.POST)
        if formset.is_valid():
            remove_previous_choices(student, internship)
            save_student_choices(formset, student, internship, speciality)

    student_choices = mdl_internship.internship_choice.search_by_student_or_choice(student=student,
                                                                                   internship=internship)

    internships = mdl_internship.internship.Internship.objects.filter(cohort=cohort, pk__gte=1)

    zipped_data = prepare_template_data(formset, student_choices, internships_offers, speciality, student,
                                        internship_id)
    information = mdl_internship.internship_student_information.find_by_person(student.person)

    context = {
        "internships": internships,
        "speciality_form": SpecialityForm(),
        "formset": formset,
        "offers_forms": zipped_data,
        "internship_id": internship.id,
        "speciality_id": int(speciality_id),
        "student": student,
        "information": information,
        "cohort": cohort
    }
    return render(request, "internship_modification_student.html", context)


def prepare_template_data(formset, current_choices, internships_offers, speciality, student, internship_id):

    current_enrollments = mdl_internship.internship_enrollment.search_by_student_and_internship(student, internship_id)
    dict_current_choices = get_dict_current_choices(current_choices)
    dict_current_enrollments = get_dict_current_enrollments(current_enrollments)
    dict_offers_choices = get_first_choices_by_organization(speciality)
    zipped_data = zip_data(dict_current_choices, formset, internships_offers, dict_current_enrollments,
                           dict_offers_choices)
    return zipped_data


def initialize_offer_preference_formset(internships_offers):
    offer_preference_formset = formset_factory(OfferPreferenceForm, formset=OfferPreferenceFormSet,
                                               extra=internships_offers.count(), min_num=internships_offers.count(),
                                               max_num=internships_offers.count(), validate_min=True, validate_max=True)
    return offer_preference_formset


def get_speciality(internship_id, speciality_id, student):
    if speciality_id == "-1":
        return find_speciality_of_choices_for_internship(internship_id, student)

    return mdl_internship.internship_speciality.get_by_id(speciality_id)


def find_speciality_of_choices_for_internship(internship_id, student):
    choices = list(mdl_internship.internship_choice.search_by_student_or_choice(student, internship_id))
    if choices:
        return choices[0].speciality
    return None


def get_dict_current_choices(current_choices):
    dict_current_choices = dict()
    for current_choice in current_choices:
        dict_current_choices[(current_choice.organization.id, current_choice.speciality.id)] = current_choice
    return dict_current_choices


def get_dict_current_enrollments(current_enrollments):
    dict_current_enrollments= dict()
    for enrollment in current_enrollments:
        key = enrollment.internship_offer.id
        if key not in dict_current_enrollments:
            dict_current_enrollments[key] = []
        dict_current_enrollments[key].append(enrollment.period.name)
    return dict_current_enrollments


def get_first_choices_by_organization(speciality):
    list_number_choices = mdl_internship.internship_choice.get_number_first_choice_by_organization(speciality)
    dict_number_choices_by_organization = dict()
    for number_first_choices in list_number_choices:
        dict_number_choices_by_organization[number_first_choices["organization"]] = \
            number_first_choices["organization__count"]
    return dict_number_choices_by_organization


def zip_data(dict_current_choices, formset, internships_offers, dict_current_enrollments, dict_offers_choices):
    if not internships_offers:
        return None
    zipped_data = []
    zipped_data_for_offer_selected = []
    elements = generate_elements(dict_current_choices, dict_current_enrollments, dict_offers_choices, formset,
                                 internships_offers)
    for element in elements:
        if int(element[2]):
            zipped_data_for_offer_selected.append(element)
        else:
            zipped_data.append(element)
    zipped_data_for_offer_selected.sort(key=lambda x: x[2])
    zipped_data_for_offer_selected.extend(zipped_data)
    return zipped_data_for_offer_selected


def generate_elements(dict_current_choices, dict_current_enrollments, dict_offers_choices, formset, internships_offers):
    for offer, form in zip(internships_offers, formset):
        offer_choice = dict_current_choices.get((offer.organization.id, offer.speciality.id), None)
        offer_value = 0 if not offer_choice else offer_choice.choice
        offer_priority = False if not offer_choice else offer_choice.priority
        offer_enrollments = dict_current_enrollments.get(offer.id, [])
        number_first_choices = dict_offers_choices.get(offer.organization.id, 0)
        element = (offer, form, str(offer_value), offer_priority, offer_enrollments, number_first_choices)
        yield element


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def assign_speciality_for_internship(request, cohort_id, student_id, internship_id):
    speciality_id = None
    if request.method == "POST":
        speciality_form = SpecialityForm(request.POST)
        if speciality_form.is_valid():
            speciality_selected = speciality_form.cleaned_data["speciality"]
            speciality_id = speciality_selected.id
    return redirect("specific_internship_student_modification", cohort_id=cohort_id, student_id=student_id,
                    internship_id=internship_id, speciality_id=speciality_id)


def remove_previous_choices(student, internship):
    previous_choices = mdl_internship.internship_choice.search_by_student_or_choice(student=student, internship=internship)
    if previous_choices:
        previous_choices.delete()
    previous_enrollments = mdl_internship.internship_enrollment.search_by_student_and_internship(student=student, internship=internship)
    if previous_enrollments:
        previous_enrollments.delete()


def save_student_choices(formset, student, internship, speciality):
    for form in formset:
        if form.cleaned_data:
            offer_pk = form.cleaned_data["offer"]
            preference_value = int(form.cleaned_data["preference"])
            priority = form.cleaned_data['priority']
            offer = mdl_internship.internship_offer.find_by_pk(offer_pk)
            if has_been_selected(preference_value) and is_correct_speciality(offer, speciality):
                internship_choice = mdl_internship.internship_choice.InternshipChoice(student=student,
                                                                                      organization=offer.organization,
                                                                                      speciality=speciality,
                                                                                      choice=preference_value,
                                                                                      internship=internship,
                                                                                      priority=priority)
                internship_choice.save()
                save_enrollments(form, offer, student, internship)


def save_enrollments(form, offer, student, internship):
    periods_name = form.cleaned_data.get("periods", [])
    for period_name in periods_name:
        period = mdl_internship.period.get_by_name(period_name)
        if not period:
            continue
        enrollment = mdl_internship.internship_enrollment. \
            InternshipEnrollment(student=student, internship_offer=offer, place=offer.organization,
                                 period=period, internship=internship)
        enrollment.save()


def has_been_selected(preference_value):
    return bool(preference_value)


def is_correct_speciality(offer, speciality):
    return offer.speciality == speciality


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def edit_period_places(request, cohort_id, internship_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    internship_offer = get_object_or_404(InternshipOffer, pk=internship_id, cohort=cohort)
    period_places_values = get_current_period_places(internship_offer)
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
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    periods_dict = get_dict_of_periods()
    internship_offer = get_object_or_404(InternshipOffer, pk=internship_id, cohort=cohort)
    if not internship_offer:
        return redirect('edit_period_places', cohort_id=cohort.id, internship_id=internship_id)

    delete_previous_period_places(internship_offer)

    for period_name in periods_dict.keys():
        period_number_places = int(request.POST.get(period_name, 0))
        save_period_places_to_db(internship_offer, periods_dict[period_name], period_number_places)

    return redirect('edit_period_places', cohort_id=cohort.id, internship_id=internship_id)


def get_dict_of_periods():
    periods = mdl_internship.period.find_all()
    periods_dict = dict()
    for period in periods:
        periods_dict[period.name] = period
    return periods_dict


def get_dict_period_places(internship_offer):
    periods_places = mdl_internship.period_internship_places.find_by_internship_offer(internship_offer)
    periods_places_dict = dict()
    for period_place in periods_places:
        periods_places_dict[period_place.period.name] = period_place
    return periods_places_dict


def save_period_places_to_db(internship_offer, period, number_places):
    if number_places <= 0:
        return
    period_places = mdl_internship.period_internship_places.PeriodInternshipPlaces(
        period=period,
        internship_offer=internship_offer,
        number_places=number_places
    )
    period_places.save()


def delete_previous_period_places(internship_offer):
    mdl_internship.period_internship_places.find_by_internship_offer(internship_offer=internship_offer).delete()


def get_current_period_places(internship_offer):
    keys = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12']
    periods_places = get_dict_period_places(internship_offer)
    periods = []
    for key in keys:
        period_place = periods_places.get(key, None)
        number_places = 0
        if period_place:
            number_places = period_place.number_places
        periods.append((key, number_places))
    return periods


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_list(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    internships = Internship.objects.filter(cohort_id=cohort_id)
    context = {
        'cohort': cohort,
        'internships': internships,
    }
    return render(request, 'internship/list.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_new(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)

    inter = Internship(cohort_id=cohort_id)
    form = InternshipForm(request.POST or None, instance=inter)
    if form.is_valid():
        form.save()

        return redirect(reverse('internship-list', kwargs={
            'cohort_id': cohort.id,
        }))

    context = {
        'form': form,
        'page_title': _('create_internship'),
        'cohort': cohort,
    }
    return render(request, 'internship/internship_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_edit(request, cohort_id, internship_id):
    inter = get_object_or_404(Internship, pk=internship_id, cohort_id=cohort_id)
    cohort = get_object_or_404(Cohort, pk=cohort_id)

    form = InternshipForm(data=request.POST or None, instance=inter)

    if form.is_valid():
        form.cohort_id = cohort_id
        form.save()

        return redirect(reverse('internship-list', kwargs={
            'cohort_id': cohort.id,
        }))

    context = {
        'form': form,
        'page_title': _('edit_internship'),
        'cohort': cohort,
    }

    return render(request, 'internship/internship_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_delete(request, cohort_id, internship_id):
    inter = get_object_or_404(Internship, pk=internship_id, cohort_id=cohort_id)

    inter.delete()
    return redirect(reverse('internship-list', kwargs={
        'cohort_id': cohort_id,
    }))