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
from base.enums import JUSTIFICATION_TYPES


class ExamEnrollment(models.Model):
    ENCODING_STATUS_LIST = (
        ('SAVED',_('Saved')),
        ('SUBMITTED',_('Submitted')))

    external_id              = models.CharField(max_length=100, blank=True, null=True)
    changed                  = models.DateTimeField(null=True)
    score_draft              = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    score_reencoded          = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    score_final              = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    justification_draft      = models.CharField(max_length=20, blank=True, null=True, choices=JUSTIFICATION_TYPES)
    justification_reencoded  = models.CharField(max_length=20, blank=True, null=True, choices=JUSTIFICATION_TYPES)
    justification_final      = models.CharField(max_length=20, blank=True, null=True, choices=JUSTIFICATION_TYPES)
    encoding_status          = models.CharField(max_length=9, blank=True, null=True, choices=ENCODING_STATUS_LIST)
    session_exam             = models.ForeignKey('SessionExam')
    learning_unit_enrollment = models.ForeignKey('LearningUnitEnrollment')

    def student(self):
        return self.learning_unit_enrollment.student

    def __str__(self):
        return u"%s - %s" % (self.session_exam, self.learning_unit_enrollment)


def calculate_exam_enrollment_progress(enrollments):
    if enrollments:
        progress = len([e for e in enrollments if e.score_final or e.justification_final]) / len(enrollments)
    else:
        progress = 0
    return progress * 100


def find_exam_enrollments_by_session(session_exam):
    enrollments = ExamEnrollment.objects.filter(session_exam=session_exam) \
        .order_by('learning_unit_enrollment__offer_enrollment__offer_year__acronym',
                  'learning_unit_enrollment__offer_enrollment__student__person__last_name',
                  'learning_unit_enrollment__offer_enrollment__student__person__first_name')
    return enrollments


def find_exam_enrollments_drafts_by_session(session_exam):
    """ Return the enrollments of a session but not the ones already submitted. """
    enrollments = ExamEnrollment.objects.filter(session_exam=session_exam) \
        .filter(score_final__isnull=True) \
        .filter(models.Q(justification_final__isnull=True) |
                models.Q(justification_final=''))
    return enrollments


def count_encoded_scores(enrollments):
    """ Count the scores that were already encoded but not submitted yet. """
    counter = 0
    for enrollment in enrollments:
        if (enrollment.score_draft or enrollment.justification_draft) \
                and not enrollment.score_final \
                and not enrollment.justification_final:
            counter += 1

    return counter


def find_exam_enrollments_to_validate_by_session(session_exam):
    enrollments = ExamEnrollment.objects.filter(session_exam=session_exam) \
        .filter(~models.Q(score_draft=models.F('score_reencoded')) |
                ~models.Q(justification_draft=models.F('justification_reencoded'))) \
        .filter(score_final__isnull=True) \
        .filter(models.Q(justification_final__isnull=True) |
                models.Q(justification_final=''))
    return enrollments


def justification_label_authorized(is_fac):
    if is_fac:
        return '%s, %s, %s, %s, %s' % (_('Absent'),_('Cheating'), _('Ill'),  _('Justified absence'), _('Score missing'))
    else:
        return '%s, %s, %s' % (_('Absent'), _('Cheating'),_('Score missing'))


