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
from django.contrib.auth.decorators import login_required, permission_required
from base import models as mdl
from reference import models as mdl_ref
from base.views import layout
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import json
from django.utils import timezone

ALL_OPTION_VALUE = "-"


@login_required
def pgm_manager_administration(request):
    entity_managed = get_administrator_faculty(request.user)
    current_academic_yr = mdl.academic_year.current_academic_year()
    return layout.render(request, "admin/pgm_manager.html", {
        'academic_year': current_academic_yr,
        'person': None,
        'manager_entity': entity_managed,
        'entity': entity_managed,
        'entities': get_managed_entities(entity_managed),
        'offer_types': get_offer_types(),
        'managers': get_entity_program_managers(entity_managed, current_academic_yr)})


@login_required
def pgm_manager_search(request):
    person_id = get_filter_value(request, 'person')
    person = None
    if person_id:
        person = mdl.person.find_by_id(person_id)
    return pgm_manager_form(None, None, request, person)


def pgm_manager_form(offers_on, error_messages, request, manager_person):
    entity = get_filter_value(request, 'entity')
    pgm_offer_type = get_filter_value(request, 'offer_type')

    entity_managed = get_administrator_faculty(request.user)
    current_academic_yr = mdl.academic_year.current_academic_year()

    data = {'academic_year': current_academic_yr,
            'person': manager_person,
            'manager_entity': entity_managed,
            'entity': entity,
            'entities': get_managed_entities(entity_managed),
            'offer_types': get_offer_types(),
            'pgms': get_programs(current_academic_yr,
                                 get_entity_list(entity, entity_managed),
                                 manager_person,
                                 pgm_offer_type),
            'managers': get_entity_program_managers(entity_managed, current_academic_yr),
            'offers_on': offers_on,
            'offer_type': pgm_offer_type,
            'add_errors': error_messages}
    return layout.render(request, "admin/pgm_manager.html", data)


def filter_by_entity_offer_type(academic_yr, entity_list, pgm_offer_type):
    return mdl.offer_year.search_offers(entity_list, academic_yr, pgm_offer_type)


def get_managed_entities(entity_managed):
    if entity_managed:
        children_acronyms = find_values('acronym', json.dumps(entity_managed.serializable_object()))
        return mdl.structure.find_by_acronyms(children_acronyms)

    return None


def get_entity_list(entity, entity_managed):
    if entity:
        entity_found = mdl.structure.search(entity, None, None).first()
        if entity_found:
            return [entity_found]
    else:
        children_acronyms = find_values('acronym', json.dumps(entity_managed.serializable_object()))
        return mdl.structure.find_by_acronyms(children_acronyms)

    return None


@login_required
def get_filter_value(request, value_name):
    if request.method == 'POST':
        value = request.POST.get(value_name, None)
    else:
        value = request.GET.get(value_name, None)

    if value == ALL_OPTION_VALUE or value == '':
        return None
    return value


def filter_by_person(person, entity_list, academic_yr, an_offer_type):
    program_managers = mdl.program_manager.find_by_person_academic_year(person,
                                                                        academic_yr,
                                                                        entity_list,
                                                                        an_offer_type)
    offer_years = []
    for manager in program_managers.distinct('offer_year'):
        offer_years.append(manager.offer_year)
    return offer_years


@login_required
@permission_required('base.is_entity_manager', raise_exception=True)
def delete_manager(request):
    pgms_to_be_removed = request.GET['pgms']  # offers_id are stock in inputbox in a list format (ex = "id1, id2")
    id_person_to_be_removed = request.GET['person']

    if id_person_to_be_removed:
        manager_person_to_be_removed = mdl.person.find_by_id(id_person_to_be_removed)
        if manager_person_to_be_removed:
            list_pgms_concerned = pgms_to_be_removed.split(",")
            offers = mdl.offer_year.find_by_id_list(list_pgms_concerned)
            remove_program_mgr_from_offers(offers, manager_person_to_be_removed)

    return HttpResponse(status=204)


def remove_program_mgr_from_offers(offers, person_to_be_removed):
    pgm_managers_to_delete = mdl.program_manager.find_by_offer_year_list_person(person_to_be_removed, offers)
    for p in pgm_managers_to_delete:
        mdl.program_manager.delete_by_id(p.id)


@login_required
@permission_required('base.is_entity_manager', raise_exception=True)
def person_list_search(request):
    lastname = request.GET['name']
    firstname = request.GET['firstname']
    employees = None
    if lastname or firstname:
        employees = mdl.person.search(lastname, firstname, True)

    serializer = PersonSerializer(employees, many=True)
    return JSONResponse(serializer.data)


@login_required
@permission_required('base.is_entity_manager', raise_exception=True)
def create_manager(request):

    person_selected = get_filter_selected_person(request)

    person_id = request.POST['person_id']
    pgms_id = request.POST['pgms_id']
    
    list_offer_id = convert_to_list(pgms_id)
    error_messages = ""
    person = mdl.person.find_by_id(person_id)

    offers_on = None
    if person:
        offers_on = mdl.offer_year.find_by_id_list(list_offer_id)
        error_messages = add_program_managers(offers_on, person)

    return pgm_manager_form(offers_on, error_messages, request, person_selected)


def get_administrator_faculty(a_user):
    entity_manager = mdl.entity_manager.find_entity_manager_by_user(a_user)
    if entity_manager:
        return entity_manager.structure
    return None


def is_already_program_manager(person, offer_yr):
    if mdl.program_manager.find_by_offer_year_person(person, offer_yr):
        return True
    return False


def add_program_managers(offers, person):
    error_messages = []
    for offer_yr in offers:
        if not add_offer_program_manager(offer_yr, person):
            error_messages.append("{0} {1} {2}".format(person, _('already_program_mgr'), offer_yr.acronym))
    return error_messages


def add_offer_program_manager(offer_yr, person):
    if offer_yr:
        if is_already_program_manager(person, offer_yr):
            return False
        else:
            add_save_program_manager(offer_yr, person)
            return True


def add_save_program_manager(offer_yr, person):
    pgm_manage = mdl.program_manager.ProgramManager(person=person,
                                                    offer_year=offer_yr)
    pgm_manage.save()


def convert_to_list(pgms_id):
    pgms_id = pgms_id.replace("[", "")
    pgms_id = pgms_id.replace("]", "")
    pgms_id = pgms_id.replace("'", "")
    list_offer_id = pgms_id.split(",")
    return list_offer_id


@login_required
def manager_pgm_list(request):
    manager_id = request.GET['manager_id']
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )


class PersonSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = mdl.person.Person
        fields = ('id', 'last_name', 'first_name', 'email', 'middle_name', 'user')


class OfferYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = mdl.offer_year.OfferYear
        fields = '__all__'


class PgmManager(object):
    # Needed to display the confirmation modal dialog while deleting
    def __init__(self, person_id, person_last_name, person_first_name, programs, offer_year_acronyms_on=None, offer_year_acronyms_off=None
                 ):
        self.person_id = person_id
        self.person_last_name = person_last_name
        self.person_first_name = person_first_name
        self.offer_year_acronyms_on = offer_year_acronyms_on  # acronyms of the offers the pgm manager will keep
        self.offer_year_acronyms_off = offer_year_acronyms_off  # acronyms of the offers the pgm manager will be removed from
        self.programs = programs


class PgmManagerSerializer(serializers.Serializer):
    # Needed to display the confirmation modal dialog while deleting
    person_id = serializers.IntegerField()
    person_last_name = serializers.CharField()
    person_first_name = serializers.CharField()
    offer_year_acronyms_on = serializers.CharField()
    offer_year_acronyms_off = serializers.CharField()
    programs = serializers.CharField()


@login_required
def update_managers_list(request):
    # Update the manager's list after add/delete
    list_id_offers_on = convert_to_list(request.GET['pgm_ids'])
    program_manager_list = mdl.program_manager.find_by_offer_year_list(list_id_offers_on)
    serializer = PgmManagerSerializer(build_program_manager_list(list_id_offers_on, program_manager_list, False),
                                      many=True)
    return JSONResponse(serializer.data)


def build_program_manager_list(list_id_offers_on, program_manager_list, detail):
    print('build_program_manager_list')
    print(timezone.now())
    pgm_managers = []
    persons = []
    for a_program_manager in program_manager_list:
        if a_program_manager.person not in pgm_managers:
            offers = get_offers_with_pgm_manager(list_id_offers_on, a_program_manager.person)
            pgms = build_offer_ids_string(offers)
            acronyms_off = build_acronyms_off_string(offers)
            if a_program_manager.person not in persons:
                persons.append(a_program_manager.person)
                if detail:
                    pgm_managers.append(PgmManager(person_id=a_program_manager.person.id,
                                                   person_last_name=a_program_manager.person.last_name,
                                                   person_first_name=a_program_manager.person.first_name,
                                                   programs=pgms,
                                                   offer_year_acronyms_on=pgm_to_keep_managing(a_program_manager.person,
                                                                                               offers),
                                                   offer_year_acronyms_off=acronyms_off
                                                   ))
                else:
                    pgm_managers.append(PgmManager(person_id=a_program_manager.person.id,
                                                   person_last_name=a_program_manager.person.last_name,
                                                   person_first_name=a_program_manager.person.first_name,
                                                   programs=pgms
                                                   ))
    print(timezone.now())
    return pgm_managers


def get_offers_with_pgm_manager(list_id_offers_on, a_person):
    offers = []
    for offer_year_id in list_id_offers_on:
        an_offer_year = mdl.offer_year.find_by_id(int(offer_year_id))
        if mdl.program_manager.find_by_offer_year_person(a_person, an_offer_year):
            offers.append(an_offer_year)
    return offers


def build_offer_ids_string(offers):
    #  Build a string of the offer ids
    #  String used in the ajax call
    pgms = ""
    for an_offer_year in offers:
        if pgms == "":
            pgms = an_offer_year.id
        else:
            pgms = "{0},{1}".format(pgms, an_offer_year.id)
    return pgms


def build_acronyms_off_string(offers):
    #  Build a string of the offer acronyms
    #  String used in the remove confirmation dialog pop-up
    acronyms_off = ""
    for an_offer_year in offers:
        if acronyms_off == "":
            acronyms_off = "{0}".format(an_offer_year.acronym)
        else:
            acronyms_off = "{0}, {1}".format(acronyms_off, an_offer_year.acronym)
    return acronyms_off


def pgm_to_keep_managing(a_person, programs):
    current_academic_yr = mdl.academic_year.current_academic_year()
    list_program_manager_to_keep = mdl.program_manager.find_by_person_exclude_offer_list(a_person, programs, current_academic_yr)
    # Concatenation of offers acronym to be used in the html page
    offer_acronym_concatenation = ""
    for program_manager_to_keep in list_program_manager_to_keep:
        if offer_acronym_concatenation == "":
            offer_acronym_concatenation = program_manager_to_keep.offer_year.acronym
        else:
            offer_acronym_concatenation = "{0}, {1}".format(offer_acronym_concatenation,
                                                            program_manager_to_keep.offer_year.acronym)
    return offer_acronym_concatenation


def get_programs(academic_yr, entity_list, manager_person, an_offer_type):
    if manager_person:
        pgms = filter_by_person(manager_person, entity_list, academic_yr, an_offer_type)
    else:
        pgms = filter_by_entity_offer_type(academic_yr, entity_list, an_offer_type)
    return pgms


def get_entity_program_managers(entity, academic_yr):
    entities = get_managed_entities(entity)
    return mdl.program_manager.find_by_management_entity(entities, academic_yr)


def find_values(key_value, json_repr):
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[key_value])
        except KeyError:
            pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # return value ignored
    return results


def get_filter_selected_person(request):
    person_selected_id = get_filter_value(request, 'person')
    if person_selected_id:
        return mdl.person.find_by_id(int(person_selected_id))
    return None


def get_offer_types():
    return mdl.offer_type.find_all()

@login_required
def delete_manager_information(request):
    print('delete_manager_information')
    # Update the manager's list after add/delete
    list_id_offers_on = convert_to_list(request.GET['pgm_ids'])
    offers_on = mdl.offer_year.find_by_id_list(list_id_offers_on)
    person_id = request.GET['person_id']
    a_person = mdl.person.find_by_id(int(person_id))
    print(a_person)
    program_manager_list = mdl.program_manager.find_by_offer_year_list_person(a_person, offers_on)
    serializer = PgmManagerSerializer(build_program_manager_list(list_id_offers_on, program_manager_list, True),
                                      many=True)


    return JSONResponse(serializer.data)