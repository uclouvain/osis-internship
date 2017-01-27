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
from django.http.response import HttpResponse
from django.http import JsonResponse

from base.models.person import *
import json

def get_persons(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        persons = Person.objects.filter(email__icontains = q )[:20]
        results = []
        for person in persons:
            person_json = person.email
            results.append(person_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def get_person_from_email(request, email):
    persons = search_by_email(email)
    person_json = []
    person_json.append({'id': persons[0].id,
                             'first_name': persons[0].first_name,
                             'last_name': persons[0].last_name,
                                  'email': persons[0].email
                                  })
    return JsonResponse({'person_json': person_json})
