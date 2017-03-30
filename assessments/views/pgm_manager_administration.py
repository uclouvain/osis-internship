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
import traceback
from collections import defaultdict
from decimal import Decimal, Context, Inexact
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as trans
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as PsycopInterfaceError
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from base import models as mdl
from assessments import models as mdl_assess
from base.enums.exam_enrollment_justification_type import JUSTIFICATION_TYPES
from attribution import models as mdl_attr
from reference import models as mdl_ref
from osis_common.document import paper_sheet
from base.utils import send_mail
from assessments.views import export_utils
from base.views import layout
import json
from osis_common.models.queue_exception import QueueException
import logging
from django.conf import settings
from django.db import connection
from reference.enums import grade_type_coverage
from base.enums import structure_type
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


@login_required
def pgm_manager_administration(request):
    faculty = find_faculty('ESPO')

    return layout.render(request, "admin/pgm_manager.html", {
        'manager_entity': faculty,
        'entity': faculty,
        'entities': ['1', '2'],
        'pgm_types': mdl_ref.grade_type.find_by_coverage(grade_type_coverage.UNIVERSITY),
        'managers': mdl.program_manager.find_by_faculty(faculty)})


@login_required
def pgm_manager_search(request):
    faculty = find_faculty('ESPO')
    entity = request.GET.get('entity', None)
    entity_list=[]
    if entity == "-":
        entity_list =  list(mdl.structure.search(entity,None,structure_type.FACULTY))
    else:
        entity_list.append(mdl.structure.search(entity,None,None).first())
        #entity_list.append("COMU")
    pgm_type = request.GET.get('pgm_type', None)
    if pgm_type == "-":
        pgm_type=None

    manager = request.GET.get('manager', None)
    academic_yr = mdl.academic_year.current_academic_year()
    # pgms = mdl.offer_year.search(entity, academic_yr, None)
    pgms = mdl.offer_year.search_offers(entity_list, academic_yr, pgm_type)

    # managers = mdl.program_manager.find_by_offer_year(pgm)
    managers = None
    return layout.render(request, "admin/pgm_manager.html", {
        'manager_entity': faculty,
        'entity': entity,
        'entities': ['1', '2'],
        'pgm_types': mdl_ref.grade_type.find_by_coverage(grade_type_coverage.UNIVERSITY),
        'pgms': pgms,
        'managers': managers})


@login_required
def remove_manager(request):
    pgms_to_be_removed = request.POST['pgms_to_be_removed']
    person_to_be_removed = request.POST['person_to_be_removed']
    print(pgms_to_be_removed)
    list_pgms_concerned = pgms_to_be_removed.split(",")
    offers = mdl.offer_year.find_by_id_list(list_pgms_concerned)

    pgm_manager_to_delete = mdl.program_manager.find_by_offer_year_list_person(person_to_be_removed, offers)
    for p in pgm_manager_to_delete:
        mdl.program_manager.delete_by_id(p.id)

    return HttpResponseRedirect(reverse('pgm_manager_search'))


@login_required
def manager_form(request):
    list_offer_id = []
    for k, v in request.POST.items():
        if k.startswith('pgm_id_'):
            list_offer_id.append(v)
    return layout.render(request, "admin/persons.html", {'pgms_id': list_offer_id})


def find_faculty(acronym):
    faculties = mdl.structure.search(acronym, None, structure_type.FACULTY)
    if faculties:
        return faculties.first()
    return None


@login_required
def person_search(request):
    list_offer_id = request.GET['pgms_id']
    name = request.GET['name']
    persons = mdl.person.find_by_last_name(name)
    return layout.render(request, "admin/persons.html", {'pgms_id': list_offer_id, 'persons': persons})


@login_required
def add_manager(request):
    person_id = request.POST['person_id']
    person = mdl.person.find_by_id(person_id)
    pgms_id = request.POST['pgms_id']

    list_offer_id = convertToList(pgms_id)

    if person:
        for offer_id in list_offer_id:
            offer_yr = mdl.offer_year.find_by_id(int(offer_id))
            pgm_manage = mdl.program_manager.ProgramManager()
            pgm_manage.person = person
            pgm_manage.offer_year = offer_yr
            pgm_manage.save()

    return HttpResponseRedirect(reverse('pgm_manager_search'))


def convertToList(pgms_id):
    pgms_id = pgms_id.replace("[", "")
    pgms_id = pgms_id.replace("]", "")
    pgms_id = pgms_id.replace("'", "")
    list_offer_id = pgms_id.split(",")
    return list_offer_id


# @login_required
def update_managers_list_old(request):

    pgm_ids = request.GET['pgm_ids']
    list_offer_id = convertToList(pgm_ids)
    managers = mdl.program_manager.find_by_offer_year_list(list_offer_id)
    persons = []
    for m in managers:
        if m.person not in persons:
            persons.append(m.person)

    serializer = ProgramManagerSerializer(managers, many=True)
    return JSONResponse(serializer.data)


def manager_pgm_list(request):
    print('manager_pgm_list')
    manager_id = request.GET['manager_id']
    print(manager_id)
    manager = mdl.program_manager.find_by_id(int(manager_id))
    offers = []
    if manager:
        pgm_managers = mdl.program_manager.find_by_person(manager.person)
        for p in pgm_managers:
            if p.offer_year not in offers:
                offers.append(p.offer_year)
    serializer = OfferYearSerializer(offers, many=True)
    return JSONResponse(serializer.data)


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = mdl.person.Person
        fields = '__all__'


class OfferYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = mdl.offer_year.OfferYear
        fields = '__all__'


class ProgramManagerSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    offer_year = OfferYearSerializer()

    class Meta:
        model = mdl.program_manager.ProgramManager
        fields = '__all__'


class PgmManager(object):

    def __init__(self, person_id, person_last_name, person_first_name, offer_year_acronyms_on, offer_year_acronyms_off,
                 programs):
        self.person_id = person_id
        self.person_last_name = person_last_name
        self.person_first_name = person_first_name
        self.offer_year_acronyms_on = offer_year_acronyms_on
        self.offer_year_acronyms_off = offer_year_acronyms_off
        self.programs = programs


class PgmManagerSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    person_last_name = serializers.CharField()
    person_first_name = serializers.CharField()
    offer_year_acronyms_on = serializers.CharField()
    offer_year_acronyms_off = serializers.CharField()
    programs = serializers.CharField()


def update_managers_list(request):
    pgm_ids = request.GET['pgm_ids']
    list_offer_id = convertToList(pgm_ids)
    managers = mdl.program_manager.find_by_offer_year_list(list_offer_id)
    managers_distinct = []
    persons = []
    pgmManagers = []

    for m in managers:
        if m.person not in persons:
            persons.append(m.person)
            acronyms_off_list = []
            acronyms_off = ""
            pgms = ""
            offers = []

            for s in list_offer_id:

                of = mdl.offer_year.find_by_id(int(s))
                mg = mdl.program_manager.find_by_offer_year_list_person(m.person, [of])
                if mg:
                    if acronyms_off == "":
                        acronyms_off = "{0}".format(of.acronym)
                    else:
                        acronyms_off = "{0}, {1}".format(acronyms_off, of.acronym)
                    if pgms == "":
                        pgms = of.id
                    else:
                        pgms = "{0}, {1}".format(pgms, of.id)
                    offers.append(of)
                    acronyms_off_list.append(acronyms_off)

            acronyms_pgm_to_manage = pgm_to_keep_managing(m.person, offers)
            pp = PgmManager(person_id=m.person.id,
                            person_last_name=m.person.last_name,
                            person_first_name=m.person.first_name,
                            offer_year_acronyms_on=acronyms_pgm_to_manage,
                            offer_year_acronyms_off=acronyms_off,
                            programs=pgms)

            pgmManagers.append(pp)

    serializer = PgmManagerSerializer(pgmManagers, many=True)
    return JSONResponse(serializer.data)


def pgm_to_keep_managing(a_person, offers):
    list_program_manager_to_keep = mdl.program_manager.find_by_person_exclude_offer_list(a_person, offers)
    ch = ""
    for program_manager_to_keep in list_program_manager_to_keep:
        if ch == "":
            ch = program_manager_to_keep.offer_year.acronym
        else:
            ch = "{0}, {1}".format(ch, program_manager_to_keep.offer_year.acronym)
    return ch

