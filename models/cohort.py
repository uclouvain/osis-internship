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
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from osis_common.models.serializable_model import SerializableModel
from osis_common.models.serializable_model import SerializableModelAdmin


class CohortAdmin(SerializableModelAdmin):
    list_display = ('name', 'description', 'publication_start_date', 'subscription_start_date',
                    'subscription_end_date', 'originated_from')
    fields = ('name', 'description', 'publication_start_date', 'subscription_start_date', 'subscription_end_date')


class Cohort(SerializableModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    publication_start_date = models.DateField()
    subscription_start_date = models.DateField()
    subscription_end_date = models.DateField()
    originated_from = models.ForeignKey('Cohort', null=True, blank=True)

    def clean(self):
        self.clean_start_date()
        self.clean_publication_date()

    def clean_start_date(self):
        if all([self.subscription_start_date, self.subscription_end_date]):
            if self.subscription_start_date >= self.subscription_end_date:
                raise ValidationError({"subscription_start_date": _("start_before_end")})

    def clean_publication_date(self):
        if all([ self.subscription_end_date, self.publication_start_date]):
            if self.publication_start_date < self.subscription_end_date:
                raise ValidationError({"publication_start_date": _("publication_after_subscription")})

    class Meta:
        ordering = ['name']

    @property
    def is_subscription_active(self):
        return self.subscription_start_date <= timezone.now().date() <= self.subscription_end_date

    @property
    def is_published(self):
        return timezone.now().date() >= self.publication_start_date

    def __str__(self):
        return self.name


def find_all():
    return Cohort.objects.all()
