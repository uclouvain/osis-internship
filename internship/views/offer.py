from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from base import models as mdl
from internship import models as mdl_internship
from internship.models.cohort import Cohort
from internship.views.internship import (get_all_organizations,
                                         get_all_specialities,
                                         get_number_choices, get_selectable,
                                         rebuild_the_lists,
                                         set_student_choices_list,
                                         set_tabs_name, sort_internships)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)

    # First get the value of the option's value for the sort
    if request.method == 'GET':
        organization_sort_value = request.GET.get('organization_sort')
        if request.GET.get('speciality_sort') != '0':
            speciality_sort_value = request.GET.get('speciality_sort')
        else :
            speciality_sort_value = None
    # Then select Internship Offer depending of the option
    if organization_sort_value and organization_sort_value != "0":
        query = mdl_internship.internship_offer.search(organization__name = organization_sort_value)
    else:
        query = mdl_internship.internship_offer.find_internships()

    # Sort the internships by the organization's reference
    query = sort_internships(query)

    # Get The number of differents choices for the internships
    get_number_choices(query)

    all_internships = mdl_internship.internship_offer.find_internships()
    all_organizations = get_all_organizations(all_internships)
    all_specialities = get_all_specialities(all_internships)
    set_tabs_name(all_specialities)
    all_non_mandatory_speciality = mdl_internship.internship_speciality.find_non_mandatory()
    if speciality_sort_value:
        all_non_mandatory_internships = mdl_internship.internship_offer.find_non_mandatory_internships(speciality__name=speciality_sort_value)
    else:
        all_non_mandatory_internships = mdl_internship.internship_offer.find_non_mandatory_internships(speciality__mandatory=0)
    get_number_choices(all_non_mandatory_internships)

    context = {
        'section': 'internship',
        'all_internships': query,
        'all_non_mandatory_internships': all_non_mandatory_internships,
        'all_organizations': all_organizations,
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
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    # Get the internship by its id
    internship = mdl_internship.internship_offer.find_intership_by_id(offer_id)
    # Get the students who have choosen this internship
    students = mdl_internship.internship_choice.search(organization=internship.organization,
                                                       speciality=internship.speciality)
    number_choices = [None]*5

    # Get the choices' number for this internship
    for index in range(1, 5):
        count = mdl_internship.internship_choice.search(
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
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    number_offers_selectable = mdl_internship.internship_offer.get_number_selectable(cohort_id)
    all_internship_offers = mdl_internship.internship_offer.find_all().filter(cohort_id=cohort_id)
    new_selectable_state = number_offers_selectable == 0

    for internship_offer in all_internship_offers:
        internship_offer.selectable = new_selectable_state
        internship_offer.save()

    return HttpResponseRedirect(reverse('internships_home', kwargs={
        'cohort_id': cohort.id,
    }))


@require_http_methods(['POST'])
@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_save(request, cohort_id):
    # Check if the internships are selectable, if yes students can save their choices
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    all_internships = mdl_internship.internship_offer.search(cohort_id=cohort_id)
    selectable = get_selectable(all_internships)

    if selectable :
        # Get the student
        student = mdl.student.find_by(person_username=request.user)
        # Delete all the student's choices for mandatory internships present in the DB
        mdl_internship.internship_choice.InternshipChoice.objects.filter(student=student, internship_choice=0).delete()

        #Build the list of the organizations and specialities get by the POST request
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
                mdl_internship.internship_choice.InternshipChoice.objects.filter(student=student, internship_choice=choice_tab).delete()

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

        rebuild_the_lists(preference_list, speciality_list, organization_list, internship_choice_tab)
        # Rebuild the lists deleting the null value
        organization_list = [x for x in organization_list if x != 0]
        speciality_list = [x for x in speciality_list if x != 0]
        preference_list = [x for x in preference_list if x != '0']
        internship_choice_tab = [x for x in internship_choice_tab if x != 0]

        if len(speciality_list) > 0:
            # Check if the student sent correctly send 4 choice.
            # If not, the choices are set to 0
            old_spec=speciality_list[0]
            new_spec=""
            index = 0
            cumul = 0
            for p in speciality_list:
                new_spec = p
                index += 1
                if old_spec == new_spec:
                    cumul += 1
                    old_spec = new_spec
                else :
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

        rebuild_the_lists(preference_list, speciality_list, organization_list, internship_choice_tab)
        # Rebuild the lists deleting the null value
        organization_list = [x for x in organization_list if x != 0]
        speciality_list = [x for x in speciality_list if x != 0]
        preference_list = [x for x in preference_list if x != '0']
        internship_choice_tab = [x for x in internship_choice_tab if x != 0]

        index = preference_list.__len__()

        # Save the new student's choices
        for x in range(0, index):
            new_choice = mdl_internship.internship_choice.InternshipChoice()
            new_choice.student = student[0]
            organization = mdl_internship.organization.search(reference=organization_list[x])
            new_choice.organization = organization[0]
            speciality = mdl_internship.internship_speciality.search(name=speciality_list[x])
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
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    # Get the student
    registration_id = request.POST.getlist('registration_id')
    student = mdl.student.find_by(registration_id=registration_id[0], full_registration = True)
    # Delete all the student's choices present in the DB
    mdl_internship.internship_choice.InternshipChoice.objects.filter(student=student).delete()
    mdl_internship.internship_enrollment.InternshipEnrollment.objects.filter(student=student).delete()

    #Build the list of the organizations and specialities get by the POST request
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

    all_internships = mdl_internship.internship_offer.find_internships()
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

    rebuild_the_lists(preference_list, speciality_list, organization_list)

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
    preference_list = [x for x in preference_list if x != '0']

    # Save the new choices
    index = final_preference_list.__len__()
    for x in range(0, index):
        new_choice = mdl_internship.internship_choice.InternshipChoice()
        new_choice.student = student[0]
        organization = mdl_internship.organization.search(reference=organization_list[x])
        new_choice.organization = organization[0]
        speciality = mdl_internship.internship_speciality.search(name=speciality_list[x])
        new_choice.speciality = speciality[0]
        new_choice.choice = final_preference_list[x]
        if final_fixthis_list[x] == '1':
            new_choice.priority = True
        else :
            new_choice.priority = False
        new_choice.save()

    # Save in the enrollement if the internships are fixed and a period is selected
    index = periods_list.__len__()
    for x in range(0, index):
        if periods_list[x] != '0':
            new_enrollment = mdl_internship.internship_enrollment.InternshipEnrollment()
            tab_period = periods_list[x].split('\\n')
            period = mdl_internship.period.search(name=tab_period[0])
            organization = mdl_internship.organization.search(reference=tab_period[1])
            speciality = mdl_internship.internship_speciality.search(name=tab_period[2])
            internship = mdl_internship.internship_offer.search(speciality__name = speciality[0], organization__reference = organization[0].reference)
            new_enrollment.student = student[0]
            new_enrollment.internship_offer = internship[0]
            new_enrollment.place = organization[0]
            new_enrollment.period = period[0]
            new_enrollment.save()

    redirect_url = reverse('internships_modification_student', args=[registration_id[0]])
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_stud(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    # Set the number of non mandatory internship and the sort array depending
    size_non_mandatory = 5
    speciality_sort_value = [None] * size_non_mandatory

    # Check if there is a speciality selected in a tab of non mandatory internship
    if request.method == 'GET':
        for x in range(1,size_non_mandatory):
            if request.GET.get("speciality_sort"+str(x)) != '0':
                speciality_sort_value[x] = request.GET.get("speciality_sort"+str(x))
            else :
                speciality_sort_value[x] = None

    # Get the student base on the user
    student = mdl.student.find_by(person_username=request.user)
    # Get in descending order the student's choices in first lines
    # FIXME: Add the cohort in the sort.
    student_choice = mdl_internship.internship_choice.find_by_student_desc(student)

    # Select all Internship Offer
    query = mdl_internship.internship_offer.find_internships()

    # Sort the internships by the organization's reference
    query = sort_internships(query)

    # Change the query into a list
    query = list(query)
    # Delete the internships in query when they are in the student's selection then rebuild the query
    # Put datas wich need to be save in the student's choice list
    query = set_student_choices_list(query, student_choice)
    # Insert the student choice into the global query, at first position,
    for choice in student_choice:
        query.insert(0, choice)

    # Get The number of differents choices for the internships
    get_number_choices(query)

    all_internships = mdl_internship.internship_offer.find_internships()
    all_speciality = get_all_specialities(all_internships)
    selectable = get_selectable(all_internships)
    set_tabs_name(all_speciality, student)

    # Set all non mandatory speciality for the dropdown list
    all_non_mandatory_speciality = mdl_internship.internship_speciality.find_non_mandatory()
    # Create an array of the number of non mandatory internship and put all the internship of the speciality selected in
    all_non_mandatory_internships = [None] * size_non_mandatory
    all_non_mandatory_selected_internships = [None] * size_non_mandatory
    for x in range(0,size_non_mandatory):
        if speciality_sort_value[x]:
            all_non_mandatory_internships[x] = mdl_internship.internship_offer.find_non_mandatory_internships(speciality__name=speciality_sort_value[x])
            get_number_choices(all_non_mandatory_internships[x])
            set_tabs_name(all_non_mandatory_internships[x])
        else:
            all_non_mandatory_internships[x] = None
        all_non_mandatory_selected_internships[x]=mdl_internship.internship_choice.search(internship_choice=x+1)

    context = {
        'section': 'internship',
        'all_internships': query,
        'non_mandatory_speciality': all_non_mandatory_speciality,
        'all_non_mandatory_internships': all_non_mandatory_internships,
        'all_non_mandatory_selected_internships': all_non_mandatory_selected_internships,
        'speciality_sort_value': speciality_sort_value,
        'all_speciality': all_speciality,
        'selectable': selectable,
        'cohort': cohort,
    }
    return render(request, "internships_stud.html", context)
