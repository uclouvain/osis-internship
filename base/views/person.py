import base64
import urllib

from django.http import HttpResponse

from base.models import person
from backoffice.settings import PERSON_PHOTO_PATH


def get_avatar(request, person_id):
    a_person = person.find_by_id(person_id)
    photo = get_photo(a_person)
    return HttpResponse(photo, content_type="image/jpeg")


def get_photo(person):
    # Return JPG in Base64 format
    # return None if no valid data: global_id or no picture
    # for template use <img src="data:image/jpeg;base64,{{person.get_photo}}" class="avatar img-responsive"/>
    # timeout 1 sec with URLLIB request

    if person.get_photo_path():
        try:
            photo = urllib.request.urlopen(person.get_photo_path(), None, 1.0)
            photo_base64 = base64.b64encode(photo.read())
            return photo_base64
        except IOError:
            return None
    else:
        return None


def get_photo_path(person):
    if person.global_id and PERSON_PHOTO_PATH != '':
        try:
            global_id_str = str(person.global_id)
            photo_path = PERSON_PHOTO_PATH + 'image' + global_id_str[-4:-2] + "/" + global_id_str + '.jpg'
            return photo_path
        except IOError:
            return None
    else:
        return None