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
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


class EntityLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'child', 'start_date', 'end_date',)
    search_fields = ['parent__id', 'parent__external_id', 'parent__entityversion__acronym',
                     'child__id', 'child__external_id', 'child__entityversion__acronym', 'start_date', 'end_date']
    raw_id_fields = ('parent', 'child',)


class EntityLink(models.Model):
    parent = models.ForeignKey('Entity', related_name='links_to_children')
    child = models.ForeignKey('Entity', related_name='link_to_parent')
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True, null=True)

    def __str__(self):
        return "Parent : {} - Child : {} - {} to {}".format(
            self.parent,
            self.child,
            self.start_date,
            self.end_date
        )

    def save(self, *args, **kwargs):
        if self.can_save_entity_link():
            super(EntityLink, self).save()
        else:
            raise AttributeError('EntityLink invalid parameters')

    def can_save_entity_link(self):
        return self.count_entity_links_same_child_overlapping_dates() == 0 and self.parent != self.child

    def _entity_links_overlapping_dates(self):
        return EntityLink.objects.filter(
            Q(start_date__range=(self.start_date, self.end_date)) |
            Q(end_date__range=(self.start_date, self.end_date)) |
            (
                Q(start_date__lte=self.start_date) & Q(end_date__gte=self.end_date)
            )
        )

    def count_entity_links_same_child_overlapping_dates(self):
        return self._entity_links_overlapping_dates().filter(child=self.child).count()

    def get_upper_entity_link(self):
        try:
            parent = self._entity_links_overlapping_dates().get(child=self.parent)
        except ObjectDoesNotExist:
            return None

        return parent

    def get_upper_hierarchy(self):
        upper_hierarchy = []
        if self.get_upper_entity_link() is not None:
            upper_hierarchy.append(self.get_upper_entity_link())
            upper_hierarchy.extend(self.get_upper_entity_link().get_upper_hierarchy())
        return upper_hierarchy


def search(**kwargs):
    queryset = EntityLink.objects

    if 'parent' in kwargs:
        queryset = queryset.filter(parent__exact=kwargs['parent'])

    if 'child' in kwargs:
        queryset = queryset.filter(child__exact=kwargs['child'])

    if 'start_date' in kwargs:
            queryset = queryset.filter(start_date__exact=kwargs['start_date'])

    if 'end_date' in kwargs:
            queryset = queryset.filter(end_date__exact=kwargs['end_date'])

    return queryset


def count(**kwargs):
    return search(**kwargs).count()
