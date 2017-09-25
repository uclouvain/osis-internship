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
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class AttributionChargeAdmin(SerializableModelAdmin):
    list_display = ('attribution', 'learning_unit_component', 'allocation_charge')
    raw_id_fields = ('attribution', 'learning_unit_component')
    search_fields = ['attribution__tutor__person__first_name', 'attribution__tutor__person__last_name',
                     'attribution__tutor__person__global_id',
                     'learning_unit_component__learning_unit_year__acronym']
    list_filter = ('learning_unit_component__type',)


class AttributionCharge(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    attribution = models.ForeignKey('Attribution')
    learning_unit_component = models.ForeignKey('base.LearningUnitComponent')
    allocation_charge = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return u"%s" % str(self.attribution)


def find_by_component_type(an_attribution=None, a_learning_unit_component_type=None):
    return AttributionCharge.objects.filter(attribution=an_attribution,
                                            learning_unit_component__learning_unit_year=an_attribution.learning_unit_year,
                                            learning_unit_component__type=a_learning_unit_component_type).first()
