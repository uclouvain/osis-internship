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

from django.core import serializers
from django.contrib.auth.models import Group, User, Permission
import codecs
import factory
import factory.fuzzy
from base import models as mdl_base
from reference import models as mdl_reference
from attribution import models as mdl_attribution
from osis_common import models as mdl_common
from django.http import HttpResponse
from base.tests.factories.person_address import PersonAddressFactory
import string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('base.is_administrator'))
def make_fixtures(request):
    list_objects = []
    # Auth
    # data_content_types = serializers.serialize('json', ContentType.objects.all())
    list_objects.extend(Permission.objects.all())
    list_objects.extend(Group.objects.all())

    users = de_identifying_users()
    list_objects.extend(users)

    # Reference
    list_objects.extend(mdl_reference.currency.Currency.objects.all())
    list_objects.extend(mdl_reference.continent.Continent.objects.all())
    countries = mdl_reference.country.Country.objects.all()
    list_objects.extend(countries)

    decrees = mdl_reference.decree.Decree.objects.all()
    list_objects.extend(decrees)



    domains = mdl_reference.domain.Domain.objects.all()
    list_objects.extend(domains)

    grade_types = mdl_reference.grade_type.GradeType.objects.all()
    list_objects.extend(grade_types)

    list_objects.extend(mdl_reference.language.Language.objects.all())

    # Base
    persons = de_identifying_persons(users)
    list_objects.extend(persons)

    persons_addresses = de_identifying_person_addresses(persons, countries)
    list_objects.extend(persons_addresses)

    academic_years = mdl_base.academic_year.AcademicYear.objects.filter(year__gte=2016, year__lte=2018)
    list_objects.extend(academic_years)

    academic_calendars = mdl_base.academic_calendar.AcademicCalendar.objects.filter(academic_year__in=academic_years)
    list_objects.extend(academic_calendars)

    organizations = mdl_base.organization.Organization.objects.all()
    list_objects.extend(organizations)

    organization_addresses = mdl_base.organization_address.OrganizationAddress.objects.all()
    list_objects.extend(organization_addresses)


    campus_list = mdl_base.campus.Campus.objects.all()
    list_objects.extend(campus_list)

    education_groups = mdl_base.education_group.EducationGroup.objects.all()
    list_objects.extend(education_groups)

    offer_types = mdl_base.offer_type.OfferType.objects.all()
    list_objects.extend(offer_types)

    education_group_years = mdl_base.education_group_year.EducationGroupYear.objects.all()
    list_objects.extend(education_group_years)

    entities = mdl_base.entity.Entity.objects.all()
    list_objects.extend(entities)

    learning_container_years_all = []
    # to have data on the different year
    for ay in academic_years:
        learning_container_years = mdl_base.learning_container_year.LearningContainerYear.objects.filter(
            academic_year=ay)[:500]
        learning_container_years_all.extend(learning_container_years)
    list_objects.extend(learning_container_years_all)

    learning_containers = []

    for lc in learning_container_years_all:
        if lc.learning_container not in learning_containers:
            learning_containers.append(lc.learning_container)
    list_objects.extend(learning_containers)


    learning_component_years = mdl_base.learning_component_year.LearningComponentYear.objects.filter(
        learning_container_year__in=learning_container_years_all)
    list_objects.extend(learning_component_years)

    entity_container_years = mdl_base.entity_container_year.EntityContainerYear.objects.filter(
        learning_container_year__in=learning_container_years_all)
    list_objects.extend(entity_container_years)

    entity_component_years = mdl_base.entity_component_year.EntityComponentYear.objects.filter(
        entity_container_year__in=entity_container_years,
        learning_component_year__in=learning_component_years)

    list_objects.extend(entity_component_years)


    structures = mdl_base.structure.Structure.objects.all()
    list_objects.extend(structures)

    structure_addresses = mdl_base.structure_address.StructureAddress.objects.all()
    list_objects.extend(structure_addresses)

    entity_managers = mdl_base.entity_manager.EntityManager.objects.filter(person__in=persons)
    list_objects.extend(entity_managers)

    entity_versions = mdl_base.entity_version.EntityVersion.objects.all()
    list_objects.extend(entity_versions)

    learning_units = mdl_base.learning_unit.LearningUnit.objects.filter(learning_container__in=learning_containers)
    list_objects.extend(learning_units)

    learning_unit_years = mdl_base.learning_unit_year.LearningUnitYear.objects.filter(
        academic_year__in=academic_years,
        learning_unit__in=learning_units,
        learning_container_year__in=learning_container_years_all)
    list_objects.extend(learning_unit_years)

    students = mdl_base.student.Student.objects.filter(person__in=persons)
    list_objects.extend(students)

    offer_years = mdl_base.offer_year.OfferYear.objects.filter(academic_year__in=academic_years)
    list_objects.extend(offer_years)

    offers = []
    for oy in offer_years:
        if oy.offer not in offers:
            offers.append(oy.offer)

    list_objects.extend(offers)


    offer_enrollments = mdl_base.offer_enrollment.OfferEnrollment.objects.filter(offer_year__in=offer_years,
                                                                                 student__in=students)
    list_objects.extend(offer_enrollments)

    learning_unit_enrollments = mdl_base.learning_unit_enrollment.LearningUnitEnrollment.objects.filter(
        learning_unit_year__in=learning_unit_years,
        offer_enrollment__in=offer_enrollments)
    list_objects.extend(learning_unit_enrollments)

    session_exams = mdl_base.session_exam.SessionExam.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                     offer_year__in=offer_years)
    list_objects.extend(session_exams)

    exam_enrollments = mdl_base.exam_enrollment.ExamEnrollment.objects.filter(
        session_exam__in=session_exams,
        learning_unit_enrollment__in=learning_unit_enrollments)
    list_objects.extend(exam_enrollments)

    external_offers = mdl_base.external_offer.ExternalOffer.objects.filter(domain__in=domains,
                                                                           grade_type__in=grade_types,
                                                                           offer_year__in=offer_years)
    list_objects.extend(external_offers)

    group_element_years = mdl_base.group_element_year.GroupElementYear.objects.filter(
        parent__in=education_group_years,
        child_branch__in=education_group_years,
        child_leaf=education_group_years,
        learning_unit_year__in=learning_unit_years)
    list_objects.extend(group_element_years)

    learning_class_years = mdl_base.learning_class_year.LearningClassYear.objects.filter(
        learning_component_year__in=learning_component_years)
    list_objects.extend(learning_class_years)

    learning_unit_components = mdl_base.learning_unit_component.LearningUnitComponent.objects.filter(
        learning_unit_year__in=learning_unit_years,
        learning_component_year__in=learning_component_years)
    list_objects.extend(learning_unit_components)

    learning_unit_component_classes = mdl_base.learning_unit_component_class.LearningUnitComponentClass.objects.filter(
        learning_unit_component__in=learning_unit_components,
        learning_class_year__in=learning_class_years)
    list_objects.extend(learning_unit_component_classes)

    offer_year_calendars = mdl_base.offer_year_calendar.OfferYearCalendar.objects.filter(
        academic_calendar__in=academic_calendars,
        offer_year__in=offer_years)
    list_objects.extend(offer_year_calendars)

    offer_year_domains = mdl_base.offer_year_domain.OfferYearDomain.objects.filter(domain__in=domains,
                                                                                   offer_year__in=offer_years)
    list_objects.extend(offer_year_domains)

    tutors = mdl_base.tutor.Tutor.objects.filter(person__in=persons)
    list_objects.extend(tutors)

    # Attribution
    attributions = mdl_attribution.attribution.Attribution.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                          tutor__in=tutors)
    list_objects.extend(attributions)

    attribution_charges = mdl_attribution.attribution_charge.AttributionCharge.objects.filter(
        attribution__in=attributions,
        learning_unit_component__in=learning_unit_components)
    list_objects.extend(attribution_charges)

    # Osis_common
    message_templates = mdl_common.message_template.MessageTemplate.objects.all()
    list_objects.extend(message_templates)

    response = HttpResponse(serializers.serialize('json',list_objects), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="initial_data.json"'

    return response


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('base.is_administrator'))
def make_fixtures_old(request):
    list_objects = []
    # Auth
    # data_content_types = serializers.serialize('json', ContentType.objects.all())

    m=''
    data_permissions = serializers.serialize('json', Permission.objects.all())
    cpt = 0
    cpt, m = concat_result(cpt, data_permissions, m)

    data_groups = serializers.serialize('json', Group.objects.all())
    cpt, m = concat_result(cpt, data_groups, m)

    users = de_identifying_users()
    data_users = serializers.serialize('json', users)
    cpt, m = concat_result(cpt, data_users, m)

    # Reference
    data_currencies = serializers.serialize('json', mdl_reference.currency.Currency.objects.all())
    cpt, m = concat_result(cpt, data_currencies, m)

    data_continents = serializers.serialize('json', mdl_reference.continent.Continent.objects.all())
    cpt, m = concat_result(cpt, data_continents, m)

    countries = mdl_reference.country.Country.objects.all()
    data_countries = serializers.serialize('json', countries)
    cpt, m = concat_result(cpt, data_countries, m)

    decrees = mdl_reference.decree.Decree.objects.all()
    data_decrees = serializers.serialize('json', decrees)
    cpt, m = concat_result(cpt, data_decrees, m)

    domains = mdl_reference.domain.Domain.objects.all()
    data_domains = serializers.serialize('json', domains)
    cpt, m = concat_result(cpt, data_domains, m)

    grade_types = mdl_reference.grade_type.GradeType.objects.all()
    data_grade_types = serializers.serialize('json', grade_types)
    cpt, m = concat_result(cpt, data_grade_types, m)

    data_languages = serializers.serialize('json', mdl_reference.language.Language.objects.all())
    cpt, m = concat_result(cpt, data_languages, m)

    # Base
    persons = de_identifying_persons(users)
    data_persons = serializers.serialize('json', persons)
    cpt, m = concat_result(cpt, data_persons, m)

    persons_addresses = de_identifying_person_addresses(persons, countries)
    data_person_addresses = serializers.serialize('json', persons_addresses)
    cpt, m = concat_result(cpt, data_person_addresses, m)

    academic_years = mdl_base.academic_year.AcademicYear.objects.filter(year__gte=2016, year__lte=2018)
    data_academic_years = serializers.serialize('json', academic_years)
    cpt, m = concat_result(cpt, data_academic_years, m)

    academic_calendars = mdl_base.academic_calendar.AcademicCalendar.objects.filter(academic_year__in=academic_years)
    data_academic_calendars = serializers.serialize('json', academic_calendars)
    cpt, m = concat_result(cpt, data_academic_calendars, m)

    organizations = mdl_base.organization.Organization.objects.all()
    data_organizations = serializers.serialize('json', organizations)
    cpt, m = concat_result(cpt, data_organizations, m)

    organization_addresses = mdl_base.organization_address.OrganizationAddress.objects.all()
    data_organization_addresses = serializers.serialize('json', organization_addresses)
    cpt, m = concat_result(cpt, data_organization_addresses, m)

    campus_list = mdl_base.campus.Campus.objects.all()
    data_campus = serializers.serialize('json', campus_list)
    cpt, m = concat_result(cpt, data_campus, m)

    education_groups = mdl_base.education_group.EducationGroup.objects.all()
    data_education_groups = serializers.serialize('json', education_groups)
    cpt, m = concat_result(cpt, data_education_groups, m)

    offer_types = mdl_base.offer_type.OfferType.objects.all()
    data_offer_types = serializers.serialize('json', offer_types)
    cpt, m = concat_result(cpt, data_offer_types, m)

    education_group_years = mdl_base.education_group_year.EducationGroupYear.objects.all()
    data_education_group_years = serializers.serialize('json', education_group_years)
    cpt, m = concat_result(cpt, data_education_group_years, m)

    entities = mdl_base.entity.Entity.objects.all()
    data_entities = serializers.serialize('json', entities)
    cpt, m = concat_result(cpt, data_entities, m)

    learning_container_years_all = []
    # to have data on the different year
    for ay in academic_years:
        learning_container_years = mdl_base.learning_container_year.LearningContainerYear.objects.filter(
            academic_year=ay)[:500]
        learning_container_years_all.extend(learning_container_years)
    data_learning_container_years = serializers.serialize('json', learning_container_years_all)
    cpt, m = concat_result(cpt, data_learning_container_years, m)

    learning_containers = []

    for lc in learning_container_years_all:
        if lc.learning_container not in learning_containers:
            learning_containers.append(lc.learning_container)
    data_learning_containers = serializers.serialize('json', learning_containers)
    cpt, m = concat_result(cpt, data_learning_containers, m)

    learning_component_years = mdl_base.learning_component_year.LearningComponentYear.objects.filter(
        learning_container_year__in=learning_container_years_all)
    data_learning_component_years = serializers.serialize('json', learning_component_years)
    cpt, m = concat_result(cpt, data_learning_component_years, m)

    entity_container_years = mdl_base.entity_container_year.EntityContainerYear.objects.filter(
        learning_container_year__in=learning_container_years_all)
    data_entity_container_years = serializers.serialize('json', entity_container_years)
    cpt, m = concat_result(cpt, data_entity_container_years, m)

    entity_component_years = mdl_base.entity_component_year.EntityComponentYear.objects.filter(
        entity_container_year__in=entity_container_years,
        learning_component_year__in=learning_component_years)
    data_entity_component_years = serializers.serialize('json', entity_component_years)
    cpt, m = concat_result(cpt, data_entity_component_years, m)

    structures = mdl_base.structure.Structure.objects.all()
    data_structures = serializers.serialize('json', structures)
    cpt, m = concat_result(cpt, data_structures, m)

    structure_addresses = mdl_base.structure_address.StructureAddress.objects.all()
    data_structure_addresses = serializers.serialize('json', structure_addresses)
    cpt, m = concat_result(cpt, data_structure_addresses, m)

    entity_managers = mdl_base.entity_manager.EntityManager.objects.filter(person__in=persons)
    data_entity_managers = serializers.serialize('json', entity_managers)
    cpt, m = concat_result(cpt, data_entity_managers, m)

    entity_versions = mdl_base.entity_version.EntityVersion.objects.all()
    data_entity_versions = serializers.serialize('json', entity_versions)
    cpt, m = concat_result(cpt, data_entity_versions, m)

    learning_units = mdl_base.learning_unit.LearningUnit.objects.filter(learning_container__in=learning_containers)
    data_learning_units = serializers.serialize('json', learning_units)
    cpt, m = concat_result(cpt, data_learning_units, m)

    learning_unit_years = mdl_base.learning_unit_year.LearningUnitYear.objects.filter(
        academic_year__in=academic_years,
        learning_unit__in=learning_units,
        learning_container_year__in=learning_container_years_all)
    data_learning_unit_years = serializers.serialize('json', learning_unit_years)
    cpt, m = concat_result(cpt, data_learning_unit_years, m)

    students = mdl_base.student.Student.objects.filter(person__in=persons)
    data_students = serializers.serialize('json', students)
    cpt, m = concat_result(cpt, data_students, m)

    offer_years = mdl_base.offer_year.OfferYear.objects.filter(academic_year__in=academic_years)
    data_offer_years = serializers.serialize('json', offer_years)
    cpt, m = concat_result(cpt, data_offer_years, m)

    offers = []
    for oy in offer_years:
        if oy.offer not in offers:
            offers.append(oy.offer)
    data_offers = serializers.serialize('json', offers)
    cpt, m = concat_result(cpt, data_offers, m)

    offer_enrollments = mdl_base.offer_enrollment.OfferEnrollment.objects.filter(offer_year__in=offer_years,
                                                                                 student__in=students)
    data_offer_enrollments = serializers.serialize('json', offer_enrollments)
    cpt, m = concat_result(cpt, data_offer_enrollments, m)

    learning_unit_enrollments = mdl_base.learning_unit_enrollment.LearningUnitEnrollment.objects.filter(
        learning_unit_year__in=learning_unit_years,
        offer_enrollment__in=offer_enrollments)
    data_learning_unit_enrollments = serializers.serialize('json', learning_unit_enrollments)
    cpt, m = concat_result(cpt, data_learning_unit_enrollments, m)

    session_exams = mdl_base.session_exam.SessionExam.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                     offer_year__in=offer_years)
    data_session_exams = serializers.serialize('json', session_exams)
    cpt, m = concat_result(cpt, data_session_exams, m)

    exam_enrollments = mdl_base.exam_enrollment.ExamEnrollment.objects.filter(
        session_exam__in=session_exams,
        learning_unit_enrollment__in=learning_unit_enrollments)
    data_exam_enrollments = serializers.serialize('json', exam_enrollments)
    cpt, m = concat_result(cpt, data_exam_enrollments, m)

    external_offers = mdl_base.external_offer.ExternalOffer.objects.filter(domain__in=domains,
                                                                           grade_type__in=grade_types,
                                                                           offer_year__in=offer_years)
    data_external_offers = serializers.serialize('json', external_offers)
    cpt, m = concat_result(cpt, data_external_offers, m)

    group_element_years = mdl_base.group_element_year.GroupElementYear.objects.filter(
        parent__in=education_group_years,
        child_branch__in=education_group_years,
        child_leaf=education_group_years,
        learning_unit_year__in=learning_unit_years)
    data_group_element_years = serializers.serialize('json', group_element_years)
    cpt, m = concat_result(cpt, data_group_element_years, m)

    learning_class_years = mdl_base.learning_class_year.LearningClassYear.objects.filter(
        learning_component_year__in=learning_component_years)
    data_learning_class_years = serializers.serialize('json', learning_class_years)
    cpt, m = concat_result(cpt, data_learning_class_years, m)

    learning_unit_components = mdl_base.learning_unit_component.LearningUnitComponent.objects.filter(
        learning_unit_year__in=learning_unit_years,
        learning_component_year__in=learning_component_years)
    data_learning_unit_components = serializers.serialize('json', learning_unit_components)
    cpt, m = concat_result(cpt, data_learning_unit_components, m)

    learning_unit_component_classes = mdl_base.learning_unit_component_class.LearningUnitComponentClass.objects.filter(
        learning_unit_component__in=learning_unit_components,
        learning_class_year__in=learning_class_years)
    data_learning_unit_component_classes = serializers.serialize('json', learning_unit_component_classes)
    cpt, m = concat_result(cpt, data_learning_unit_component_classes, m)

    offer_year_calendars = mdl_base.offer_year_calendar.OfferYearCalendar.objects.filter(
        academic_calendar__in=academic_calendars,
        offer_year__in=offer_years)
    data_offer_year_calendars = serializers.serialize('json', offer_year_calendars)
    cpt, m = concat_result(cpt, data_offer_year_calendars, m)

    offer_year_domains = mdl_base.offer_year_domain.OfferYearDomain.objects.filter(domain__in=domains,
                                                                                   offer_year__in=offer_years)
    data_offer_year_domains = serializers.serialize('json', offer_year_domains)
    cpt, m = concat_result(cpt, data_offer_year_domains, m)

    tutors = mdl_base.tutor.Tutor.objects.filter(person__in=persons)
    data_tutors = serializers.serialize('json', tutors)
    cpt, m = concat_result(cpt, data_tutors, m)

    # Attribution
    attributions = mdl_attribution.attribution.Attribution.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                          tutor__in=tutors)
    data_attributions = serializers.serialize('json', attributions)
    cpt, m = concat_result(cpt, data_attributions, m)

    attribution_charges = mdl_attribution.attribution_charge.AttributionCharge.objects.filter(
        attribution__in=attributions,
        learning_unit_component__in=learning_unit_components)
    data_attribution_charges = serializers.serialize('json', attribution_charges)
    cpt, m = concat_result(cpt, data_attribution_charges, m)

    # Osis_common
    message_templates = mdl_common.message_template.MessageTemplate.objects.all()
    data_message_templates = serializers.serialize('json', message_templates)
    cpt, m = concat_result(cpt, data_message_templates, m)

    # m = "[{}]".format(m)
    #
    # with codecs.open('base/fixtures/initial_data.json', 'wb', encoding='utf-8') as f_inital_fixtures:
    #     f_inital_fixtures.write(m)
    l = []
    l.extend(users)
    l.extend(Group.objects.all())
    response = HttpResponse(serializers.serialize('json',l), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="initial_data.json"'
    # filename = "dddd"
    # response = HttpResponse(f_inital_fixtures, content_type='application/json')
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

    # return HttpResponse(status=200)


def concat_result(cpt, data, fixtures_data):
    if data and data != '[]':
        cl = clear_data(data)
        if cl:
            if cpt > 0:
                fixtures_data = "{}, {}".format(fixtures_data, cl)
            else:
                fixtures_data = "{}".format(cl)

            cpt = cpt + 1
    return cpt, fixtures_data


def de_identifying_users():
    users = User.objects.all()[:50]
    for user in users:
        user.lastname= factory.Faker('last_name')

    return users


def de_identifying_persons(users):
    persons = []
    for user in users:
        p = mdl_base.person.find_by_user(user)
        if p:
            p.last_name = str(factory.Faker('last_name'))
            p.first_name = str(factory.Faker('first_name'))
            p.global_id = str(factory.fuzzy.FuzzyText(length=10, chars=string.digits))
            persons.append(p)
    get_students(persons)
    get_tutors(persons)
    return persons


def get_tutors(persons):
    tutors = mdl_base.tutor.Tutor.objects.exclude(person__in=persons)[:50]
    for t in tutors:
        persons.append(t.person)


def get_students(persons):
    students = mdl_base.student.Student.objects.filter(person__in=persons)[:50]
    for stud in students:
        persons.append(stud)


def de_identifying_person_addresses(persons, countries):
    person_addresses = []
    for p in persons:
        if p:
            country_random = countries.order_by('?').first()
            person_adr = PersonAddressFactory(person=p, country=country_random)
            person_addresses.append(person_adr)
    return person_addresses


def clear_data(data_content_types):

    if data_content_types != "[]":

        makeitastring = ''.join(map(str, data_content_types))
        makeitastring = makeitastring.replace('[','',1)


        k = makeitastring.rfind("]")
        new_string = makeitastring[:k] + "" + makeitastring[k+1:]
        return new_string

    return None
