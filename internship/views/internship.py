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
from django.contrib.auth.decorators import login_required
from internship.models import InternshipOffer, InternshipChoice
from internship.forms import InternshipChoiceForm
from pprint import pprint

@login_required
def internships(request):
    #First get the value of the option's value for the sort
    if request.method == 'GET':
        organization_sort_value = request.GET.get('organization_sort')

    #Then select Internship Offer depending of the option
        if organization_sort_value and organization_sort_value != "0":
            query = InternshipOffer.find_interships_by_organization(organization_sort_value)
        else :
            query = InternshipOffer.find_internships()

    #Create the options for the selected list, delete dubblons
    query_organizations = InternshipOffer.find_internships()
    internship_organizations = []
    for internship in query_organizations:
        internship_organizations.append(internship.organization)
    internship_organizations = list(set(internship_organizations))

    return render(request, "internships.html", {'section': 'internship',
                                                'all_internships': query,
                                                'all_organizations':internship_organizations,
                                                'organization_sort_value':organization_sort_value})

@login_required
def internships_save(request):
    form = InternshipChoiceForm(data=request.POST)
    if request.POST['learning_unit_year']:
        learning_unit_year_list = request.POST.getlist('learning_unit_year')
        print(learning_unit_year_list)

    if request.POST['organization']:
        organization_list = request.POST.getlist('organization')
        print(organization_list)

    if request.POST['preference']:
        preference_list = request.POST.getlist('preference')
        print(preference_list)


    print(request.user)

    return render(request, "internships.html", {'section': 'internship',
                                                'form': form
                                                #'all_internships': query,
                                                #'all_organizations':internship_organizations,
                                                #'organization_sort_value':organization_sort_value
                                                })
