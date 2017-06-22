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
from django.contrib import admin
from django.db.models import Prefetch

from base.models import entity_version
from base.models.enums import entity_container_year_link_type


class EntityContainerYearAdmin(admin.ModelAdmin):
    list_display = ('learning_container_year', 'entity', 'type')
    fieldsets = ((None, {'fields': ('entity',)}),)
    search_fields = ['learning_container_year__acronym', 'type']


class EntityContainerYear(models.Model):
    external_id = models.CharField(max_length=255, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    entity = models.ForeignKey('Entity')
    learning_container_year = models.ForeignKey('LearningContainerYear')
    type = models.CharField(max_length=35, choices=entity_container_year_link_type.ENTITY_CONTAINER_YEAR_LINK_TYPES)

    class Meta:
        unique_together = ('entity', 'learning_container_year', 'type',)

    def __str__(self):
        return u"%s - %s - %s" % (self.entity, self.learning_container_year, self.type)


def find_entities(learning_container_year, link_type=None):
    lcy_start_date = learning_container_year.academic_year.start_date

    queryset = EntityContainerYear.objects.filter(learning_container_year=learning_container_year)
    if isinstance(link_type, list):
        queryset = queryset.filter(type__in=link_type)
    elif link_type:
        queryset = queryset.filter(type=link_type)

    entity_container_years = queryset.select_related('learning_container_year__academic_year', 'entity')\
                                     .prefetch_related(
                                            Prefetch('entity__entityversion_set',
                                                     queryset=entity_version.find_latest_version(lcy_start_date),
                                                     to_attr="entity_versions")
                                    )

    return {ecy.type: _get_latest_entity_version(ecy) for ecy in entity_container_years}


def _get_latest_entity_version(entity_container_year):
    entity_version = None
    if entity_container_year.entity.entity_versions:
        entity_version = entity_container_year.entity.entity_versions[-1]
    return entity_version


def find_requirement_entity(learning_container_year):
    results = find_entities(learning_container_year, entity_container_year_link_type.REQUIREMENT_ENTITY)
    return next(iter(results.values()), None)


def find_allocation_entity(learning_container_year):
    results = find_entities(learning_container_year, entity_container_year_link_type.ALLOCATION_ENTITY)
    return next(iter(results.values()), None)


def find_all_additional_requirement_entities(learning_container_year):
    results = find_entities(learning_container_year, [entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1,
                                                      entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2])
    return next(iter(results.values()), None)


def find_by_learning_container_year(a_learning_container_year, a_entity_container_year_link_type):
    return EntityContainerYear.objects.filter(learning_container_year=a_learning_container_year,
                                              type=a_entity_container_year_link_type)

