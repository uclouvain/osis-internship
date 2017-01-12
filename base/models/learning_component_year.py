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
from base.enums.learning_component_year_type import YEAR_TYPE
from django.contrib import admin

class LearningComponentYearAdmin(admin.ModelAdmin):
    list_display = ('learning_container_year', 'learning_component', 'title', 'acronym', 'credit_number', 'hour_volume','term')
    fieldsets = ((None, {'fields': ('learning_container_year', 'learning_component', 'title', 'acronym',
                                    'credit_number', 'hour_volume','term')}),)
    search_fields = ['acronym']


class LearningComponentYear(models.Model):
    learning_container_year = models.ForeignKey('LearningContainerYear')
    learning_component = models.ForeignKey('LearningComponent')
    title = models.CharField(max_length=255)
    acronym = models.CharField(max_length=3)
    credit_number = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hour_volume = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    term = models.CharField(max_length=1)

    def save(self, *args, **kwargs):
        if self.learning_container_year.learning_container != self.learning_component.learning_container:
            raise AttributeError("Learning container year and learning component have different learning containers.")

        super(LearningComponentYear, self).save()

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.title)

    class Meta:
        permissions = (
            ("can_access_learningunitcomponentyear", "Can access learning unit component year"),
        )


def find_by_id(learning_component_year_id):
    return LearningComponentYear.objects.get(pk=learning_component_year_id)
