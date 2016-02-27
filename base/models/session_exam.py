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
from django.utils.translation import ugettext_lazy as _

from base.models.attribution import Attribution
from base.models.exam_enrollment import find_exam_enrollments_by_session
from base.models.offer_year_calendar import offer_year_calendar_by_current_session_exam


class SessionExam(models.Model):
    SESSION_STATUS = (
        ('IDLE', _('Idle')),
        ('OPEN', _('Open')),
        ('CLOSED', _('Closed')))

    external_id         = models.CharField(max_length=100, blank=True, null=True)
    changed             = models.DateTimeField(null=True)
    number_session      = models.IntegerField()
    status              = models.CharField(max_length=10,choices=SESSION_STATUS)
    learning_unit_year  = models.ForeignKey('LearningUnitYear')
    offer_year_calendar = models.ForeignKey('OfferYearCalendar')

    @property
    def offer(self):
        for rec_exam_enrollment in find_exam_enrollments_by_session(self):
            return rec_exam_enrollment.learning_unit_enrollment.offer
        return None

    @property
    def progress(self):
        enrollments = list(find_exam_enrollments_by_session(self))

        if enrollments:
            progress = 0
            for e in enrollments:
                if e.score_final is not None or e.justification_final is not None:
                    progress = progress +1
            return str(progress) + "/"+ str(len(enrollments))
        else:
            return "0/0"

    def __str__(self):
        return u"%s - %d" % (self.learning_unit_year, self.number_session)


def current_session_exam():
    offer_calendar = offer_year_calendar_by_current_session_exam()
    session_exam = SessionExam.objects.filter(offer_year_calendar=offer_calendar).first()
    return session_exam


def find_session_by_id(id):
    return SessionExam.objects.get(pk=id)


def find_sessions_by_tutor(tutor, academic_year):
    learning_units = Attribution.objects.filter(tutor=tutor).values('learning_unit')
    return SessionExam.objects.filter(~models.Q(status='IDLE')) \
        .filter(learning_unit_year__academic_year=academic_year) \
        .filter(learning_unit_year__learning_unit__in=learning_units)


def find_sessions_by_faculty(faculty, academic_year):
    return SessionExam.objects.filter(~models.Q(status='IDLE')) \
        .filter(offer_year_calendar__offer_year__academic_year=academic_year) \
        .filter(offer_year_calendar__offer_year__structure=faculty)

