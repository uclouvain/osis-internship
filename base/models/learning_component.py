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


class LearningComponentAdmin(admin.ModelAdmin):
    list_display = ('learning_container', )
    fieldsets = ((None, {'fields': ('learning_container', )}),)
    search_fields = ['acronym']


class LearningComponent(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    learning_container = models.ForeignKey('LearningContainer')


def find_by_id(learning_component_id):
    return LearningComponent.objects.get(pk=learning_component_id)


def find_by_ids(learning_component_ids):
    return LearningComponent.objects.filter(pk__in=learning_component_ids)


def search(acronym=None):
    queryset = LearningComponent.objects

    if acronym:
        queryset = queryset.filter(acronym=acronym)

    return queryset

