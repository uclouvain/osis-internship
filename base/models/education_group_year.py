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
from django.utils.translation import ugettext_lazy as _
from base.models import offer, program_manager, academic_year
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class EducationGroupYearAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'education_group_type', 'changed')
    fieldsets = ((None, {'fields': ('academic_year', 'entity_administration', 'entity_administration_fac',
                                    'entity_management', 'entity_management_fac', 'acronym', 'title',
                                    'title_international', 'title_short', 'title_printable', 'grade', 'grade_type',
                                    'recipient', 'location', 'postal_code', 'city', 'country', 'phone', 'fax', 'email',
                                    'campus', 'education_group_type', 'education_group')}),)
    list_filter = ('academic_year', 'grade', 'education_group_type', 'campus')
    raw_id_fields = ('education_group_type', 'grade_type','campus','country','entity_administration',
                     'entity_administration_fac', 'entity_management', 'entity_management_fac', 'academic_year',
                     'education_group')
    search_fields = ['acronym']


GRADE_TYPES = (
    ('BACHELOR', _('bachelor')),
    ('MASTER', _('master')),
    ('DOCTORATE', _('ph_d')))


class EducationGroupYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    education_group = models.ForeignKey('EducationGroup')
    academic_year = models.ForeignKey('AcademicYear')
    acronym = models.CharField(max_length=15, db_index=True)
    title = models.CharField(max_length=255)
    title_international = models.CharField(max_length=255, blank=True, null=True)
    title_short = models.CharField(max_length=255, blank=True, null=True)
    title_printable = models.CharField(max_length=255, blank=True, null=True)
    grade = models.CharField(max_length=20, blank=True, null=True, choices=GRADE_TYPES)
    entity_administration = models.ForeignKey('Structure', related_name='education_group_admministration', blank=True, null=True)
    entity_administration_fac = models.ForeignKey('Structure', related_name='education_group_admministration_fac', blank=True, null=True)
    entity_management = models.ForeignKey('Structure', related_name='education_group_management', blank=True, null=True)
    entity_management_fac = models.ForeignKey('Structure', related_name='education_group_management_fac', blank=True, null=True)
    recipient = models.CharField(max_length=255, blank=True, null=True)  # Recipient of scores cheets (Structure)
    location = models.CharField(max_length=255, blank=True, null=True)  # Address for scores cheets
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    fax = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    campus = models.ForeignKey('Campus', blank=True, null=True)
    grade_type = models.ForeignKey('reference.GradeType', blank=True, null=True)
    enrollment_enabled = models.BooleanField(default=False)
    education_group_type = models.ForeignKey('OfferType', blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)

