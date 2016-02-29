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

from base import models as mdl


@login_required
def institution(request):
    return render(request, "institution.html", {'section': 'institution'})


def structures(request):
    return render(request, "structures.html", {'init': "1"})


def structures_search(request):
    acronym = request.GET['acronym']
    title = request.GET['title']

    query = mdl.structure.find_structures()

    if not acronym is None and len(acronym) > 0  :
        query = query.filter(acronym__icontains=acronym)
    if not title is None and len(title) > 0  :
        query = query.filter(title__icontains=title)

    return render(request, "structures.html", {'title': title,
                                               'acronym': acronym,
                                               'init': "0",
                                               'structures': query})


def structure_read(request,id):
    structure = mdl.structure.find_structure_by_id(id)
    offers_years = mdl.offer_year.find_offer_years_by_structure(structure)
    return render(request, "structure.html", {'structure': structure,
                                              'offers_years': offers_years})
