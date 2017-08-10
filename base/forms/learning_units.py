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
from django import forms
from django.db.models import Prefetch, Count

from base import models as mdl
from django.core.exceptions import ValidationError

from base.models.enums import entity_container_year_link_type

MAX_ROW_NUMBERS = 1000

class LearningUnitYearForm(forms.Form):
    academic_year_id = forms.CharField(max_length=10, required=False)
    container_type = status = forms.CharField(required=False)
    acronym = title = requirement_entity_acronym = forms.CharField(widget=forms.TextInput(attrs={'size': '10', 'class': 'form-control'}),
                                                                   max_length=20, required=False)
    with_entity_subordinated = forms.BooleanField(required=False)

    def clean_acronym(self):
        MIN_ACRONYM_LENGTH = 3
        data_cleaned = self.cleaned_data.get('acronym')
        data_cleaned = _treat_empty_or_str_none_as_none(data_cleaned)
        if data_cleaned and len(data_cleaned) < MIN_ACRONYM_LENGTH:
            raise ValidationError('LU_ERRORS_INVALID_SEARCH')
        return data_cleaned

    def clean_academic_year_id(self):
        data_cleaned = self.cleaned_data.get('academic_year_id')
        if data_cleaned == 'all':
            return None
        return data_cleaned

    def clean_requirement_entity_acronym(self):
        data_cleaned = self.cleaned_data.get('requirement_entity_acronym')
        if data_cleaned:
            return data_cleaned.upper()
        return data_cleaned

    def clean(self):
        clean_data = _clean_data(self.cleaned_data)
        is_valid_search(**clean_data)
        return clean_data

    def get_learning_units(self):
        clean_data = self.cleaned_data

        entity_container_prefetch = Prefetch('learning_container_year__entitycontaineryear_set',
                                             queryset=mdl.entity_container_year.search(
                                                        link_type=[entity_container_year_link_type.ALLOCATION_ENTITY,
                                                                   entity_container_year_link_type.REQUIREMENT_ENTITY])
                                                        .prefetch_related(
                                                            Prefetch('entity__entityversion_set', to_attr='entity_versions')
                                                        ),
                                             to_attr='entity_containers_year')

        clean_data['learning_container_year_id'] = _get_filter_learning_container_ids(clean_data)
        learning_units = mdl.learning_unit_year.search(**clean_data)\
                                               .select_related('academic_year', 'learning_container_year')\
                                               .prefetch_related(entity_container_prefetch)\
                                               .order_by('academic_year__year', 'acronym')[:MAX_ROW_NUMBERS]

        return [_append_latest_entities(learning_unit) for learning_unit in learning_units]


def is_valid_search(**search_filter):
    MINIMUM_FILTER = 2

    if sum(1 for value in search_filter.values() if value) < MINIMUM_FILTER:
        raise ValidationError('LU_ERRORS_INVALID_SEARCH')


def _clean_data(datas_to_clean):
    return {key: _treat_empty_or_str_none_as_none(value) for (key, value) in datas_to_clean.items()}


def _treat_empty_or_str_none_as_none(data):
    return None if not data or data == "NONE" else data


def _get_filter_learning_container_ids(filter_data):
    requirement_entity_acronym = filter_data.get('requirement_entity_acronym')
    with_entity_subordinated = filter_data.get('with_entity_subordinated', False)

    if requirement_entity_acronym:
        entity_ids = _get_entities_ids(requirement_entity_acronym, with_entity_subordinated)
        return list(mdl.entity_container_year.search(link_type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                                     entity_id=entity_ids)\
                                             .values_list('learning_container_year', flat=True).distinct())
    return None


def _get_entities_ids(requirement_entity_acronym, with_entity_subordinated):
    entities_ids = set()
    entity_versions = mdl.entity_version.search(acronym=requirement_entity_acronym)
    entities_ids |= set(entity_versions.values_list('entity', flat=True).distinct())

    if with_entity_subordinated:
        for entity_version in entity_versions:
            all_descendants = entity_version.find_descendants(entity_version.start_date)
            entities_ids |= {descendant.entity.id for descendant in all_descendants}
    return list(entities_ids)


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