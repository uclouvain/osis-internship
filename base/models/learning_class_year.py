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


class LearningClassYearAdmin(admin.ModelAdmin):
    list_display = ('learning_component_year', 'learning_class', 'acronym_class_number', 'language', 'term')
    fieldsets = ((None, {'fields': ('learning_component_year', 'learning_class', 'acronym', 'acronym_class_number', 'language', 'term')}),)
    search_fields = ['acronym']


class LearningClassYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    learning_component_year = models.ForeignKey('LearningComponentYear')
    learning_class = models.ForeignKey('LearningClass')
    acronym_class_number = models.CharField(max_length=3)
    language = models.ForeignKey('reference.Language')
    term = models.CharField(max_length=1)

    class Meta:
        permissions = (
            ("can_access_learningclassyear", "Can access learning class year"),
        )


def find_by_id(learning_class_year_id):
    return LearningClassYear.objects.get(pk=learning_class_year_id)


def find_by_ids(learning_unit_year_ids):
    return LearningClassYear.objects.filter(pk__in=learning_unit_year_ids)


def search(acronym=None):
    queryset = LearningClassYear.objects

    if acronym:
        queryset = queryset.filter(acronym=acronym)

    return queryset

