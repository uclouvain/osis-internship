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
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from base import models as mdl
from internship import models as mdl_int
from internship.views.internship import get_all_specialities, set_tabs_name
from internship.utils.importing import import_offers


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def list_internships(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    organization_sort_value = None
    speciality_sort_value = None
    # First get the value of the option's value for the sort
    if request.method == 'GET':
        organization_sort_value = request.GET.get('organization_sort')
        if request.GET.get('speciality_sort') != '0':
            speciality_sort_value = request.GET.get('speciality_sort')

    # Then select Internship Offer depending of the option
    if organization_sort_value and organization_sort_value != "0":
        query = mdl_int.internship_offer.search(organization__name=organization_sort_value)
    else:
        query = mdl_int.internship_offer.find_internships()

    query = query.filter(organization__cohort=cohort)

    # Sort the internships by the organization's reference
    query = _sort_internships(query)

    # Get The number of different choices for the internships
    _get_number_choices(query)

    internships = mdl_int.internship.Internship.objects.filter(cohort=cohort)

    all_internships = mdl_int.internship_offer.find_internships().filter(organization__cohort=cohort)
    organizations = _get_all_organizations(all_internships)
    all_specialities = get_all_specialities(all_internships)
    set_tabs_name(all_specialities)
    all_non_mandatory_speciality = mdl_int.internship_speciality.find_non_mandatory()
    if speciality_sort_value:
        all_non_mandatory_internships = mdl_int.internship_offer.find_non_mandatory_internships(speciality__name=speciality_sort_value)
    else:
        all_non_mandatory_internships = mdl_int.internship_offer.find_non_mandatory_internships(speciality__mandatory=0)

    all_non_mandatory_internships = all_non_mandatory_internships.filter(organization__cohort=cohort)
    all_non_mandatory_speciality = all_non_mandatory_speciality.filter(cohort=cohort)

    _get_number_choices(all_non_mandatory_internships)

    context = {
        'section': 'internship',
        'all_internships': query,
        'internships': internships,
        'all_non_mandatory_internships': all_non_mandatory_internships,
        'organizations': organizations,
        'all_speciality': all_specialities,
        'organization_sort_value': organization_sort_value,
        'speciality_sort_value': speciality_sort_value,
        'non_mandatory_speciality': all_non_mandatory_speciality,
        'cohort': cohort,
    }
    return render(request, "internships.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_choice(request, cohort_id, offer_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    # Get the internship by its id
    # TODO: Check if this algo is ok
    internship = get_object_or_404(mdl_int.internship_offer.InternshipOffer, pk=offer_id, organization__cohort=cohort)
    # Get the students who have choosen this internship
    students = mdl_int.internship_choice.search(organization=internship.organization, speciality=internship.speciality)
    number_choices = [None]*5

    # Get the choices' number for this internship
    for index in range(1, 5):
        count = mdl_int.internship_choice.search(
            organization=internship.organization,
            speciality=internship.speciality,
            choice=index).count()

        number_choices[index] = count

    context = {
        'section': 'internship',
        'internship': internship,
        'students': students,
        'number_choices': number_choices,
        'cohort': cohort,
    }
    return render(request, "internship_detail.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_block(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)

    number_offers_selectable = mdl_int.internship_offer.get_number_selectable(cohort)
    all_internship_offers = mdl_int.internship_offer.find_all().filter(organization__cohort=cohort)

    new_selectable_state = number_offers_selectable == 0

    all_internship_offers.update(selectable=new_selectable_state)

    return HttpResponseRedirect(reverse('internships_home', kwargs={
        'cohort_id': cohort.id,
    }))


@require_http_methods(['POST'])
@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_save(request, cohort_id):
    # Check if the internships are selectable, if yes students can save their choices
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    all_internships = mdl_int.internship_offer.search(organization__cohort=cohort)
    selectable = _get_selectable(all_internships)

    if selectable:
        # Get the student
        student = mdl.student.find_by(person_username=request.user)
        # Delete all the student's choices for mandatory internships present in the DB
        mdl_int.internship_choice.InternshipChoice.objects.filter(student=student, internship_id=0).delete()

        # Build the list of the organizations and specialities get by the POST request
        organization_list = list()
        speciality_list = list()
        internship_choice_tab = []
        if request.POST.get('organization'):
            organization_list = request.POST.getlist('organization')
        if request.POST.get('speciality'):
            speciality_list = request.POST.getlist('speciality')
        if request.POST.getlist('is_choice'):
            internship_choice_tab = request.POST.getlist('is_choice')
            internship_choice_tab_del = list(set(internship_choice_tab))
            for choice_tab in internship_choice_tab_del:
                mdl_int.internship_choice.InternshipChoice.objects.filter(student=student,
                                                                          internship_choice=choice_tab).delete()

        all_specialities = get_all_specialities(all_internships)
        set_tabs_name(all_specialities)
        # Create an array with all the tab name of the speciality
        preference_list_tab = []
        for speciality in all_specialities:
            preference_list_tab.append('preference'+speciality.tab)

        # Create a list, for each element of the previous tab,
        # check if this element(speciality) is in the post request
        # If yes, add all the preference of the speciality in the list
        preference_list = list()
        for pref_tab in preference_list_tab:
            if request.POST.get(pref_tab):
                for pref in request.POST.getlist(pref_tab) :
                    preference_list.append(pref)

        _rebuild_the_lists(preference_list, speciality_list, organization_list, internship_choice_tab)
        # Rebuild the lists deleting the null value
        organization_list = [x for x in organization_list if x != 0]
        speciality_list = [x for x in speciality_list if x != 0]
        preference_list = [x for x in preference_list if x != '0']
        internship_choice_tab = [x for x in internship_choice_tab if x != 0]

        if len(speciality_list) > 0:
            # Check if the student sent correctly send 4 choice.
            # If not, the choices are set to 0
            old_spec=speciality_list[0]
            index = 0
            cumul = 0
            for p in speciality_list:
                new_spec = p
                index += 1
                if old_spec == new_spec:
                    cumul += 1
                    old_spec = new_spec
                else:
                    if cumul < 4:
                        cumul += 1
                        for i in range(index-cumul,index-1):
                            preference_list[i] = 0
                        cumul = 1
                    else :
                        cumul = 1
                    old_spec = new_spec
            if index < 4:
                for i in range(index-cumul,index):
                    preference_list[i] = 0
            else :
                if cumul != 4 :
                    for i in range(index-cumul,index):
                        if i < len(preference_list):
                            preference_list[i] = 0

        _rebuild_the_lists(preference_list, speciality_list, organization_list, internship_choice_tab)
        # Rebuild the lists deleting the null value
        organization_list = [x for x in organization_list if x != 0]
        speciality_list = [x for x in speciality_list if x != 0]
        preference_list = [x for x in preference_list if x != '0']
        internship_choice_tab = [x for x in internship_choice_tab if x != 0]

        index = preference_list.__len__()

        # Save the new student's choices
        for x in range(0, index):
            new_choice = mdl_int.internship_choice.InternshipChoice()
            new_choice.student = student[0]
            organization = mdl_int.organization.search(reference=organization_list[x])
            new_choice.organization = organization[0]
            speciality = mdl_int.internship_speciality.search(name=speciality_list[x])
            new_choice.speciality = speciality[0]
            new_choice.choice = preference_list[x]
            new_choice.internship_choice = internship_choice_tab[x]
            new_choice.priority = False
            new_choice.save()

    return HttpResponseRedirect(reverse('internships_stud', kwargs={
        'cohort_id': cohort.id,
    }))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_save_modification_student(request, cohort_id):
    # Get the student
    registration_id = request.POST.getlist('registration_id')
    student = mdl.student.find_by(registration_id=registration_id[0], full_registration = True)
    # Delete all the student's choices present in the DB
    mdl_int.internship_choice.InternshipChoice.objects.filter(student=student).delete()
    mdl_int.internship_enrollment.InternshipEnrollment.objects.filter(student=student).delete()

    # Build the list of the organizations and specialities get by the POST request
    organization_list = list()
    speciality_list = list()
    periods_list = list()
    fixthis_list = list()

    if request.POST.get('organization'):
        organization_list = request.POST.getlist('organization')
    if request.POST.get('speciality'):
        speciality_list = request.POST.getlist('speciality')
    if request.POST.get('periods_s'):
        periods_list = request.POST.getlist('periods_s')
    if request.POST.get('fixthis'):
        fixthis_list = request.POST.getlist('fixthis')

    all_internships = mdl_int.internship_offer.find_internships()
    all_specialities = get_all_specialities(all_internships)
    set_tabs_name(all_specialities)

    # Create an array with all the tab name of the speciality
    preference_list_tab = []
    for speciality in all_specialities:
        preference_list_tab.append('preference'+speciality.tab)

    # Create a list, for each element of the previous tab,
    # check if this element(speciality) is in the post request
    # If yes, add all the preference of the speciality in the list
    preference_list = list()
    for pref_tab in preference_list_tab:
        if request.POST.get(pref_tab):
            for pref in request.POST.getlist(pref_tab) :
                preference_list.append(pref)

    # If the fix checkbox is checked, the list receive '0', '1' as data
    # Delete the '0' value (the value before the '1', wich is required)
    index = 0
    for value in fixthis_list:
        if value == '1'and fixthis_list[index-1]=='0':
            del fixthis_list[index-1]
        index += 1

    _rebuild_the_lists(preference_list, speciality_list, organization_list)

    # Create the list of all preference and the internships fixed
    final_preference_list = list()
    final_fixthis_list = list()
    index = 0
    for p in preference_list:
        if p != '0':
            final_preference_list.append(p)
            final_fixthis_list.append(fixthis_list[index])
        index += 1

    # Rebuild the lists deleting the null value
    organization_list = [x for x in organization_list if x != 0]
    speciality_list = [x for x in speciality_list if x != 0]

    # Save the new choices
    index = final_preference_list.__len__()
    for x in range(0, index):
        new_choice = mdl_int.internship_choice.InternshipChoice()
        new_choice.student = student[0]
        organization = mdl_int.organization.search(reference=organization_list[x])
        new_choice.organization = organization[0]
        speciality = mdl_int.internship_speciality.search(name=speciality_list[x])
        new_choice.speciality = speciality[0]
        new_choice.choice = final_preference_list[x]
        if final_fixthis_list[x] == '1':
            new_choice.priority = True
        else:
            new_choice.priority = False
        new_choice.save()

    # Save in the enrollment if the internships are fixed and a period is selected
    index = periods_list.__len__()
    for x in range(0, index):
        if periods_list[x] != '0':
            new_enrollment = mdl_int.internship_enrollment.InternshipEnrollment()
            tab_period = periods_list[x].split('\\n')
            period = mdl_int.period.search(name=tab_period[0])
            organization = mdl_int.organization.search(reference=tab_period[1])
            speciality = mdl_int.internship_speciality.search(name=tab_period[2])
            internship = mdl_int.internship_offer.search(speciality__name=speciality[0],
                                                         organization__reference=organization[0].reference)
            new_enrollment.student = student[0]
            new_enrollment.internship_offer = internship[0]
            new_enrollment.place = organization[0]
            new_enrollment.period = period[0]
            new_enrollment.save()

    redirect_url = reverse('internships_modification_student', args=[registration_id[0]])
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def upload_offers(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    if request.method == 'POST':
        file_name = request.FILES['file']

        if file_name is not None:
            if ".xls" not in str(file_name):
                messages.add_message(request, messages.ERROR, _('file_must_be_xls'))
            else:
                import_offers.import_xlsx(file_name, cohort)

    return HttpResponseRedirect(reverse('internships', kwargs={'cohort_id': cohort.id}))


def _get_all_organizations(internships):
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


def _rebuild_the_lists(preference_list, speciality_list, organization_list, internship_choice_tab=None):
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


def _sort_internships(sort_internships):
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
    number_ref = sorted(number_ref, key=int)
    number_ref = _delete_dublons_keep_order(number_ref)
    for i in number_ref:
        internships = mdl_int.internship_offer.search(organization__reference=i)
        for internship in internships:
            tab.append(internship)
    return tab


def _get_number_choices(internships):
    """
        Set new variables for the param, the number of the first and other choice for one internship
        Params :
            internships : the internships we want to compute the number of choices
    """
    for internship in internships:
        number_first_choice = len(mdl_int.internship_choice.search(organization=internship.organization,
                                                                   speciality__acronym=internship.speciality.acronym,
                                                                   choice=1))
        number_other_choice = len(mdl_int.internship_choice.search_other_choices(organization=internship.organization,
                                                                                 speciality__acronym=internship.speciality.acronym))
        internship.number_first_choice = number_first_choice
        internship.number_other_choice = number_other_choice


def _delete_dublons_keep_order(seq):
    """
        Function to delete the dublons of any list and keep the order of the list.
        Param:
            seq : the list where there is dublons
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def _get_selectable(internships):
    """
        Function to check if the internships are selectable.
        Return the status of the first internship.
        If there is no internship, return True
    """
    if len(internships) > 0:
        return internships[0].selectable
    else:
        return True
