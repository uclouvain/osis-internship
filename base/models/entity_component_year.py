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


VOLUME_FOR_UNKNOWN_QUADRIMESTER = -1


class EntityComponentYearAdmin(admin.ModelAdmin):
    list_display = ('entity_container_year', 'learning_component_year', 'hourly_volume_total',
                    'hourly_volume_partial')
    search_fields = ['entity_container_year__learning_container_year__acronym']
    raw_id_fields = ('entity_container_year', 'learning_component_year')


class EntityComponentYear(models.Model):
    external_id = models.CharField(max_length=255, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    entity_container_year = models.ForeignKey('EntityContainerYear')
    learning_component_year = models.ForeignKey('LearningComponentYear')
    hourly_volume_total = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hourly_volume_partial = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)


    @property
    def volumes(self):
        if not self.hourly_volume_total:
            return dict.fromkeys(['hourly_volume', 'quadrimester_volume', 'vol_q1', 'vol_q2'], '?')

        if  self.hourly_volume_partial is None:
            return {'hourly_volume': self.hourly_volume_total,
                    'quadrimester_volume': '?',
                    'vol_q1': '?',
                    'vol_q2': '?'}

        if self.unknown_quadrimester():
            return {'hourly_volume': self.hourly_volume_total,
                    'quadrimester_volume': 'Q1|2',
                    'vol_q1': '({})'.format(self.hourly_volume_total),
                    'vol_q2': '({})'.format(self.hourly_volume_total)}

        return {'hourly_volume': self.hourly_volume_total,
                'quadrimester_volume': self.format_nominal_quadrimester(),
                'vol_q1': self.hourly_volume_partial,
                'vol_q2': self.format_volq2()}


    def unknown_quadrimester(self):
        if self.hourly_volume_partial == VOLUME_FOR_UNKNOWN_QUADRIMESTER:
            return True
        return False


    def format_nominal_quadrimester(self):
        if self.hourly_volume_total == self.hourly_volume_partial:
            return 'Q1'
        else:
            if self.hourly_volume_partial == 0:
                return 'Q2'
            else:
                return 'Q1&2'
        return None

    def format_volq2(self):
        vol_q2 = self.hourly_volume_total - self.hourly_volume_partial
        if vol_q2 == 0:
            return '-'
        return vol_q2

    def __str__(self):
        return u"%s - %s" % (self.entity_container_year, self.learning_component_year)


def find_by_entity_container_year(entity_container_yrs, a_learning_component_year):
    return EntityComponentYear.objects.filter(entity_container_year__in=entity_container_yrs,
                                           learning_component_year=a_learning_component_year)
