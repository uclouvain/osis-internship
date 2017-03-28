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
import urllib
from django.http import HttpResponse
from base.models import person
from backoffice.settings import PERSON_PHOTO_PATH
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static


@login_required
def get_avatar(request, person_id):
    try:
        a_person = person.find_by_id(person_id)
    except:
        photo = get_default_avatar(request)
        return HttpResponse(photo, content_type="image/jpeg")
    if a_person and PERSON_PHOTO_PATH != '':
        try:
            photo = urllib.request.urlopen(get_photo_path(a_person), None, 1)
        except:
            photo = get_default_avatar(request)
            return HttpResponse(photo, content_type="image/jpeg")
    else:
        photo = get_default_avatar(request)
    return HttpResponse(photo, content_type="image/jpeg")


@login_required
def get_photo_path(a_person):
    if a_person.global_id and PERSON_PHOTO_PATH != '':
        try:
            global_id_str = str(a_person.global_id)
            photo_path = PERSON_PHOTO_PATH + 'image' + global_id_str[-4:-2] + "/" + global_id_str + '.jpg'
            return photo_path
        except IOError:
            return None
    else:
        return None


@login_required
def get_default_avatar(request):
    return urllib.request.urlopen("http://" + request.get_host() + static('img/osis_person_unknown.png'), None, 1)
