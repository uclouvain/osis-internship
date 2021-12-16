##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class InternshipSpecialityAdmin(SerializableModelAdmin):
    list_display = ('name', 'acronym', 'mandatory', 'cohort', 'sequence', 'selectable', 'is_subspecialty')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'sequence', 'mandatory', 'cohort', 'selectable', 'parent')}),)
    list_filter = ('cohort', 'selectable', 'parent')


class InternshipSpeciality(SerializableModel):
    name = models.CharField(max_length=125)
    acronym = models.CharField(max_length=125, null=True, blank=True)
    mandatory = models.BooleanField(default=False)
    sequence = models.IntegerField(blank=True, null=True)
    cohort = models.ForeignKey('internship.Cohort', on_delete=models.CASCADE)
    selectable = models.BooleanField(default=True)

    parent = models.ForeignKey("InternshipSpeciality", on_delete=models.CASCADE, null=True, blank=True)

    def acronym_with_sequence(self):
        if self.sequence:
            return "{}{}".format(self.acronym, self.sequence)
        else:
            return self.acronym

    def is_subspecialty(self):
        return self.parent is not None

    # enable list display as logo in admin
    is_subspecialty.boolean = True

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class IsSubspecialtyFilter(admin.SimpleListFilter):
    title = 'is_subspecialty'
    parameter_name = 'is_subspecialty'

    def lookups(self, request, model_admin):
        return (('Yes', 'Yes'),('No', 'No'),)

    def queryset(self, request, queryset):
        return queryset.filter(parent__is_null=self.value() == 'Yes')


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipSpeciality.objects.filter(**kwargs).order_by('acronym', 'name')


def find_all(cohort):
    return InternshipSpeciality.objects.filter(cohort=cohort).order_by('acronym', 'name')


def find_by_cohort(cohort):
    return InternshipSpeciality.objects.filter(cohort=cohort).order_by("name")


def acronym_exists(cohort, acronym):
    return InternshipSpeciality.objects.filter(cohort=cohort, acronym__iexact=acronym).exists()


def get_by_id(speciality_id):
    try:
        return InternshipSpeciality.objects.get(pk=speciality_id)
    except ObjectDoesNotExist:
        return None


def set_speciality_unique(specialities):
    specialities_size = len(specialities)
    for element in specialities:
        name = element.name.split()
        size = len(name)
        if name[size - 1].isdigit():
            temp_name = ""
            for x in range(0, size - 1):
                temp_name += name[x] + " "
            element.name = temp_name

    item_deleted = 0
    for x in range(1, specialities_size):
        if specialities[x - 1 - item_deleted] != 0:
            if specialities[x].name == specialities[x - 1 - item_deleted].name:
                specialities[x] = 0
                item_deleted += 1

    specialities = [x for x in specialities if x != 0]
    return specialities

