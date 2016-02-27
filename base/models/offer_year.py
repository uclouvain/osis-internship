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

from base.models.offer import find_offer_by_id
from base.models.offer_year_calendar import OfferYearCalendar


class OfferYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    offer = models.ForeignKey('Offer')
    academic_year = models.ForeignKey('AcademicYear')
    acronym = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    structure = models.ForeignKey('Structure')
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', db_index=True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.offer.acronym)

    @property
    def offer_year_children(self):
        """
        To find children
        """
        return OfferYear.objects.filter(parent=self)

    @property
    def offer_year_sibling(self):
        """
        To find other focuses
        """
        if self.parent:
            return OfferYear.objects.filter(parent=self.parent).exclude(id=self.id).exclude()
        return None

    @property
    def is_orientation(self):
        if self.orientation_sibling():
            return True
        else:
            return False

    @property
    def orientation_sibling(self):
        if self.offer:
            offer = find_offer_by_id(self.offer.id)
            return OfferYear.objects.filter(offer=offer, acronym=self.acronym,
                                            academic_year=self.academic_year).exclude(id=self.id)
        return None

    def find_offer_year_calendar(self):
        return OfferYearCalendar.objects.filter(offer_year=self, start_date__isnull=False,
                                                end_date__isnull=False).order_by('start_date',
                                                                                 'academic_calendar__title')


def find_offer_years_by_academic_year(academic_year):
    return OfferYear.objects.filter(academic_year=int(academic_year))


def find_offer_years_by_academic_year_structure(academic_year, structure):
    return OfferYear.objects.filter(academic_year=academic_year, structure=structure).order_by('acronym')


def find_offer_year_by_id(offer_year_id):
    return OfferYear.objects.get(pk=offer_year_id)


def find_all_offers():
    return OfferYear.objects.all()