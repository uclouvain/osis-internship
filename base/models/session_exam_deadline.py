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
import datetime
from django.db import models
from django.contrib import admin
from base.models.enums import number_session


class SessionExamDeadlineAdmin(admin.ModelAdmin):
    list_display = ('deadline', 'deadline_tutor', 'offer_enrollment', 'number_session', 'changed')
    list_filter = ('offer_enrollment', 'number_session',)
    raw_id_fields = ('offer_enrollment',)
    search_fields = ['offer_enrollment', 'number_session']


class SessionExamDeadline(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    deadline = models.DateTimeField()
    deadline_tutor = models.IntegerField(null=True)  # Delta day(s)
    number_session = models.IntegerField(choices=number_session.NUMBERS_SESSION)
    offer_enrollment = models.ForeignKey('OfferEnrollment')
