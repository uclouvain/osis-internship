import urllib
from django.http import HttpResponse
from base.models import person
from backoffice.settings import PERSON_PHOTO_PATH,PERSON_PHOTO_PATH_DEFAULT,PERSON_PHOTO_PATH_DEFAULT_F,PERSON_PHOTO_PATH_DEFAULT_M
from django.contrib.auth.decorators import login_required


@login_required
def get_avatar(request, person_id):
    try:
        a_person = person.find_by_id(person_id)
    except:
        photo = urllib.request.urlopen(PERSON_PHOTO_PATH_DEFAULT, None, 1)
        return HttpResponse(photo, content_type="image/jpeg")
    if a_person and PERSON_PHOTO_PATH != '':
        try:
            photo = urllib.request.urlopen(get_photo_path(a_person), None, 1)
        except :
            photo = urllib.request.urlopen(get_default_avatar(person_id), None, 1)
    else:
        photo = urllib.request.urlopen(PERSON_PHOTO_PATH_DEFAULT, None, 1)
    return HttpResponse(photo, content_type="image/jpeg")

@login_required
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

@login_required
def get_default_avatar(person_id):
    try:
        a_person = person.find_by_id(person_id)
    except:
        return PERSON_PHOTO_PATH_DEFAULT
    if a_person.gender == "M":
        return PERSON_PHOTO_PATH_DEFAULT_M
    elif a_person.gender == "F":
        return PERSON_PHOTO_PATH_DEFAULT_F
    else:
        return PERSON_PHOTO_PATH_DEFAULT





