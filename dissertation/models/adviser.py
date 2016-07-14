##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from .dissertation_role import DissertationRole
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin


class AdviserAdmin(admin.ModelAdmin):
    list_display = ('person', 'type')


class Adviser(models.Model):
    TYPES_CHOICES = (
        ('PRF', _('Professor')),
        ('MGR', _('Manager')),
    )

    person = models.OneToOneField('base.Person', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TYPES_CHOICES, default='PRF')
    available_by_email = models.BooleanField(default=False)
    available_by_phone = models.BooleanField(default=False)
    available_at_office = models.BooleanField(default=False)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        first_name = ""
        middle_name = ""
        last_name = ""
        if self.person.first_name:
            first_name = self.person.first_name
        if self.person.middle_name:
            middle_name = self.person.middle_name
        if self.person.last_name:
            last_name = self.person.last_name + ","
        return u"%s %s %s" % (last_name.upper(), first_name, middle_name)

    def stat_dissertation_role(self):
        list_stat = [0] * 4
        queryset = DissertationRole.objects.all().filter(Q(adviser=self))
        list_stat[0] = queryset.filter(Q(adviser=self) & Q(dissertation__active=True)).count()
        list_stat[1] = queryset.filter(
            Q(adviser=self) & Q(status='PROMOTEUR') &
            Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                                  Q(dissertation__status='ENDED') |
                                                  Q(dissertation__status='DEFENDED')).count()
        list_stat[4] = queryset.filter(Q(adviser=self) &
                                       Q(status='PROMOTEUR') &
                                       Q(dissertation__status='DIR_SUBMIT') &
                                       Q(dissertation__active=True)).count()

        advisers_copro = queryset.filter(
            Q(adviser=self) &
            Q(status='CO_PROMOTEUR') &
            Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                                  Q(dissertation__status='ENDED') |
                                                  Q(dissertation__status='DEFENDED'))
        list_stat[2] = advisers_copro.count()
        tab_offer_count_copro = {}
        for dissertaion_role_copro in advisers_copro:
            if dissertaion_role_copro.dissertation.offer_year_start.offer.title in tab_offer_count_copro:
                tab_offer_count_copro[dissertaion_role_copro.dissertation.offer_year_start.offer.title] = \
                    tab_offer_count_copro[str(dissertaion_role_copro.dissertation.offer_year_start.offer.title)] + 1
            else:
                tab_offer_count_copro[dissertaion_role_copro.dissertation.offer_year_start.offer.title] = 1
        advisers_reader = queryset.filter(Q(adviser=self) &
                                          Q(status='READER') &
                                          Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                                                                Q(dissertation__status='ENDED') |
                                                                                Q(dissertation__status='DEFENDED'))
        list_stat[3] = advisers_reader.count()
        tab_offer_count_read = {}
        for dissertaion_role_read in advisers_reader:
            if dissertaion_role_read.dissertation.offer_year_start.offer.title in tab_offer_count_read:
                tab_offer_count_read[dissertaion_role_read.dissertation.offer_year_start.offer.title] = \
                    tab_offer_count_read[str(dissertaion_role_read.dissertation.offer_year_start.offer.title)] + 1
            else:
                tab_offer_count_read[dissertaion_role_read.dissertation.offer_year_start.offer.title] = 1
        advisers_pro = queryset.filter(Q(adviser=self) &
                                       Q(status='PROMOTEUR') &
                                       Q(dissertation__active=True)).exclude(Q(dissertation__status='DRAFT') |
                                                                             Q(dissertation__status='ENDED') |
                                                                             Q(dissertation__status='DEFENDED'))
        tab_offer_count_pro = {}
        for dissertaion_role_pro in advisers_pro:
            if dissertaion_role_pro.dissertation.offer_year_start.offer.title in tab_offer_count_pro:
                tab_offer_count_pro[dissertaion_role_pro.dissertation.offer_year_start.offer.title] = \
                    tab_offer_count_pro[str(dissertaion_role_pro.dissertation.offer_year_start.offer.title)] + 1
            else:
                tab_offer_count_pro[dissertaion_role_pro.dissertation.offer_year_start.offer.title] = 1
        return list_stat, tab_offer_count_read, tab_offer_count_copro, tab_offer_count_pro

    class Meta:
        ordering = ["person__last_name", "person__middle_name", "person__first_name"]


def find_adviser_by_person(a_person):
    adviser = Adviser.objects.get(person=a_person)
    return adviser


def search_adviser(terms):
    queryset = Adviser.objects.all().filter(type='PRF')
    if terms:
        queryset = queryset.filter(
            (Q(person__first_name__icontains=terms) | Q(person__last_name__icontains=terms)) &
            Q(type='PRF')).distinct()
    return queryset
