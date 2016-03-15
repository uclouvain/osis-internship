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
from internship.models import InternshipMaster

@login_required
def interships_masters(request):
    #First get the value of the 2 options for the sort
    if request.method == 'GET':
        spec_sort_get = request.GET.get('spec_sort')
        place_sort_get = request.GET.get('place_sort')

    #Then select Internship Master depending of the options
    #If both exist / if just speciality exist / if just Place exist / if none exist
    if spec_sort_get and spec_sort_get != "0":
        if place_sort_get and place_sort_get != "0":
            query = InternshipMaster.find_masters_by_spec_and_place(spec_sort_get, place_sort_get)
        else:
            query = InternshipMaster.find_masters_by_spec(spec_sort_get)
    else:
        if place_sort_get and place_sort_get != "0":
            query = InternshipMaster.find_masters_by_place(place_sort_get)
        else :
            query = InternshipMaster.find_masters()

    #Create the options for the selected list, delete dubblons
    query_master = InternshipMaster.find_masters()
    master_specs = []
    master_places = []
    for master in query_master:
        master_specs.append(master.speciality)
        master_places.append(master.organization)
    master_specs = list(set(master_specs))
    master_places = list(set(master_places))

    return render(request, "interships_masters.html", {'section': 'internship',
                                                        'all_masters': query, 'all_spec' : master_specs, 'all_places' : master_places,
                                                        'spec_sort_get':spec_sort_get, 'place_sort_get':place_sort_get})
