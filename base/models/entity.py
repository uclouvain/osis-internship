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
from django.db import models
from django.contrib import admin
from django.utils import timezone
from base.models.entity_link import EntityLink


class EntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization',)
    search_fields = ['organization']
    raw_id_fields = ('organization',)


class Entity(models.Model):
    organization = models.ForeignKey('Organization', null=True)

    class Meta:
        verbose_name_plural = "entities"

    def __str__(self):
        return "{0} ({1})".format(self.id, self.organization.acronym)

    def _direct_children(self, date=None):
        if date is None:
            date = timezone.now()

        return EntityLink.objects.filter(parent=self,
                                         start_date__lte=date,
                                         end_date__gte=date
                                         )

    def get_direct_children(self, date=None):
        qs = self._direct_children(date).select_related("child")
        return [entity_link.child for entity_link in qs]

    def count_direct_children(self, date=None):
        return self._direct_children(date).count()

    def find_descendants(self, date=None):
        if date is None:
            date = timezone.now()

        descendants = []
        if self.count_direct_children(date) > 0:
            direct_children = self.get_direct_children(date)
            descendants.extend(direct_children)
            for child in direct_children:
                descendants.extend(child.find_descendants(date))

        return descendants


def search(**kwargs):
    queryset = Entity.objects

    if 'acronym' in kwargs:
        queryset = queryset.filter(entityversion__acronym__icontains=kwargs['acronym'])

    if 'entity_type' in kwargs:
        queryset = queryset.filter(entityversion__entity_type__icontains=kwargs['entity_type'])

    if 'version_date' in kwargs:
        queryset = queryset.filter(entityversion__start_date__lte=kwargs['version_date'],
                                   entityversion__end_date__gte=kwargs['version_date'])

    return queryset
