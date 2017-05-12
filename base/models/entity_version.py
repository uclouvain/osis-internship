##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
    search_fields = ['entity', 'title', 'acronym', 'entity_type', 'start_date', 'end_date']
    raw_id_fields = ('entity',)


class EntityVersion(models.Model):
    entity = models.ForeignKey('Entity')
    title = models.CharField(max_length=255)
    acronym = models.CharField(max_length=20)
    entity_type = models.CharField(choices=entity_type.ENTITY_TYPES, max_length=50, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

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
    try:
        if date is None:
            date = timezone.now()

        entity_version = EntityVersion.objects.get(acronym=acronym,
                                                   start_date__lte=date,
                                                   end_date__gte=date
                                                   )
    except ObjectDoesNotExist:
        return None

    return entity_version
