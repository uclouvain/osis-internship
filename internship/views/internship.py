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
from internship.models import InternshipOffer
from pprint import pprint

@login_required
def internships(request):
    #First get the value of the 2 options for the sort
    if request.method == 'GET':
        luy_sort_get = request.GET.get('luy_sort')
        place_sort_get = request.GET.get('place_sort')

    #Then select Internship Offer depending of the options
    #If both exist / if just LearningUnitYear exist / if just Place exist / if none exist
    if luy_sort_get and luy_sort_get != "0":
        if place_sort_get and place_sort_get != "0":
            query = InternshipOffer.find_internships_by_luy_and_place(luy_sort_get, place_sort_get)
        else:
            query = InternshipOffer.find_internships_by_luy(luy_sort_get)
    else:
        if place_sort_get and place_sort_get != "0":
            query = InternshipOffer.find_internships_by_place(place_sort_get)
        else :
            query = InternshipOffer.find_internships()

    #Create the options for the selected list, delete dubblons
    query_places = InternshipOffer.find_internships()
    internship_luy = []
    internship_places = []
    for internship in query_places:
        internship_luy.append(internship.learning_unit_year)
        internship_places.append(internship.organization)
    internship_luy = list(set(internship_luy))
    internship_places = list(set(internship_places))

    return render(request, "internships.html", {'section': 'internship', 'all_internships': query,
                                                'all_luy':internship_luy, 'all_places':internship_places,
                                                'luy_sort_get':luy_sort_get, 'place_sort_get':place_sort_get})
