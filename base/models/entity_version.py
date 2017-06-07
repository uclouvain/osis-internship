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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from base.models.enums import entity_type


class EntityVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity', 'acronym', 'title', 'entity_type', 'start_date', 'end_date',)
    search_fields = ['entity__id', 'entity__external_id', 'title', 'acronym', 'entity_type', 'start_date', 'end_date']
    raw_id_fields = ('entity',)


class EntityVersion(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    entity = models.ForeignKey('Entity')
    title = models.CharField(max_length=255)
    acronym = models.CharField(max_length=20)
    entity_type = models.CharField(choices=entity_type.ENTITY_TYPES, max_length=50, db_index=True)
    parent = models.ForeignKey('Entity', related_name='parent_of', blank=True, null=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True, blank=True, null=True)

    def __str__(self):
        return "{} ({} - {} - {} to {})".format(
            self.acronym,
            self.title,
            self.entity_type,
            self.start_date,
            self.end_date
        )

    def save(self, *args, **kwargs):
        if self.can_save_entity_version():
            super(EntityVersion, self).save()
        else:
            raise AttributeError('EntityVersion invalid parameters')

    def can_save_entity_version(self):
        return self.count_entity_versions_same_entity_overlapping_dates() == 0 and \
               self.count_entity_versions_same_acronym_overlapping_dates() == 0

    def search_entity_versions_with_overlapping_dates(self):
        return EntityVersion.objects.filter(
                Q(start_date__range=(self.start_date, self.end_date)) |
                Q(end_date__range=(self.start_date, self.end_date)) |
                (
                    Q(start_date__lte=self.start_date) & Q(end_date__gte=self.end_date)
                )
            )

    def count_entity_versions_same_entity_overlapping_dates(self):
        return self.search_entity_versions_with_overlapping_dates().filter(entity=self.entity).count()

    def count_entity_versions_same_acronym_overlapping_dates(self):
        return self.search_entity_versions_with_overlapping_dates().filter(acronym=self.acronym).count()


def find(acronym, date=None):
    if date is None:
        date = timezone.now()
    try:
        entity_version = EntityVersion.objects.get(acronym=acronym,
                                                   start_date__lte=date,
                                                   end_date__gte=date
                                                   )
    except ObjectDoesNotExist:
        return None

    return entity_version


def search(**kwargs):
    queryset = EntityVersion.objects

    if 'entity' in kwargs:
        queryset = queryset.filter(entity__exact=kwargs['entity'])

    if 'title' in kwargs:
        queryset = queryset.filter(title__exact=kwargs['title'])

    if 'acronym' in kwargs:
        queryset = queryset.filter(acronym__exact=kwargs['acronym'])

    if 'entity_type' in kwargs:
        queryset = queryset.filter(entity_type__exact=kwargs['entity_type'])

    if 'start_date' in kwargs:
            queryset = queryset.filter(start_date__exact=kwargs['start_date'])

    if 'end_date' in kwargs:
            queryset = queryset.filter(end_date__exact=kwargs['end_date'])

    return queryset


def count(**kwargs):
    return search(**kwargs).count()
