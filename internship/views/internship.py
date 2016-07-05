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
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from internship.models import InternshipEnrollment, InternshipOffer, InternshipChoice, Organization, Period, InternshipSpeciality
from internship.forms import InternshipChoiceForm, InternshipOfferForm
from base import models as mdl
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict

import urllib.request
import unicodedata
from xml.dom import minidom
from math import sin, cos, radians, degrees, acos


def geocode(addr):
    lat_long = [None]*2
    # Transform the address for a good url and delete all accents
    addr = addr.replace(" ", "+")
    addr = addr.replace("'", "\'")
    addr = strip_accents(addr)
    # get the complete url
    url = "https://maps.googleapis.com/maps/api/geocode/xml?address=%s&key=AIzaSyCWeZdraxzqRTMxXxbXY3bncaD6Ijq_EvE" % addr

    # using urllib get the xml
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')

    # Parse the xml to have the latitude and longitude of the address
    xmldoc = minidom.parseString(data)
    lat = xmldoc.getElementsByTagName('location')
    for l in lat:
        c = l.getElementsByTagName('lat')[0].firstChild.data
        d = l.getElementsByTagName('lng')[0].firstChild.data
        lat_long[0] = c
        lat_long[1] = d
    # return the value
    return lat_long


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def calc_dist(lat_a, long_a, lat_b, long_b):
    lat_a = radians(float(lat_a))
    lat_b = radians(float(lat_b))
    long_a = float(long_a)
    long_b = float(long_b)
    long_diff = radians(long_a - long_b)
    distance = (sin(lat_a) * sin(lat_b) +
                cos(lat_a) * cos(lat_b) * cos(long_diff))
    # for distance in miles use this
    # return (degrees(acos(distance)) * 69.09)
    # for distance in kilometers use this
    return (degrees(acos(distance)) * 69.09)/0.621371


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships(request):
    # First get the value of the option's value for the sort
    if request.method == 'GET':
        organization_sort_value = request.GET.get('organization_sort')

    # Then select Internship Offer depending of the option
    if organization_sort_value and organization_sort_value != "0":
        query = InternshipOffer.find_interships_by_organization(organization_sort_value)
    else:
        query = InternshipOffer.find_internships()

    for internship in query:
        number_first_choice = len(InternshipChoice.find_by(internship.organization, internship.speciality,
                                                           s_choice=1))
        number_other_choice = len(InternshipChoice.find_by(internship.organization, internship.speciality,
                                                           s_choice=2))
        internship.number_first_choice = number_first_choice
        internship.number_other_choice = number_other_choice

    # Create the options for the selected list, delete duplicated
    query_organizations = InternshipOffer.find_internships()
    internship_organizations = []
    internship_speciality = []
    for internship in query_organizations:
        internship_organizations.append(internship.organization)
        internship_speciality.append(internship.speciality)
    internship_organizations = list(set(internship_organizations))
    internship_speciality = list(OrderedDict.fromkeys(internship_speciality))
    for luy in internship_speciality:
        tab = luy.name.replace(" ", "")
        luy.tab = tab

    return render(request, "internships.html", {'section':                  'internship',
                                                'all_internships':          query,
                                                'all_organizations':        internship_organizations,
                                                'all_speciality':           internship_speciality,
                                                'organization_sort_value':  organization_sort_value, })


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def internships_stud(request):
    student = mdl.student.find_by(person_username=request.user)
    # get in order descending to have the first choices in first lines in the insert (line 114)
    student_choice = InternshipChoice.find_by_student_desc(student)
    # First get the value of the option's value for the sort
    if request.method == 'GET':
        organization_sort_value = request.GET.get('organization_sort')

    # Then select Internship Offer depending of the option
    if organization_sort_value and organization_sort_value != "0":
        query = InternshipOffer.find_interships_by_organization(organization_sort_value)
    else:
        query = InternshipOffer.find_internships()

    # Change the query into a list
    query = list(query)
    # delete the internships in query when they are in the student's selection then rebuild the query
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

    # insert the student choice into the global query, at first position,
    # if they are in organization_sort_value (if it exist)
    for choice in student_choice:
        if organization_sort_value and organization_sort_value != "0":
            if choice.organization.name == organization_sort_value:
                query.insert(0, choice)
        else:
            query.insert(0, choice)

    for internship in query:
        number_first_choice = len(InternshipChoice.find_by(internship.organization, internship.speciality,
                                                           s_choice=1))
        internship.number_first_choice = number_first_choice

    # Create the options for the selected list, delete duplicated
    query_organizations = InternshipOffer.find_internships()
    internship_organizations = []
    for internship in query_organizations:
        internship_organizations.append(internship.organization)
    internship_organizations = list(set(internship_organizations))

    all_internships = InternshipOffer.find_internships()
    all_speciality = []
    for choice in all_internships:
        all_speciality.append(choice.speciality)
    all_speciality = list(OrderedDict.fromkeys(all_speciality))
    for luy in all_speciality:
        size = len(InternshipChoice.find_by(s_speciality=luy, s_student=student))
        luy.size = size
        tab = luy.name.replace(" ", "")
        luy.tab = tab

    if len(query) > 0 :
        if query[0].selectable:
            selectable = True
        else :
            selectable = False
    else :
        selectable = True

    return render(request, "internships_stud.html", {'section': 'internship',
                                                'all_internships' : query,
                                                'all_organizations' : internship_organizations,
                                                'organization_sort_value' : organization_sort_value,
                                                'all_speciality' : all_speciality,
                                                'selectable' : selectable,
                                                 })


@login_required
def internships_save(request):
    internships = InternshipOffer.find_internships()
    if len(internships) > 0:
        if internships[0].selectable:
            selectable = True
        else:
            selectable = False
    else:
        selectable = True

    if selectable :
        student = mdl.student.find_by(person_username=request.user)
        InternshipChoice.objects.filter(student=student).delete()

        form = InternshipChoiceForm(data=request.POST)
        preference_list = list()
        if request.POST['organization']:
            organization_list = request.POST.getlist('organization')

        if request.POST['speciality']:
            speciality_list = request.POST.getlist('speciality')

        all_internships = InternshipOffer.find_internships()
        all_speciality = []
        for choice in all_internships:
            all_speciality.append(choice.speciality)

        all_speciality = list(OrderedDict.fromkeys(all_speciality))
        for luy in all_speciality :
            tab = luy.name.replace(" ", "")
            luy.tab = tab

        preference_list_tab = []
        for luy in all_speciality:
            preference_list_tab.append('preference'+luy.tab)

        preference_list= list()
        for pref_tab in preference_list_tab:
            if request.POST[pref_tab]:
                for pref in request.POST.getlist(pref_tab) :
                    preference_list.append(pref)

        index = 0
        for r in preference_list:
            if r == "0":
                speciality_list[index] = 0
                organization_list[index] = 0
            index += 1

        organization_list = [x for x in organization_list if x != 0]
        speciality_list = [x for x in speciality_list if x != 0]
        preference_list = [x for x in preference_list if x != '0']

        if len(speciality_list) > 0:
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
                        preference_list[i] = 0

        index = 0
        for r in preference_list:
            if r == 0:
                speciality_list[index] = 0
                organization_list[index] = 0
            index += 1

        organization_list = [x for x in organization_list if x != 0]
        speciality_list = [x for x in speciality_list if x != 0]
        preference_list = [x for x in preference_list if x != 0]

        index = preference_list.__len__()

        for x in range(0, index):
            new_choice = InternshipChoice()
            new_choice.student = student[0]
            organization = Organization.search(reference=organization_list[x])
            new_choice.organization = organization[0]
            speciality = InternshipSpeciality.find_by(name=speciality_list[x])
            new_choice.speciality = speciality[0]
            new_choice.choice = preference_list[x]
            new_choice.priority = False
            new_choice.save()

    return HttpResponseRedirect(reverse('internships_stud'))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_create(request):
    # Select all the organisation (service partner)
    organizations = Organization.find_all_order_by_reference()

    # select all the speciality which contain the word stage
    speciality = InternshipSpeciality.find_all()

    # Send them to the page
    return render(request, "internships_create.html", {'section':                   'internship',
                                                       'all_speciality':            speciality,
                                                       'all_organization':          organizations, })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_new(request):
    return internships_edit(request, None)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_edit(request, internship_id):
    success = 0
    check_internship = 0
    form = InternshipOfferForm(data=request.POST)

    organization = Organization.search(reference=request.POST['organization'])
    speciality = InternshipSpeciality.find_by(name=request.POST['speciality'])

    if internship_id:
        internship = InternshipOffer.find_intership_by_id(internship_id)
    else:
        internship = InternshipOffer()
        check_internship = len(InternshipOffer.find_interships_by_learning_unit_organization(speciality[0].name,
                                                                                             request.POST['organization']))

    if check_internship == 0:
        if request.POST['organization']:
            internship.organization = organization[0]

        if request.POST['speciality']:
            internship.speciality = speciality[0]
            internship.title = speciality[0].name

        if request.POST['maximum_enrollments']:
            internship.maximum_enrollments = request.POST['maximum_enrollments']

        internship.selectable = True
        internship.save()
        success = 1
        if internship_id:
            message = "%s" % _('Stage correctement modifié ! Vous pouvez cliquer sur le bouton Retour')
            organization_related = organization[0]
        else:
            message = "%s" % _('Stage correctement créé !')
            organization_related = None

    else:
        message = "%s" % _('Ce stage pour cet hôpital existe déjà !')

    # Select all the organisation (service partner)
    organizations = Organization.find_all_order_by_reference()
    # select all the speciality which contain the word stage
    speciality = InternshipSpeciality.find_all()

    # Send them to the page
    return render(request, "internships_create.html", {'section':                   'internship',
                                                       'all_speciality':            speciality,
                                                       'all_organization':          organizations,
                                                       'select_organization':       organization[0].reference,
                                                       'select_speciality': speciality[0].name,
                                                       'message':                   message,
                                                       'success':                   success,
                                                       'organization_related':      organization_related, })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_choice(request, id):
    internship = InternshipOffer.find_intership_by_id(id)
    students = InternshipChoice.find_by(s_organization=internship.organization,
                                        s_speciality=internship.speciality)
    number_choices = [None]*5

    for index in range(1, 5):
        number_choices[index] = len(InternshipChoice.find_by(s_organization=internship.organization,
                                                             s_speciality=internship.speciality,
                                                             s_define_choice=index))

    return render(request, "internship_detail.html", {'section':        'internship',
                                                      'internship':     internship,
                                                      'students':       students,
                                                      'number_choices': number_choices, })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_modification(request, internship_id):
    internship = InternshipOffer.find_intership_by_id(internship_id)
    organization_sorted = request.POST['organization_sort']
    return render(request, "internship_modification.html", {'internship':           internship,
                                                            'internship_id':        internship_id,
                                                            'organization_sorted':  organization_sorted, })


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_block(request, block):
    internships = InternshipOffer.find_internships()

    for internship in internships:
        edit_internship = InternshipOffer.find_intership_by_id(internship.id)
        edit_internship.organization = internship.organization
        edit_internship.speciality = internship.speciality
        edit_internship.title = internship.title
        edit_internship.maximum_enrollments = internship.maximum_enrollments
        if block == '1':
            edit_internship.selectable = False
        else:
            edit_internship.selectable = True
        edit_internship.save()

    return HttpResponseRedirect(reverse('internships_home'))

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_modification_student(request, registration_id):
    student = mdl.student.find_by(registration_id=registration_id, full_registration = True)
    #get in order descending to have the first choices in first lines in the insert (line 114)
    student_choice = InternshipChoice.find_by_student_desc(student)
    #First get the value of the option's value for the sort
    if request.method == 'GET':
        organization_sort_value = request.GET.get('organization_sort')

    #Then select Internship Offer depending of the option
    if organization_sort_value and organization_sort_value != "0":
        query = InternshipOffer.find_interships_by_organization(organization_sort_value)
    else :
        query = InternshipOffer.find_internships()

    #Change the query into a list
    query=list(query)
    #delete the internships in query when they are in the student's selection then rebuild the query
    index = 0
    for choice in student_choice:
        for internship in query :
            if internship.organization == choice.organization and \
                internship.speciality == choice.speciality :
                    choice.maximum_enrollments =  internship.maximum_enrollments
                    choice.selectable =  internship.selectable
                    query[index] = 0
            index += 1
        query = [x for x in query if x != 0]
        index = 0
    query = [x for x in query if x != 0]

    #insert the student choice into the global query, at first position,
    #if they are in organization_sort_value (if it exist)
    for choice in student_choice :
        if organization_sort_value and organization_sort_value != "0" :
            if choice.organization.name == organization_sort_value :
                query.insert(0,choice)
        else :
            query.insert(0,choice)

    for internship in query:
        number_first_choice = len(InternshipChoice.find_by(internship.organization, internship.speciality, s_choice = 1))
        internship.number_first_choice = number_first_choice

    # Create the options for the selected list, delete duplicated
    query_organizations = InternshipOffer.find_internships()
    internship_organizations = []
    for internship in query_organizations:
        internship_organizations.append(internship.organization)
    internship_organizations = list(set(internship_organizations))

    all_internships = InternshipOffer.find_internships()
    all_speciality = []
    for choice in all_internships:
        all_speciality.append(choice.speciality)
    all_speciality = list(set(all_speciality))
    for luy in all_speciality :
        size = len(InternshipChoice.find_by(s_speciality=luy, s_student=student))
        luy.size = size
        tab = luy.name.replace(" ", "")
        luy.tab = tab

    periods = Period.find_all()

    return render(request, "internship_modification_student.html", {'section': 'internship',
                                                'all_internships' : query,
                                                'all_organizations' : internship_organizations,
                                                'organization_sort_value' : organization_sort_value,
                                                'all_speciality' : all_speciality,
                                                'periods' : periods,
                                                'registration_id':registration_id,
                                                'student' : student[0],
                                                 })

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_save_modification_student(request) :
    if request.POST['organization']:
        organization_list = request.POST.getlist('organization')

    if request.POST['speciality']:
        speciality_list = request.POST.getlist('speciality')

    all_internships = InternshipOffer.find_internships()
    all_speciality = []
    for choice in all_internships:
        all_speciality.append(choice.speciality)
    all_speciality = list(set(all_speciality))
    for luy in all_speciality :
        tab = luy.name.replace(" ", "")
        luy.tab = tab

    preference_list_tab = []
    for luy in all_speciality:
        preference_list_tab.append('preference'+luy.tab)

    preference_list= list()
    for pref_tab in preference_list_tab:
        if request.POST[pref_tab]:
            for pref in request.POST.getlist(pref_tab) :
                preference_list.append(pref)

    if request.POST['periods_s']:
        periods_list = request.POST.getlist('periods_s')

    if request.POST.get('fixthis'):
        fixthis_list = request.POST.getlist('fixthis')
    index = 0
    fixthis_final_list = []
    for value in fixthis_list:
        if value == '1'and fixthis_list[index-1]=='0':
            del fixthis_list[index-1]
        index += 1

    index = 0
    for r in preference_list:
        if r == "0":
            speciality_list[index] = 0
            organization_list[index] = 0
        index += 1

    registration_id = request.POST.getlist('registration_id')
    student = mdl.student.find_by(registration_id=registration_id[0], full_registration = True)
    organization_list = [x for x in organization_list if x != 0]
    speciality_list = [x for x in speciality_list if x != 0]
    preference_list = [x for x in preference_list if x != '0']
    periods_list = [x for x in periods_list if x != '0']

    InternshipChoice.objects.filter(student=student).delete()
    index = preference_list.__len__()
    for x in range(0, index):
        new_choice = InternshipChoice()
        new_choice.student = student[0]
        organization = Organization.search(reference=organization_list[x])
        new_choice.organization = organization[0]
        speciality = InternshipSpeciality.find_by(name=speciality_list[x])
        new_choice.speciality = speciality[0]
        new_choice.choice = preference_list[x]
        if fixthis_list[x] == '1':
            new_choice.priority = True
        else :
            new_choice.priority = False
        new_choice.save()

    index = periods_list.__len__()
    InternshipEnrollment.objects.filter(student=student).delete()
    for x in range(0, index):
        if periods_list[x] != '0':
            new_enrollment = InternshipEnrollment()
            tab_period = periods_list[x].split('\\n')
            period = Period.find_by(name=tab_period[0])
            organization = Organization.search(reference=tab_period[1])
            speciality = InternshipSpeciality.find_by(name=tab_period[2])
            internship = InternshipOffer.find_interships_by_learning_unit_organization(speciality[0].name, organization[0].reference)
            new_enrollment.student = student[0]
            new_enrollment.internship_offer = internship[0]
            new_enrollment.place = organization[0]
            new_enrollment.period = period[0]
            new_enrollment.save()

    redirect_url = reverse('internships_modification_student', args=[registration_id[0]])
    return HttpResponseRedirect(redirect_url)
