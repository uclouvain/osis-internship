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
import json
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
import sys


def make_fixtures(request):
    # Auth
    data_permissions = serializers.serialize('json', Permission.objects.all())
    data_groups = serializers.serialize('json', Group.objects.all())
    users = de_identifying_users()
    data_users = serializers.serialize('json', users)
    # Reference

    data_currencies = serializers.serialize('json', mdl_reference.currency.Currency.objects.all())
    data_continents = serializers.serialize('json', mdl_reference.continent.Continent.objects.all())
    countries = mdl_reference.country.Country.objects.all()
    data_countries = serializers.serialize('json', countries)
    decrees = mdl_reference.decree.Decree.objects.all()
    data_decrees = serializers.serialize('json', decrees)
    domains = mdl_reference.domain.Domain.objects.all()
    data_domains = serializers.serialize('json', domains)
    grade_types = mdl_reference.grade_type.GradeType.objects.all()
    data_grade_types = serializers.serialize('json', grade_types)
    data_languages = serializers.serialize('json', mdl_reference.language.Language.objects.all())

    # Base
    persons = de_identifying_persons(users)
    data_persons = serializers.serialize('json', persons)

    persons_addresses = de_identifying_person_addresses(persons, countries)
    data_person_addresses = serializers.serialize('json', persons_addresses)

    academic_years = mdl_base.academic_year.AcademicYear.objects.filter(year__gte=2016, year__lte=2018)
    data_academic_years = serializers.serialize('json', academic_years)

    academic_calendars = mdl_base.academic_calendar.AcademicCalendar.objects.filter(academic_year__in=academic_years)
    data_academic_calendars = serializers.serialize('json', academic_calendars)

    organizations = mdl_base.organization.Organization.objects.all()
    data_organizations = serializers.serialize('json', organizations)

    organization_addresses = mdl_base.organization_address.OrganizationAddress.objects.all()
    data_organization_addresses = serializers.serialize('json', organization_addresses)

    campus_list = mdl_base.campus.Campus.objects.all()
    data_campus = serializers.serialize('json', campus_list)

    education_groups = mdl_base.education_group.EducationGroup.objects.all()
    data_education_groups = serializers.serialize('json', education_groups)

    offer_types = mdl_base.offer_type.OfferType.objects.all()
    data_offer_types = serializers.serialize('json', offer_types)

    education_group_years = mdl_base.education_group_year.EducationGroupYear.objects.all()
    data_education_group_years = serializers.serialize('json', education_group_years)

    entities = mdl_base.entity.Entity.objects.all()
    data_entities = serializers.serialize('json', entities)

    learning_container_years_all = []
    # to have data on the different year
    for ay in academic_years:
        learning_container_years = mdl_base.learning_container_year.LearningContainerYear.objects.filter(
            academic_year=ay)[:500]
        learning_container_years_all.extend(learning_container_years)
    data_learning_container_years = serializers.serialize('json', learning_container_years_all)

    learning_containers = []

    for lc in learning_container_years:
        if lc.learning_container not in learning_containers:
            learning_containers.append(lc.learning_container)
    data_learning_containers = serializers.serialize('json', learning_containers)

    learning_component_years = mdl_base.learning_component_year.LearningComponentYear.objects.filter(
        learning_container_year__in=learning_container_years)
    data_learning_component_years = serializers.serialize('json', learning_component_years)

    entity_container_years = mdl_base.entity_container_year.EntityContainerYear.objects.filter(
        learning_container_year__in=learning_container_years)
    data_entity_container_years = serializers.serialize('json', entity_container_years)

    entity_component_years = mdl_base.entity_component_year.EntityComponentYear.objects.filter(
        entity_container_year__in=entity_container_years,
        learning_component_year__in=learning_component_years)
    data_entity_component_years = serializers.serialize('json', entity_component_years)

    structures = mdl_base.structure.Structure.objects.all()
    data_structures = serializers.serialize('json', structures)

    structure_addresses = mdl_base.structure_address.StructureAddress.objects.all()
    data_structure_addresses = serializers.serialize('json', structure_addresses)

    entity_managers = mdl_base.entity_manager.EntityManager.objects.filter(person__in=persons)
    data_entity_managers = serializers.serialize('json', entity_managers)

    entity_versions = mdl_base.entity_version.EntityVersion.objects.all()
    data_entity_versions = serializers.serialize('json', entity_versions)

    learning_units = mdl_base.learning_unit.LearningUnit.objects.filter(learning_container__in=learning_containers)
    data_learning_units = serializers.serialize('json', learning_units)

    learning_unit_years = mdl_base.learning_unit_year.LearningUnitYear.objects.filter(
        academic_year__in=academic_years,
        learning_unit__in=learning_units,
        learning_container_year__in=learning_container_years)
    data_learning_unit_years = serializers.serialize('json', learning_unit_years)

    students = mdl_base.student.Student.objects.filter(person__in=persons)
    data_students = serializers.serialize('json', students)

    offer_years = mdl_base.offer_year.OfferYear.objects.filter(academic_year__in=academic_years)
    data_offer_years = serializers.serialize('json', offer_years)

    offers = []
    for oy in offer_years:
        if oy.offer not in offers:
            offers.append(oy.offer)
    data_offers = serializers.serialize('json', offers)

    offer_enrollments = mdl_base.offer_enrollment.OfferEnrollment.objects.filter(offer_year__in=offer_years,
                                                                                 student__in=students)
    data_offer_enrollments = serializers.serialize('json', offer_enrollments)

    learning_unit_enrollments = mdl_base.learning_unit_enrollment.LearningUnitEnrollment.objects.filter(
        learning_unit_year__in=learning_unit_years,
        offer_enrollment__in=offer_enrollments)
    data_learning_unit_enrollments = serializers.serialize('json', learning_unit_enrollments)

    session_exams = mdl_base.session_exam.SessionExam.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                     offer_year__in=offer_years)
    data_session_exams = serializers.serialize('json', session_exams)

    exam_enrollments = mdl_base.exam_enrollment.ExamEnrollment.objects.filter(
        session_exam__in=session_exams,
        learning_unit_enrollment__in=learning_unit_enrollments)
    data_exam_enrollments = serializers.serialize('json', exam_enrollments)

    external_offers = mdl_base.external_offer.ExternalOffer.objects.filter(domain__in=domains,
                                                                           grade_type__in=grade_types,
                                                                           offer_year__in=offer_years)
    data_external_offers = serializers.serialize('json', external_offers)

    group_element_years = mdl_base.group_element_year.GroupElementYear.objects.filter(
        parent__in=education_group_years,
        child_branch__in=education_group_years,
        child_leaf=education_group_years,
        learning_unit_year__in=learning_unit_years)
    data_group_element_years = serializers.serialize('json', group_element_years)

    learning_class_years = mdl_base.learning_class_year.LearningClassYear.objects.filter(
        learning_component_year__in=learning_component_years)
    data_learning_class_years = serializers.serialize('json', learning_class_years)

    learning_unit_components = mdl_base.learning_unit_component.LearningUnitComponent.objects.filter(
        learning_unit_year__in=learning_unit_years,
        learning_component_year__in=learning_component_years)
    data_learning_unit_components = serializers.serialize('json', learning_unit_components)

    learning_unit_component_classes = mdl_base.learning_unit_component_class.LearningUnitComponentClass.objects.filter(
        learning_unit_component__in=learning_unit_components,
        learning_class_year__in=learning_class_years)
    data_learning_unit_component_classes = serializers.serialize('json', learning_unit_component_classes)

    offer_year_calendars = mdl_base.offer_year_calendar.OfferYearCalendar.objects.filter(
        academic_calendar__in=academic_calendars,
        offer_year__in=offer_years)
    data_offer_year_calendars = serializers.serialize('json', offer_year_calendars)

    offer_year_domains = mdl_base.offer_year_domain.OfferYearDomain.objects.filter(domain__in=domains,
                                                                                   offer_year__in=offer_years)
    data_offer_year_domains = serializers.serialize('json', offer_year_domains)

    tutors = mdl_base.tutor.Tutor.objects.filter(person__in=persons)
    data_tutors = serializers.serialize('json', tutors)

    # Attribution
    attributions = mdl_attribution.attribution.Attribution.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                          tutor__in=tutors)
    data_attributions = serializers.serialize('json', attributions)

    attribution_charges = mdl_attribution.attribution_charge.AttributionCharge.objects.filter(
        attribution__in=attributions,
        learning_unit_component__in=learning_unit_components)
    data_attribution_charges = serializers.serialize('json', attribution_charges)

    # Osis_common
    message_templates = mdl_common.message_template.MessageTemplate.objects.all()
    data_message_templates = serializers.serialize('json', message_templates)

    with codecs.open('base/fixtures/initial_data.json', 'wb', encoding='utf-8') as f_inital_fixtures:
        # Auth         
        f_inital_fixtures.write(data_permissions)
        f_inital_fixtures.write(data_groups)
        f_inital_fixtures.write(data_users)

        # Reference
        f_inital_fixtures.write(data_currencies)
        f_inital_fixtures.write(data_continents)
        f_inital_fixtures.write(data_countries)
        f_inital_fixtures.write(data_decrees)
        f_inital_fixtures.write(data_domains)
        f_inital_fixtures.write(data_grade_types)
        f_inital_fixtures.write(data_languages)

        # Base
        f_inital_fixtures.write(data_persons)
        f_inital_fixtures.write(data_person_addresses)
    
        f_inital_fixtures.write(data_academic_years)
        f_inital_fixtures.write(data_academic_calendars)
    
        f_inital_fixtures.write(data_organizations)
        f_inital_fixtures.write(data_organization_addresses)
    
        f_inital_fixtures.write(data_campus)
        f_inital_fixtures.write(data_education_groups)
        f_inital_fixtures.write(data_offer_types)
        f_inital_fixtures.write(data_education_group_years)
        f_inital_fixtures.write(data_entities)
        f_inital_fixtures.write(data_learning_containers)
        f_inital_fixtures.write(data_learning_containers)
        f_inital_fixtures.write(data_learning_component_years)
        f_inital_fixtures.write(data_entity_container_years)
        f_inital_fixtures.write(data_entity_component_years)
        f_inital_fixtures.write(data_structures)
        f_inital_fixtures.write(data_structure_addresses)
        f_inital_fixtures.write(data_entity_managers)
        f_inital_fixtures.write(data_entity_versions)
        f_inital_fixtures.write(data_learning_units)
        f_inital_fixtures.write(data_learning_unit_years)
        f_inital_fixtures.write(data_students)
        f_inital_fixtures.write(data_offers)
        f_inital_fixtures.write(data_offer_years)
        f_inital_fixtures.write(data_offer_enrollments)
        f_inital_fixtures.write(data_learning_unit_enrollments)
        f_inital_fixtures.write(data_session_exams)
        f_inital_fixtures.write(data_exam_enrollments)
        f_inital_fixtures.write(data_external_offers)
        f_inital_fixtures.write(data_group_element_years)
        f_inital_fixtures.write(data_learning_class_years)
        f_inital_fixtures.write(data_learning_unit_components)
        f_inital_fixtures.write(data_learning_unit_component_classes)
        f_inital_fixtures.write(data_offer_year_calendars)
        f_inital_fixtures.write(data_offer_year_domains)
        f_inital_fixtures.write(data_tutors)

        # Attribution
        f_inital_fixtures.write(data_attributions)
        f_inital_fixtures.write(data_attribution_charges)

        # Common
        f_inital_fixtures.write(data_message_templates)

    return HttpResponse(status=200)


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
