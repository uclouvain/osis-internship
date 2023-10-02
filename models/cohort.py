##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from osis_common.models.serializable_model import SerializableModel
from osis_common.models.serializable_model import SerializableModelAdmin


class CohortAdmin(SerializableModelAdmin):
    list_display = ('name', 'description', 'publication_start_date', 'subscription_start_date',
                    'subscription_end_date', 'originated_from', 'is_parent', 'parent_cohort')
    fields = (
        'name', 'description', 'publication_start_date',
        'subscription_start_date', 'subscription_end_date', 'is_parent', 'parent_cohort',
    )


class Cohort(SerializableModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    publication_start_date = models.DateField(null=True, blank=True)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    originated_from = models.ForeignKey(
        'Cohort', null=True, blank=True,
        on_delete=models.CASCADE
    )

    is_parent = models.BooleanField(default=False)
    parent_cohort = models.ForeignKey(
        'Cohort', null=True, blank=True, on_delete=models.PROTECT, related_name='subcohorts'
    )

    def clean(self):
        self.clean_start_date()
        self.clean_publication_date()
        self.clean_parent_cohort()

    def clean_start_date(self):
        if all([self.subscription_start_date, self.subscription_end_date]):
            if self.subscription_start_date >= self.subscription_end_date:
                raise ValidationError({"subscription_start_date": _("Start date must be earlier than end date.")})

    def clean_publication_date(self):
        if all([self.subscription_end_date, self.publication_start_date]):
            if self.publication_start_date < self.subscription_end_date:
                raise ValidationError(
                    {"publication_start_date": _("Publication must be done after the subscription process.")}
                )

    def clean_parent_cohort(self):
        if self.parent_cohort and not self.parent_cohort.is_parent:
            raise ValidationError(
                {"parent_cohort": _("The parent cohort must be defined as parent")}
            )
        if self.is_parent and any(
                [self.subscription_start_date, self.subscription_end_date, self.publication_start_date]
        ):
            raise ValidationError(
                {"is_parent": _("A parent cohort cannot have publication and subscription dates")}
            )
        if not self.is_parent and not all(
                [self.subscription_start_date, self.subscription_end_date, self.publication_start_date]
        ):
            raise ValidationError(
                {"is_parent": _("A subcohort or standalone cohort must have publication and subscription dates")}
            )

    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                check=Q(is_parent=False) | Q(publication_start_date__isnull=True),
                name=_("A parent cohort cannot have publication and subscription dates")),
            models.CheckConstraint(
                check=Q(is_parent=True) | Q(publication_start_date__isnull=False),
                name=_("A subcohort must have publication and subscription dates")
            ),
            models.CheckConstraint(
                check=Q(is_parent=False) | Q(parent_cohort__isnull=True),
                name=_("A parent cohort cannot have a parent itself")
            ),
        ]

    @property
    def is_subscription_active(self):
        return self.subscription_start_date <= timezone.now().date() <= self.subscription_end_date

    @property
    def is_published(self):
        return timezone.now().date() >= self.publication_start_date

    def __str__(self):
        return self.name
