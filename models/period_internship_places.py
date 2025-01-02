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
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class PeriodInternshipPlacesAdmin(SerializableModelAdmin):
    list_display = ('period', 'internship_offer', 'number_places')
    fieldsets = ((None, {'fields': ('period', 'internship_offer', 'number_places')}),)
    raw_id_fields = ('period', 'internship_offer')
    list_filter = ('period__cohort',)
    search_fields = ['internship_offer__organization__name', 'internship_offer__organization__reference']


class PeriodInternshipPlaces(SerializableModel):
    period = models.ForeignKey('internship.Period', on_delete=models.CASCADE, verbose_name=_('Period'))
    internship_offer = models.ForeignKey(
        'internship.InternshipOffer', on_delete=models.CASCADE, verbose_name=_('Internship Offer')
    )
    number_places = models.IntegerField(verbose_name=_('Number places'))

    def __str__(self):
        return u"%s (%s)" % (self.internship_offer, self.period)


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return PeriodInternshipPlaces.objects.filter(**kwargs).select_related("period", "internship_offer")


def find_by_internship_offer(internship_offer):
    return PeriodInternshipPlaces.objects.filter(internship_offer=internship_offer)


def update_maximum_enrollments(internship_offer):
    places = find_by_internship_offer(internship_offer)
    maximum_enrollments = 0
    for place in places:
        maximum_enrollments += place.number_places
    internship_offer.maximum_enrollments = maximum_enrollments
    internship_offer.save()
