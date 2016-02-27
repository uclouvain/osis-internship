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
from django.utils import timezone

from base.enums import EVENT_TYPE


class OfferYearCalendar(models.Model):
    external_id       = models.CharField(max_length=100, blank=True, null=True)
    changed           = models.DateTimeField(null=True)
    academic_calendar = models.ForeignKey('AcademicCalendar')
    offer_year        = models.ForeignKey('OfferYear')
    event_type        = models.CharField(max_length=50, choices=EVENT_TYPE)
    start_date        = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    end_date          = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    customized        = models.BooleanField(default=False)

    def __str__(self):
        return u"%s - %s - %s" % (self.academic_calendar, self.offer_year, self.event_type)


def offer_year_calendar_by_current_session_exam():
    return OfferYearCalendar.objects.filter(event_type__startswith='EXAM_SCORES_SUBMISSION_SESS_') \
        .filter(start_date__lte=timezone.now()) \
        .filter(end_date__gte=timezone.now()).first()


def find_offer_years_by_academic_calendar(academic_calendar):
    return OfferYearCalendar.objects.filter(academic_calendar=int(academic_calendar.id))