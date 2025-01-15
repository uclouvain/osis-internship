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
import uuid as uuid
from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext_lazy as _

from internship.models.cohort import get_current_and_future_cohorts
from internship.models.enums.role import Role
from internship.models.enums.user_account_expiry import UserAccountExpiry


class MasterAllocationAdmin(admin.ModelAdmin):
    list_display = ('master', 'organization', 'specialty', 'cohort', 'role')
    fieldsets = ((None, {'fields': ('master', 'organization', 'specialty', 'role')}),)
    raw_id_fields = ('master', 'organization', 'specialty')
    list_filter = ('organization__cohort', 'specialty__cohort', 'role')
    search_fields = ['master__person__last_name', 'master__person__first_name']


class MasterAllocation(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    master = models.ForeignKey(
        'internship.InternshipMaster', on_delete=models.CASCADE, verbose_name=_('Master')
    )
    organization = models.ForeignKey(
        'internship.Organization',
        blank=True, null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Organization'),
    )
    specialty = models.ForeignKey(
        'internship.InternshipSpeciality',
        blank=True, null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Specialty'),
    )

    role = models.CharField(
        max_length=50,
        choices=Role.choices(),
        default=Role.MASTER.name,
        verbose_name=_('Role'),
    )

    def cohort(self):
        return self.specialty.cohort if self.specialty else (self.organization.cohort if self.organization else None)

    def save(self, *args, **kwargs):
        existing = MasterAllocation.objects.filter(
            master=self.master,
            organization=self.organization,
            specialty=self.specialty,
            role=self.role
        )
        if not existing:
            super(MasterAllocation, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {} - {}".format(self.master, self.organization, self.specialty)


def find_by_master(cohort, a_master):
    return find_by_cohort(cohort).filter(master=a_master)


def search(cohort, specialty, hospital, account=None, expiry=None, role=Role.MASTER.name):
    masters = find_by_cohort(cohort)

    if role:
        masters = masters.filter(role=role)

    if specialty:
        masters = masters.filter(specialty=specialty)

    if hospital:
        masters = masters.filter(organization=hospital)

    if account:
        masters = masters.filter(master__user_account_status=account)

    if expiry:
        if expiry == UserAccountExpiry.EXPIRED.value:
            masters = masters.filter(master__user_account_expiration_date__lte=datetime.now())
        elif expiry == UserAccountExpiry.LT_3MONTHS.value:
            masters = masters.filter(
                master__user_account_expiration_date__range=(
                    datetime.now() + timedelta(days=1),
                    datetime.now() + timedelta(days=92)
                )
            ).order_by('master__user_account_expiration_date')
        elif expiry == UserAccountExpiry.GT_3MONTHS.value:
            masters = masters.filter(master__user_account_expiration_date__gte=datetime.now() + timedelta(days=92))

    if specialty or hospital:
        return masters.order_by("master__person__last_name", "master__person__first_name")
    else:
        return masters \
            .filter(specialty__isnull=False, organization__isnull=False) \
            .order_by("master__person__last_name", "master__person__first_name")


def clean_allocations(cohort, master, postpone):
    if postpone:
        MasterAllocation.objects.filter(
            organization__cohort__in=get_current_and_future_cohorts(),
            master=master
        ).delete()
    else:
        find_by_master(cohort, master).delete()


def find_by_cohort(cohort_from):
    return MasterAllocation.objects.filter(Q(organization__cohort=cohort_from) | Q(specialty__cohort=cohort_from))
