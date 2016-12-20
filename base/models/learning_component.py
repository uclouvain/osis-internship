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
    list_display = ('learning_container', 'type','title','end_year')
    fieldsets = ((None, {'fields': ('learning_container', 'type','title','end_year')}),)
    search_fields = ['acronym']


class LearningComponent(models.Model):
    learning_container = models.ForeignKey('LearningContainer')
    type = models.CharField(max_length=12)
    title = models.CharField(max_length=20)
    end_date = models.DateField(default=timezone.now, blank=True, null=True)


def find_by_id(learning_component_id):
    return LearningComponent.objects.get(pk=learning_component_id)
