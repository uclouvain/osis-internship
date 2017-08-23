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
from django.db import models

from base import models as mdl
from base.models.enums import entity_container_year_link_type


class LearningUnitYearWithContext:
    def __init__(self, **kwargs):
        self.learning_unit_year = kwargs.get('learning_unit_year')


def get_with_context(**learning_unit_year_data):
    entity_container_prefetch = models.Prefetch(
        'learning_container_year__entitycontaineryear_set',
        queryset=mdl.entity_container_year
        .search(
            link_type=[entity_container_year_link_type.REQUIREMENT_ENTITY,
                       entity_container_year_link_type.ALLOCATION_ENTITY,
                       entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1,
                       entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2]
        )
        .prefetch_related(
            models.Prefetch('entity__entityversion_set', to_attr='entity_versions')
        ),
        to_attr='entity_containers_year'
    )

    learning_component_prefetch = models.Prefetch(
        'learningunitcomponent_set',
        queryset=mdl.learning_unit_component.LearningUnitComponent.objects.all()
        .order_by('learning_component_year__type', 'learning_component_year__acronym')
        .select_related('learning_component_year')
        .prefetch_related(
            models.Prefetch('learning_component_year__entitycomponentyear_set',
                            queryset=mdl.entity_component_year.EntityComponentYear.objects.all()
                            .select_related('entity_container_year'),
                            to_attr='entity_components_year'
                            )
        ),
        to_attr='learning_unit_components'
    )

    learning_units = mdl.learning_unit_year.search(**learning_unit_year_data) \
        .select_related('academic_year', 'learning_container_year') \
        .prefetch_related(entity_container_prefetch) \
        .prefetch_related(learning_component_prefetch) \
        .order_by('academic_year__year', 'acronym')

    learning_units = [_append_latest_entities(learning_unit) for learning_unit in learning_units]
    learning_units = [_append_components(learning_unit) for learning_unit in learning_units]

    return learning_units


def _append_latest_entities(learning_unit):
    learning_unit.entities = {}
    if learning_unit.learning_container_year and learning_unit.learning_container_year.entity_containers_year:
        for entity_container_yr in learning_unit.learning_container_year.entity_containers_year:
            link_type = entity_container_yr.type
            latest_version = _get_latest_entity_version(entity_container_yr)
            learning_unit.entities[link_type] = latest_version
    return learning_unit


def _get_latest_entity_version(entity_container_year):
    entity_version = None
    if entity_container_year.entity.entity_versions:
        entity_version = entity_container_year.entity.entity_versions[-1]
    return entity_version


def _append_components(learning_unit):
    learning_unit.components = []
    if learning_unit.learning_unit_components:
        for learning_unit_component in learning_unit.learning_unit_components:
            learning_unit.components.append(learning_unit_component.learning_component_year)
    return learning_unit
