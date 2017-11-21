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
from django.core.exceptions import ObjectDoesNotExist


class InternshipSpecialityAdmin(SerializableModelAdmin):
    list_display = ('learning_unit', 'name', 'acronym', 'mandatory', 'cohort', 'sequence')
    fieldsets = ((None, {'fields': ('learning_unit', 'name', 'acronym', 'sequence', 'mandatory', 'cohort')}),)
    raw_id_fields = ('learning_unit',)


class InternshipSpeciality(SerializableModel):
    learning_unit = models.ForeignKey('base.LearningUnit')
    name = models.CharField(max_length=125, blank=False, null=False)
    acronym = models.CharField(max_length=125, blank=False, null=False)
    mandatory = models.BooleanField(default=False)
    sequence = models.IntegerField(blank=True, null=True)
    cohort = models.ForeignKey('internship.cohort', null=False, on_delete=models.CASCADE)

    def acronym_with_sequence(self):
        if self.sequence:
            return "{}{}".format(self.acronym, self.sequence)
        else:
            return self.acronym

    def __str__(self):
        return self.name


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipSpeciality.objects.filter(**kwargs).select_related("learning_unit").order_by('acronym', 'name')


def find_all(cohort):
    return InternshipSpeciality.objects.filter(cohort=cohort).select_related("learning_unit").order_by('acronym', 'name')


def find_by_cohort(cohort):
    return InternshipSpeciality.objects.filter(cohort=cohort).order_by("name")


def find_non_mandatory():
    return InternshipSpeciality.objects.filter(mandatory=False)\
                                       .select_related("learning_unit")\
                                       .order_by('acronym', 'name')


def find_by_id(speciality_id):
    try:
        return InternshipSpeciality.objects.get(pk=speciality_id)
    except ObjectDoesNotExist:
        return None
