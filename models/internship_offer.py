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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class InternshipOfferAdmin(SerializableModelAdmin):
    list_display = ('organization', 'speciality', 'title', 'maximum_enrollments', 'master', 'selectable', 'cohort')
    fieldsets = ((None, {'fields': ('organization', 'speciality', 'title', 'maximum_enrollments', 'master',
                                    'selectable', 'cohort')}),)
    raw_id_fields = ('organization', 'speciality')
    list_filter = ('cohort', 'speciality', 'organization')
    search_fields = ['organization__name', 'organization__reference', 'speciality__name', 'master']


class InternshipOffer(SerializableModel):
    organization = models.ForeignKey(
        'internship.Organization', on_delete=models.CASCADE, verbose_name=_('Organization')
    )
    speciality = models.ForeignKey(
        'internship.InternshipSpeciality', null=True, on_delete=models.CASCADE, verbose_name=_('Speciality')
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    maximum_enrollments = models.IntegerField(verbose_name=_('Maximum enrollments'))
    master = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Master'))
    selectable = models.BooleanField(default=True, verbose_name=_('Selectable'))
    cohort = models.ForeignKey('internship.Cohort', on_delete=models.CASCADE, verbose_name=_('Cohort'))

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ("is_internship_manager", "Is Internship Manager"),
            ("can_access_internship", "Can access internships"),
        )


def find_internships(cohort):
    return InternshipOffer.objects.filter(cohort=cohort)


def find_mandatory_internships(cohort):
    return _apply_constraints(find_internships(cohort).filter(speciality__mandatory=1))


def search(**kwargs):
    return _apply_constraints(InternshipOffer.objects.filter(**kwargs))


def _apply_constraints(resultset):
    return resultset.select_related("organization", "speciality") \
        .order_by('speciality__acronym', 'speciality__name', 'organization__reference')


def find_by_speciality(speciality):
    return InternshipOffer.objects.filter(speciality=speciality).order_by("organization__reference")


def find_by_id(a_id):
    try:
        return InternshipOffer.objects.get(pk=a_id)
    except ObjectDoesNotExist:
        return None
