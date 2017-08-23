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
from base import models as mdl_base
from reference import models as mdl_reference
from attribution import models as mdl_attribution
from cms import models as mdl_cms
from osis_common import models as mdl_common
from django.http import HttpResponse
from base.tests.factories.person_address import PersonAddressFactory
import string
from django.contrib.auth.decorators import login_required, user_passes_test
import string
import os
from faker import Faker
import random

MAX_NUMBER_ROW_PERSON = 500
MAX_ROW_NUMBER = 1000
CMS_MAX_ROW_NUMBER = 500
fake = Faker()


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('base.is_administrator'))
def make_fixtures(request):
    list_objects = []
    # Auth
    list_objects.extend(Permission.objects.all())
    list_objects.extend(Group.objects.all())
    #
    users = de_identifying_users()
    list_objects.extend(users)
    #
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
    min_year_bound = mdl_base.academic_year.current_academic_year().year - 1
    max_year_bound = mdl_base.academic_year.current_academic_year().year + 1
    academic_years = mdl_base.academic_year.AcademicYear.objects.filter(year__gte=min_year_bound,
                                                                        year__lte=max_year_bound)
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
    # to have data concerning different years
    for ay in academic_years:
        learning_container_years = mdl_base.learning_container_year.LearningContainerYear.objects.filter(
            academic_year=ay)[:MAX_ROW_NUMBER]
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
    if entity_managers is None or len(entity_managers) == 0:
        entity_managers = mdl_base.entity_manager.EntityManager.objects.all()

        if entity_managers is None or len(entity_managers) == 0:

            entity_managers_person = create_fake_person_for_entity_manager(persons)
            list_objects.extend(entity_managers_person)
            entity_managers = create_fake_entity_manager(entity_managers_person, structures)

    list_objects.extend(entity_managers)

    entity_versions = mdl_base.entity_version.EntityVersion.objects.all()
    list_objects.extend(entity_versions)
    # Strang after synchro, the field learning_container_id is empty in the table learning_unit
    # The problem is going to be corrected in the ticket legacy #665
    learning_units = mdl_base.learning_unit.LearningUnit.objects.filter(learning_container__in=learning_containers)
    list_objects.extend(learning_units)

    # To correct the preceding problem
    if learning_units is None or len(learning_units) == 0:
        learning_units = mdl_base.learning_unit.LearningUnit.objects.all()[:MAX_ROW_NUMBER]
        list_objects.extend(learning_units)
    #
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

    # Cms
    text_labels = mdl_cms.text_label.TextLabel.objects.all()[:CMS_MAX_ROW_NUMBER]
    list_objects.extend(text_labels)

    translated_texts = mdl_cms.translated_text.TranslatedText.objects.filter(text_label__in=text_labels)
    list_objects.extend(translated_texts)

    translated_text_labels = mdl_cms.translated_text_label.TranslatedTextLabel.objects\
        .filter(text_label__in=text_labels)
    list_objects.extend(translated_text_labels)

    response = HttpResponse(serializers.serialize('json', list_objects), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="initial_data.json"'

    return response


def de_identifying_users():
    users = User.objects.all()[:50]
    for user in users:
        user.lastname = fake.last_name()
    return users


def de_identifying_persons(users):
    persons = []
    get_users_persons(persons, users)
    get_students_persons(persons)
    get_tutors_persons(persons)
    for a_person in persons:
        a_person.last_name = fake.last_name()
        a_person.first_name = fake.first_name()
        if a_person.global_id:
            a_person.global_id = a_person.global_id[::-1]
        a_person.email = fake.email()
    return persons


def get_users_persons(persons_param, users):
    persons = persons_param
    for a_user in users:
        p = mdl_base.person.find_by_user(a_user)
        if p:
            persons.append(p)
    return persons


def get_tutors_persons(persons_param):
    persons = persons_param
    tutors = mdl_base.tutor.Tutor.objects.exclude(person__in=persons)[:MAX_NUMBER_ROW_PERSON]
    for t in tutors:
        if t.person not in persons:
            persons.append(t.person)
    return persons


def get_students_persons(persons_param):
    persons = persons_param
    if persons:
        students = mdl_base.student.Student.objects.filter(person__in=persons)[:MAX_NUMBER_ROW_PERSON]
        for stud in students:
            if stud.person not in persons:
                persons.append(stud.person)
    return persons


def de_identifying_person_addresses(persons, countries_param):
    person_addresses = []
    countries = countries_param
    for a_person in persons:
        if a_person:
            if countries:
                country_random = countries[random.randint(0, len(countries)-1)]
                person_adr = PersonAddressFactory(person=a_person,
                                                  country=country_random)
            else:
                person_adr = PersonAddressFactory(person=a_person)
                countries = [person_adr.country]

            person_addresses.append(person_adr)
    return person_addresses


def find_person_max_id(persons):
    max_id = 0
    for p in persons:
        if p.id > max_id:
            max_id = p.id
    return max_id


def create_fake_person_for_entity_manager(persons):
    max_id = int(find_person_max_id(persons))
    cpt = 0
    fake_list = []

    while cpt < 5:
        max_id += 1
        fake_list.append(mdl_base.person.Person(last_name=fake.last_name(),
                                                first_name=fake.first_name(),
                                                employee=True,
                                                user=None,
                                                id=max_id))
        cpt += 1
    return fake_list


def create_fake_entity_manager(persons, structures):
    fake_list = []
    if persons and structures:
        cpt = 0
        new_id = 1
        while cpt < 5 and cpt < len(persons):
            fake_list.append(mdl_base.entity_manager.EntityManager(person=persons[cpt],
                                                                   structure=structures[random.randint(0, len(structures)-1)],
                                                                   id=new_id))
            new_id = new_id + 1
            cpt = cpt + 1
    return fake_list
