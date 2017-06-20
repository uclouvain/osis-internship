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


class EntityComponentYearAdmin(admin.ModelAdmin):
    list_display = ('entity_container_year', 'learning_component_year', 'hourly_volume_total',
                    'hourly_volume_partial')
    search_fields = ['entity_container_year__learning_container_year__acronym']


class EntityComponentYear(models.Model):
    external_id = models.CharField(max_length=255, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    entity_container_year = models.ForeignKey('EntityContainerYear')
    learning_component_year = models.ForeignKey('LearningComponentYear')
    hourly_volume_total = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hourly_volume_partial = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)


    @property
    def hourly_volume_partial_q2(self):
        if self.hourly_volume_total:
            if self.hourly_volume_partial:
                q2 = self.hourly_volume_total - self.hourly_volume_partial
                if q2 <= 0:
                    return None
                else:
                    return q2
        return None


    def __str__(self):
        return u"%s - %s" % (self.entity_container_year, self.learning_component_year)
