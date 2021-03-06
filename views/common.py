##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import math

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import gettext_lazy as _

PAGINATOR_SIZE_LIST = [10, 25, 50, 100]


def display_errors(request, errors):
    for error in errors:
        for key, value in error.items():
            messages.add_message(request, messages.ERROR, "{} : {}".format(_(key), value[0]), "alert-danger")


def display_report_errors(request, errors):
    for error in errors:
        for key, value in error.items():
            key = key.replace("report_", "")
            add_report_message(key, request, value)


def add_report_message(key, request, value):
    if (key == "__all__"):
        messages.add_message(request, messages.ERROR, "{}".format(value[0]), "alert-danger")
    else:
        messages.add_message(request, messages.ERROR, "{} : {}".format(_(key), value[0]), "alert-danger")


def get_object_list(request, objects):
    store_paginator_size(request)
    size = get_paginator_size(request)
    if objects is None:
        objects = []
    paginator = Paginator(objects, size)
    page = request.GET.get('page')

    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
    return object_list


def store_paginator_size(request):
    if 'paginator_size' in request.GET:
        request.session['paginator_size'] = request.session.setdefault('paginator_size', {})
        request.session['paginator_size'].update({request.path: request.GET.get('paginator_size')})


def get_paginator_size(request):
    if 'paginator_size' in request.session and request.path in request.session['paginator_size']:
        return request.session.get('paginator_size')[request.path]
    elif 'paginator_size' in request.GET:
        return request.GET.get('paginator_size')
    else:
        return PAGINATOR_SIZE_LIST[0]


def round_half_up(n):
    return int(math.floor(n + 0.5))
