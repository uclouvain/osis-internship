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
from base.models import Structure, Organization
import json

@login_required
def institution(request):
    return render(request, "institution.html", {'section': 'institution'})


def structures(request):
    return render(request, "structures.html", {'init': "1"})


def structures_search(request):
    acronym = request.GET['acronym']
    title = request.GET['title']

    query = Structure.find_structures()

    if not acronym is None and len(acronym) > 0  :
        query = query.filter(acronym__icontains=acronym)
    if not title is None and len(title) > 0  :
        query = query.filter(title__icontains=title)

    return render(request, "structures.html", {'title': title,
                                               'acronym': acronym,
                                               'init': "0",
                                               'structures': query})


def structure_read(request,id):
    structure = Structure.find_by_id(id)
    return render(request, "structure.html", {'structure': structure})


def structure_read_by_acronym(request,name):
    print('structure_read_by_acronym',name)
    structure = Structure.find_by_acronym(name)
    print(structure)
    return render(request, "structure.html", {'structure': structure})


def structure_diagram(request, organization_id):
    print('structure_diagram')
    organization = Organization.find_by_id(organization_id)
    structure = organization.find_structure()
    tags =  organization.find_structure_tree()#Tree of structure
    data = json.dumps(tags)
    return render(request, "structure_organogram.html", {'structure': structure, 'data':data})


def structure_diagram_by_entitie(request,id):
    print('structure_diagram_by_structure')
    structure = Structure.find_by_id(id)
    # structure_parent = structure.part_of
    tags = structure.find_tree_by_structure()#Tree of structure
    data = json.dumps(tags)
    return render(request, "structure_organogram.html", {'structure': structure, 'data':data})
