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
from base.models.enums import number_session, academic_calendar_type


class SessionExamCalendarAdmin(admin.ModelAdmin):
    list_display = ('academic_calendar', 'number_session', 'changed')
    list_filter = ('academic_calendar', 'number_session',)
    raw_id_fields = ('academic_calendar',)
    search_fields = ['academic_calendar', 'number_session']


class SessionExamCalendar(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    number_session = models.IntegerField(choices=number_session.NUMBERS_SESSION)
    academic_calendar = models.ForeignKey('AcademicCalendar')

    class Meta:
        unique_together = (("number_session", "academic_calendar"),)

    def __str__(self):
        return u"%s - %s" % (self.academic_calendar, self.number_session)

    def save(self, *args, **kwargs):
        # Ensure only academic calendar of type "SCORES_EXAM_SUBMISSION" can be saved
        if self.academic_calendar.reference != academic_calendar_type.SCORES_EXAM_SUBMISSION:
            raise ValueError('The academic calendar is not a scores exam submission type')

        super(SessionExamCalendar, self).save(*args, **kwargs)

def current_session_exam(date=datetime.date.today()):
    """"
    :return session exam, None if not in session exam [Default: Return current session exam]
    """
    try:
        return SessionExamCalendar.objects.get(academic_calendar__start_date__lte=date,
                                           academic_calendar__end_date__gte=date)
    except SessionExamCalendar.DoesNotExist:
        return None

def find_session_exam_number(date=datetime.date.today()):
    """"
    :return session exam number, None if not in session exam [Default: Return current session exam]
    """
    current_session = current_session_exam(date)
    if current_session:
        return current_session.number_session
    return None

def get_latest_session_exam(date=datetime.date.today()):
    """"
    :return latest session exam done of the current academic calendar
    """
    return SessionExamCalendar.objects.filter(academic_calendar__end_date__lte=date) \
        .order_by('-academic_calendar__end_date') \
        .first()
