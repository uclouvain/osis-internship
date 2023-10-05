##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import date
from itertools import chain

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class PeriodAdmin(SerializableModelAdmin):
    list_display = (
        'name', 'date_start', 'date_end', 'cohort', 'reminder_mail_sent', 'remedial', 'place_evaluation_active'
    )
    fieldsets = ((None, {'fields': ('name', 'date_start', 'date_end', 'cohort', 'remedial')}),)
    list_filter = ('cohort', 'reminder_mail_sent', 'remedial', 'place_evaluation_active')


class ActivePeriod(models.Manager):
    def get_queryset(self):
        current_date = date.today()
        return super().get_queryset().filter(date_start__lte=current_date, date_end__gte=current_date)


class PastPeriod(models.Manager):
    def get_queryset(self):
        current_date = date.today()
        return super().get_queryset().filter(
            date_start__lte=current_date,
            date_end__lte=current_date
        ).order_by('-date_end')


class Period(SerializableModel):
    name = models.CharField(max_length=255)
    date_start = models.DateField()
    date_end = models.DateField()
    cohort = models.ForeignKey('internship.cohort', on_delete=models.CASCADE)
    reminder_mail_sent = models.BooleanField(default=False)
    remedial = models.BooleanField(default=False)
    place_evaluation_active = models.BooleanField(default=False)
    exclude_from_assignment = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActivePeriod()
    past = PastPeriod()

    def clean(self):
        self.clean_start_date()

    def clean_start_date(self):
        if all([self.date_start, self.date_end]) and self.date_start >= self.date_end:
            raise ValidationError({"date_start": _("Start date must be earlier than end date.")})
        if all([self.cohort_id, self.date_start, self.date_end]):
            self._check_period_overlap_in_parent_cohort()

    def _check_period_overlap_in_parent_cohort(self):
        linked_cohorts = self.cohort.parent_cohort.subcohorts.all() if self.cohort.parent_cohort else []
        for linked_cohort in linked_cohorts:
            for period in linked_cohort.period_set.filter(remedial=False):
                if self.cohort != linked_cohort and not self.remedial \
                        and ((self.date_start <= period.date_end and self.date_end >= period.date_start) or
                             (period.date_start <= self.date_end and period.date_end >= self.date_start)):
                    raise ValidationError(
                        {"date_start": _(
                            "The period overlaps {} in {} (only possible for remedial periods)"
                        ).format(period.name, linked_cohort.name)}
                    )

    def number(self):
        return int(self.name[1])

    @property
    def is_active(self):
        return self.date_start <= date.today() <= self.date_end

    @property
    def is_past(self):
        return date.today() > self.date_end

    def __str__(self):
        return u"%s" % self.name


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return Period.objects.filter(**kwargs).select_related().order_by("date_start")


def get_periods(cohort_id, remedial: bool, exclude_from_assignment: bool = False):
    return Period.objects.filter(
        cohort__pk=cohort_id,
        remedial=remedial,
        exclude_from_assignment=exclude_from_assignment,
    ).prefetch_related(
        'internshipstudentaffectationstat_set'
    ).order_by("date_end")


def get_assignable_periods(cohort_id):
    return get_periods(cohort_id, remedial=False, exclude_from_assignment=False)


def get_remedial_periods(cohort_id):
    return get_periods(cohort_id, remedial=True, exclude_from_assignment=True)


def get_effective_periods(cohort_id):
    return get_assignable_periods(cohort_id) | get_remedial_periods(cohort_id)


def get_subcohorts_periods(cohort):
    return list(
        chain.from_iterable([get_assignable_periods(cohort_id=subcohort.id) for subcohort in cohort.subcohorts.all()])
    )
