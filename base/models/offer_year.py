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
from django.utils.translation import ugettext_lazy as _
from base.models import offer, structure, program_manager


class OfferYearAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'offer', 'parent', 'title', 'academic_year', 'changed')
    fieldsets = ((None, {'fields': ('offer', 'academic_year', 'structure', 'acronym', 'title', 'parent',
                                    'title_international', 'title_short', 'title_printable', 'grade')}),)
    raw_id_fields = ('offer', 'structure', 'parent')
    search_fields = ['acronym']


GRADE_TYPES = (
    ('BACHELOR', _('bachelor')),
    ('MASTER', _('master')),
    ('DOCTORATE', _('ph_d')))


class OfferYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    offer = models.ForeignKey('Offer')
    academic_year = models.ForeignKey('AcademicYear')
    acronym = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    title_international = models.CharField(max_length=255, blank=True, null=True)
    title_short = models.CharField(max_length=255, blank=True, null=True)
    title_printable = models.CharField(max_length=255, blank=True, null=True)
    structure = models.ForeignKey(structure.Structure)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', db_index=True)
    grade = models.CharField(max_length=20, blank=True, null=True, choices=GRADE_TYPES)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)

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
            off = offer.find_by_id(self.offer.id)
            return OfferYear.objects.filter(offer=off, acronym=self.acronym,
                                            academic_year=self.academic_year).exclude(id=self.id)
        return None


def find_by_academic_year(academic_yr):
    return OfferYear.objects.filter(academic_year=int(academic_yr))


def find_by_structure(struct):
    return OfferYear.objects.filter(structure=struct).order_by('academic_year', 'acronym')


def find_by_id(offer_year_id):
    return OfferYear.objects.get(pk=offer_year_id)


def search_root_offers(entity=None, academic_yr=None, acronym=None):
    """
    Offers are organized hierarchically. This function returns only root offers.
    """
    has_criteria = False
    queryset = OfferYear.objects

    if entity:
        queryset = queryset.filter(structure__acronym__icontains=entity)
        has_criteria = True

    if academic_yr:
        queryset = queryset.filter(academic_year=academic_yr)
        has_criteria = True

    if acronym:
        queryset = queryset.filter(acronym__icontains=acronym)
        has_criteria = True

    if has_criteria:
        queryset = queryset.filter(parent=None)
        return queryset
    else:
        return None


def find_by_academicyear_acronym(academic_yr, acronym):
    return OfferYear.objects.filter(academic_year=academic_yr, acronym=acronym)


def find_by_user(user):
    offer_year_list = []
    program_mgr_list= program_manager.find_by_user(user)
    for program in program_mgr_list:
        offer_year_list.append(program.offer_year)
    return offer_year_list
