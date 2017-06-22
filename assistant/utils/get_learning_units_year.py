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
from django.http import JsonResponse
from base.models.learning_unit_year import search


def get_learning_units_year(request):
    if request.is_ajax() and 'term' in request.GET:
        q = request.GET.get('term')
        learning_units_year = search(acronym=q)[:50]
        response_data = []
        for learning_unit_year in learning_units_year:
            response_data.append({'value': learning_unit_year.acronym,
                                  'title': learning_unit_year.title,
                                  'academic_year': str(learning_unit_year.academic_year),
                                  'id': learning_unit_year.id
                                  })
    else:
        response_data = []
    return JsonResponse(response_data, safe=False)
