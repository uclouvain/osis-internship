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
from base.models.enums import academic_type, rate, internship_presence, schedule_type, activity_presence, diploma_focus


class EducationGroupYearAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'education_group_type', 'changed')
    fieldsets = ((None, {'fields': ('academic_year', 'acronym', 'title', 'education_group_type', 'education_group')}),)
    list_filter = ('academic_year', 'education_group_type')
    raw_id_fields = ('education_group_type', 'academic_year', 'education_group')
    search_fields = ['acronym']


class EducationGroupYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    acronym = models.CharField(max_length=15, db_index=True)
    title = models.CharField(max_length=255)
    academic_year = models.ForeignKey('AcademicYear')
    education_group = models.ForeignKey('EducationGroup')
    education_group_type = models.ForeignKey('OfferType', blank=True, null=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    active = models.BooleanField(default=False)
    subtest = models.BooleanField(default=False)
    concours = models.BooleanField(default=False)
    fundable = models.BooleanField(default=False)
    funding_guidance = models.CharField(max_length=1, blank=True, null=True)
    funding_cud = = models.BooleanField(default=False)
    funding_guidance_cud = models.CharField(max_length=1, blank=True, null=True)
    academic_type = models.CharField(max_length=20, choices=academic_type.ACADEMIC_TYPES)
    university_certificate = = models.BooleanField(default=False)
    rate = models.CharField(max_length=20, choices=rate.RATES)
    enrollment_campus = models.ForeignKey('Campus')
    main_teaching_campus = models.ForeignKey('Campus', blank=True, null=True)
    administration_entity = models.ForeignKey('Entity')
    academic_entity = models.ForeignKey('Entity')
    dissertation = models.BooleanField(default=False)
    internship = models.CharField(max_length=20, choices=internship_presence.INTERNSHIP_STATUS, blank=True, null=True)
    schedule_type = models.CharField(max_length=20, choices=schedule_type.SCHEDULE_TYPES, default=schedule_type.DAILY)
    english_activities = models.CharField(max_length=20, choices=activity_presence.ACTIVITY_PRESENCES, blank=True, null=True)
    other_language_activities = models.CharField(max_length=20, choices=activity_presence.ACTIVITY_PRESENCES, blank=True, null=True)
    other_campus_activities = models.CharField(max_length=20, choices=activity_presence.ACTIVITY_PRESENCES, blank=True, null=True)
    supplement = models.ForeignKey('Supplement', blank=True, null=True)
    joint_diploma = models.BooleanField(default=False)
    diploma_focus = models.CharField(max_length=30, choices=diploma_focus.DIPLOMA_FOCUS, blank=True, null=True)
    diploma_title = models.CharField(max_length=140, blank=True, null=True)
    exchange_comment = models.CharField(max_length=320, blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)
