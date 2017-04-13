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
from reference.enums import grade_type_coverage
from base.enums import structure_type
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from base.enums import person_status, person_type
from django.contrib.auth.models import User


ALL_OPTION_VALUE = "-"


@login_required
def pgm_manager_administration(request):
    faculty = get_administrator_faculty(request)
    current_academic_yr = mdl.academic_year.current_academic_year()
    return layout.render(request, "admin/pgm_manager.html", {
        'academic_year': current_academic_yr,
        'person': None,
        'manager_entity': faculty,
        'entity': faculty,
        'entities': ['1', '2'],
        'pgm_types': mdl_ref.grade_type.find_by_coverage(grade_type_coverage.UNIVERSITY),
        'managers': get_faculty_program_managers(faculty, current_academic_yr)})


@login_required
def pgm_manager_search(request):
    faculty = get_administrator_faculty(request)
    entity = request.GET.get('entity', None)
    pgm_grade_type = get_filter_value(request, 'pgm_type')
    person = get_filter_value(request, 'person')

    return pgm_manager_search_form(entity,  faculty, person, pgm_grade_type, None, request)


def pgm_manager_search_form(entity, faculty, person, pgm_grade_type, offers_on, request):
    print(person)
    entity_list = get_entity_list(entity)
    current_academic_yr = mdl.academic_year.current_academic_year()
    manager_person = None
    if person:
        manager_person = mdl.person.find_by_id(int(person))
    data = {'academic_year': current_academic_yr,
            'person': manager_person,
            'manager_entity': faculty,
            'entity': entity,
            'pgm_types': mdl_ref.grade_type.find_by_coverage(grade_type_coverage.UNIVERSITY),
            'pgms': get_programs(current_academic_yr, entity_list, manager_person, pgm_grade_type),
            'managers': get_faculty_program_managers(faculty, current_academic_yr),
            'offers_on': offers_on,
            'pgm_type': pgm_grade_type}
    return layout.render(request, "admin/pgm_manager.html", data)


def filter_by_entity_grade_type(academic_yr, entity_list, pgm_grade_type):
    return mdl.offer_year.search_offers(entity_list, academic_yr, pgm_grade_type)


def get_entity_list(entity):
    if entity:
        if entity == ALL_OPTION_VALUE:
            return list(mdl.structure.search(entity, None, structure_type.FACULTY))
        else:
            entity_found = mdl.structure.search(entity, None, None).first()
            if entity_found:
                return [entity_found]
    return None


def get_filter_value(request, value_name):
    if request.method == 'POST':
        value = request.POST.get(value_name, None)
    else:
        value = request.GET.get(value_name, None)

    if value == ALL_OPTION_VALUE:
        return None
    return value


def filter_by_person(manager_person, entity_list, academic_yr, pgm_type):
    managers = mdl.program_manager.find_by_person_academic_year(manager_person, academic_yr, entity_list, pgm_type)
    pgms2 = []
    for m in managers.distinct('offer_year'):
        pgms2.append(m.offer_year)
    return pgms2


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def remove_manager(request):
    pgms_to_be_removed = request.GET['pgms_to_be_removed']
    person_to_be_removed = request.GET['person_to_be_removed']

    if person_to_be_removed:
        manager_person_to_be_removed = mdl.person.find_by_id(person_to_be_removed)
        if manager_person_to_be_removed:
            list_pgms_concerned = pgms_to_be_removed.split(",")
            offers = mdl.offer_year.find_by_id_list(list_pgms_concerned)
            remove_programs_managers(offers, manager_person_to_be_removed)

    return HttpResponse(status=204)


def get_offer_with_checkbox_on(request):
    if request.method == 'POST':
        offers_checked_ch = request.POST['offers_checked']
    else:
        offers_checked_ch = request.GET.get('offers_checked')

    offers_checked = offers_checked_ch.split(",")

    offers_on = None
    if offers_checked:
        offers_on = mdl.offer_year.find_by_id_list(offers_checked)
    return offers_on


def remove_programs_managers(offers, person_to_be_removed):
    pgm_manager_to_delete = mdl.program_manager.find_by_offer_year_list_person(person_to_be_removed, offers)
    for p in pgm_manager_to_delete:
        mdl.program_manager.delete_by_id(p.id)


@login_required
def find_checked_pgms(request):
    # If pgm checkbox is checked there is the pgm id in the hidden textbox prefix by pgm_id_
    list_offer_id = []
    for k, v in request.POST.items():
        if k.startswith('pgm_id_'):
            if v:
                list_offer_id.append(v)
    return list_offer_id


def find_faculty(acronym):
    return mdl.structure.find_first(acronym, None, structure_type.FACULTY)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def person_list_search(request):
    lastname = request.GET['name']
    firstname = request.GET['firstname']
    employees = None
    if lastname or firstname:
        employees = mdl.employee.search(lastname, firstname)
    print('employees')
    print(employees)
    persons = []
    for e in employees:
        if e.person not in persons:
            persons.append(e.person)
    serializer = PersonSerializer(persons, many=True)
    return JSONResponse(serializer.data)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def add_manager(request):
    print('add_manager')
    person_id = request.POST['person_id']
    person = mdl.person.find_by_id(person_id)
    pgms_id = request.POST['pgms_id']
    
    list_offer_id = convert_to_list(pgms_id)

    if person:
        add_program_managers(list_offer_id, person)

    entity = get_filter_value(request, 'entity')
    pgm_grade_type = get_filter_value(request, 'pgm_type')
    person = get_filter_value(request, 'person')

    faculty = get_administrator_faculty(request)

    offers_on = mdl.offer_year.find_by_id_list(list_offer_id)
    return pgm_manager_search_form(entity,  faculty, person, pgm_grade_type, offers_on, request)


def get_administrator_faculty(request):
    faculty_administrator = mdl.faculty_administrator.find_faculty_administrator_by_user(request.user)
    if faculty_administrator:
        return faculty_administrator.structure
    return None


def add_program_managers(list_offer_id, person):
    for offer_id in list_offer_id:
        offer_yr = mdl.offer_year.find_by_id(int(offer_id))
        if offer_yr:
            pgm_manage = mdl.program_manager.ProgramManager()
            pgm_manage.person = person
            pgm_manage.offer_year = offer_yr
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
    # user = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user = UserSerializer(many=False)

    class Meta:
        model = mdl.person.Person
        fields = ('id', 'last_name', 'first_name', 'email', 'middle_name', 'user')


class OfferYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = mdl.offer_year.OfferYear
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


@login_required
def update_managers_list(request):
    list_offer_id = convert_to_list(request.GET['pgm_ids'])
    program_manager_list = mdl.program_manager.find_by_offer_year_list(list_offer_id)
    pgm_managers = []
    persons = []

    for program_manager in program_manager_list:
        if program_manager.person not in pgm_managers:
            acronyms_off_list = []
            acronyms_off = ""
            pgms = ""
            offers = []

            for offer_year_id in list_offer_id:
                an_offer_year = mdl.offer_year.find_by_id(int(offer_year_id))
                mg = mdl.program_manager.find_by_offer_year_list_person(program_manager.person, [an_offer_year])
                if mg:
                    if acronyms_off == "":
                        acronyms_off = "{0}".format(an_offer_year.acronym)
                    else:
                        acronyms_off = "{0}, {1}".format(acronyms_off, an_offer_year.acronym)
                    if pgms == "":
                        pgms = an_offer_year.id
                    else:
                        pgms = "{0}, {1}".format(pgms, an_offer_year.id)
                    offers.append(an_offer_year)
                    acronyms_off_list.append(acronyms_off)
            if program_manager.person not in persons:
                persons.append(program_manager.person)

                pgm_managers.append(PgmManager(person_id=program_manager.person.id,
                                               person_last_name=program_manager.person.last_name,
                                               person_first_name=program_manager.person.first_name,
                                               offer_year_acronyms_on=pgm_to_keep_managing(program_manager.person,
                                                                                           offers),
                                               offer_year_acronyms_off=acronyms_off,
                                               programs=pgms))

    serializer = PgmManagerSerializer(pgm_managers, many=True)
    return JSONResponse(serializer.data)


def pgm_to_keep_managing(a_person, programs):
    list_program_manager_to_keep = mdl.program_manager.find_by_person_exclude_offer_list(a_person, programs)
    # Concatenation of offers acronym to be used in the html page
    offer_acronym_concatenation = ""
    for program_manager_to_keep in list_program_manager_to_keep:
        if offer_acronym_concatenation == "":
            offer_acronym_concatenation = program_manager_to_keep.offer_year.acronym
        else:
            offer_acronym_concatenation = "{0}, {1}".format(offer_acronym_concatenation,
                                                            program_manager_to_keep.offer_year.acronym)
    return offer_acronym_concatenation


def get_programs(academic_yr, entity_list, manager_person, pgm_grade_type):
    if manager_person:
        pgms = filter_by_person(manager_person, entity_list, academic_yr, pgm_grade_type)
    else:
        pgms = filter_by_entity_grade_type(academic_yr, entity_list, pgm_grade_type)
    return pgms


def get_faculty_program_managers(faculty, academic_yr):
    return mdl.program_manager.find_by_entity_administration_fac(faculty, academic_yr)

