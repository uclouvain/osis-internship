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
from django.contrib.auth.decorators import login_required, user_passes_test
from faker import Faker
import random


MAX_NUMBER_ROW_PERSON = 100
MAX_ROW_NUMBER = 500
CMS_MAX_ROW_NUMBER = 100
fake = Faker()


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('base.is_administrator'))
def make_fixtures(request):
    list_objects = []

    list_objects += build_auth()

    users = de_identifying_users()
    list_objects.extend(users)

    list_objects += build_reference()

    persons = de_identifying_persons(users)
    list_objects.extend(persons)

    list_objects += de_identifying_person_addresses(persons)

    academic_years = get_academic_years()
    list_objects.extend(academic_years)

    list_objects += build_organizations()

    list_objects += mdl_base.campus.Campus.objects.all()

    list_objects.extend(mdl_base.education_group.EducationGroup.objects.all())

    list_objects.extend(mdl_base.offer_type.OfferType.objects.all())

    education_group_years = mdl_base.education_group_year.EducationGroupYear.objects.all()
    list_objects.extend(education_group_years)

    learning_container_years_all = get_learning_container_years(academic_years)

    entities = get_entities(learning_container_years_all)

    list_objects.extend(entities)

    list_objects.extend(learning_container_years_all)

    learning_containers = get_learning_containers(learning_container_years_all)
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

    list_objects += build_entity_managers(persons, structures)

    list_objects += build_entity_versions(entities)

    learning_units = mdl_base.learning_unit.LearningUnit.objects.filter(learning_container__in=learning_containers)[:MAX_ROW_NUMBER]
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

    list_objects += build_offers(offer_years)

    offer_enrollments = mdl_base.offer_enrollment.OfferEnrollment.objects.filter(offer_year__in=offer_years,
                                                                                 student__in=students)
    list_objects.extend(offer_enrollments)

    learning_unit_enrollments = mdl_base.learning_unit_enrollment.LearningUnitEnrollment.objects.filter(
        learning_unit_year__in=learning_unit_years,
        offer_enrollment__in=offer_enrollments)
    list_objects.extend(learning_unit_enrollments)

    list_objects += build_exam(learning_unit_enrollments, learning_unit_years, offer_years)

    list_objects += build_group_element_years(education_group_years, learning_unit_years)

    learning_class_years = mdl_base.learning_class_year.LearningClassYear.objects.filter(
        learning_component_year__in=learning_component_years)
    list_objects.extend(learning_class_years)

    learning_unit_components = mdl_base.learning_unit_component.LearningUnitComponent.objects.filter(
        learning_unit_year__in=learning_unit_years,
        learning_component_year__in=learning_component_years)
    list_objects.extend(learning_unit_components)

    list_objects += build_learning_unit_component_classes(learning_class_years, learning_unit_components)

    list_objects += create_offers_details(offer_years, academic_years)

    list_objects += build_attributions(learning_unit_components, learning_unit_years, persons)

    list_objects += build_osis_common()

    list_objects += build_cms()

    response = HttpResponse(serializers.serialize('json', list_objects), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="initial_data.json"'

    return response


def build_entity_versions(entities):
    entity_versions = mdl_base.entity_version.EntityVersion.objects.filter(entity__in=entities)
    return entity_versions


def build_entity_managers(persons, structures):
    entity_managers_person = []
    entity_managers = mdl_base.entity_manager.EntityManager.objects.filter(person__in=persons)
    if entity_managers:
        entity_managers = mdl_base.entity_manager.EntityManager.objects.all()
        if entity_managers:
            entity_managers_person = create_fake_person_for_entity_manager(persons)
            entity_managers = create_fake_entity_manager(entity_managers_person, structures)

    return entity_managers_person + entity_managers


def build_group_element_years(education_group_years, learning_unit_years):
    group_element_years = mdl_base.group_element_year.GroupElementYear.objects.filter(
        parent__in=education_group_years,
        child_branch__in=education_group_years,
        child_leaf=education_group_years,
        learning_unit_year__in=learning_unit_years)
    return group_element_years


def build_learning_unit_component_classes(learning_class_years, learning_unit_components):
    learning_unit_component_classes = mdl_base.learning_unit_component_class.LearningUnitComponentClass.objects.filter(
        learning_unit_component__in=learning_unit_components,
        learning_class_year__in=learning_class_years)
    return learning_unit_component_classes


def build_osis_common():
    return mdl_common.message_template.MessageTemplate.objects.all()


def build_reference():
    return list(mdl_reference.currency.Currency.objects.all()) + \
           list(mdl_reference.continent.Continent.objects.all()) + \
           list(mdl_reference.decree.Decree.objects.all()) + \
           list(mdl_reference.language.Language.objects.all())


def build_auth():
    return list(Permission.objects.all()) + list(Group.objects.all())


def build_cms():
    text_labels = mdl_cms.text_label.TextLabel.objects.all()[:CMS_MAX_ROW_NUMBER]
    translated_texts = mdl_cms.translated_text.TranslatedText.objects.filter(text_label__in=text_labels)
    translated_text_labels = mdl_cms.translated_text_label.TranslatedTextLabel.objects \
        .filter(text_label__in=text_labels)
    return list(text_labels) + list(translated_texts) + list(translated_text_labels)


def build_attributions(learning_unit_components, learning_unit_years, persons):
    tutors = mdl_base.tutor.Tutor.objects.filter(person__in=persons)

    attributions = mdl_attribution.attribution.Attribution.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                          tutor__in=tutors)

    attribution_charges = mdl_attribution.attribution_charge.AttributionCharge.objects.filter(
        attribution__in=attributions,
        learning_unit_component__in=learning_unit_components)

    return list(tutors) + list(attributions) + list(attribution_charges)


def build_exam(learning_unit_enrollments, learning_unit_years,  offer_years):
    session_exams = mdl_base.session_exam.SessionExam.objects.filter(learning_unit_year__in=learning_unit_years,
                                                                     offer_year__in=offer_years)

    exam_enrollments = mdl_base.exam_enrollment.ExamEnrollment.objects.filter(
        session_exam__in=session_exams,
        learning_unit_enrollment__in=learning_unit_enrollments)
    return list(session_exams) + list(exam_enrollments)


def build_offers(offer_years):
    return list({oy.offer for oy in offer_years})


def get_learning_containers(learning_container_years_all):
    return list([lc.learning_container for lc in learning_container_years_all])


def get_learning_container_years(academic_years):
    learning_container_years_all = []
    # to have data concerning different years
    for ay in academic_years:
        learning_container_years = mdl_base.learning_container_year.LearningContainerYear.objects.filter(
            academic_year=ay)[:MAX_ROW_NUMBER]
        learning_container_years_all.extend(learning_container_years)
    return learning_container_years_all


def get_academic_years():
    min_year_bound = mdl_base.academic_year.current_academic_year().year - 1
    max_year_bound = mdl_base.academic_year.current_academic_year().year + 1
    academic_years = mdl_base.academic_year.AcademicYear.objects.filter(year__gte=min_year_bound,
                                                                        year__lte=max_year_bound)
    return academic_years


def build_organizations():
    organizations = mdl_base.organization.Organization.objects.all()
    organization_addresses = mdl_base.organization_address.OrganizationAddress.objects.all()
    return list(organizations) + list(organization_addresses)


def create_offers_details(offer_years, academic_years):
    academic_calendars = mdl_base.academic_calendar.AcademicCalendar.objects.filter(academic_year__in=academic_years)

    offer_year_calendars = mdl_base.offer_year_calendar.OfferYearCalendar.objects.filter(
        academic_calendar__in=academic_calendars,
        offer_year__in=offer_years)

    domains = mdl_reference.domain.Domain.objects.all()

    grade_types = mdl_reference.grade_type.GradeType.objects.all()

    external_offers = mdl_base.external_offer.ExternalOffer.objects.filter(domain__in=domains,
                                                                           grade_type__in=grade_types,
                                                                           offer_year__in=offer_years)

    offer_year_domains = mdl_base.offer_year_domain.OfferYearDomain.objects.filter(domain__in=domains,
                                                                                   offer_year__in=offer_years)

    return list(academic_calendars) + list(offer_year_calendars) + list(domains) + list(grade_types) + \
           list(external_offers) + list(offer_year_domains)


def de_identifying_users():
    users = User.objects.all()[:50]
    for user in users:
        user.lastname = fake.last_name()
    return users


def de_identifying_persons(users):
    persons = get_users_persons(users)
    persons += get_students_persons(persons)
    persons += get_tutors_persons(persons)
    for a_person in persons:
        a_person.last_name = fake.last_name()
        a_person.first_name = fake.first_name()
        if a_person.global_id:
            a_person.global_id = a_person.global_id[::-1]
        a_person.email = fake.email()
    return persons


def get_users_persons(users):
    return list(mdl_base.person.Person.objects.select_related('user').filter(id__in=users))


def get_tutors_persons(persons):
    if persons:
        tutors = mdl_base.tutor.Tutor.objects.exclude(person__in=persons)[:MAX_NUMBER_ROW_PERSON]
        return [t.person for t in tutors]
    return []


def get_students_persons(persons):
    if persons:
        students = mdl_base.student.Student.objects.exclude(person__in=persons)[:MAX_NUMBER_ROW_PERSON]
        return [stud.person for stud in students]
    return []


def de_identifying_person_addresses(persons):
    person_addresses = []
    countries = mdl_reference.country.Country.objects.all()

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
    return list(countries) + list(person_addresses)


def find_person_max_id(persons):
    if persons:
        return max(person.id for person in persons)
    return 0


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


def get_entities(learning_container_years_all):
    entity_ids = mdl_base.entity_container_year.EntityContainerYear.objects.filter(learning_container_year__in=learning_container_years_all)\
        .order_by('entity').distinct('entity').values_list('entity', flat=True)

    return mdl_base.entity.Entity.objects.filter(id__in=entity_ids)
