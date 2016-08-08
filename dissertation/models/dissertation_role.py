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
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class DissertationRole(models.Model):
    STATUS_CHOICES = (
        ('PROMOTEUR', _('pro')),
        ('CO_PROMOTEUR', _('copro')),
        ('READER', _('reader')),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    adviser = models.ForeignKey('Adviser')
    dissertation = models.ForeignKey('Dissertation')

    def __str__(self):
        return u"%s %s" % (self.status if self.status else "",
                           self.adviser if self.adviser else "")


def count_by_adviser(adviser, role=None, dissertation_status=None):
    query = DissertationRole.objects.filter(adviser=adviser)

    if role is not None:
        query = query.filter(status=role)

    if dissertation_status is not None:
        query = query.filter(dissertation__status=dissertation_status)

    query = query.filter(dissertation__active=True)\
                 .count()

    return query


def count_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation)\
                                   .count()


def search_by_adviser_and_role_stats(adviser, role):
    return DissertationRole.objects.filter(adviser=adviser)\
                                   .filter(status=role)\
                                   .filter(dissertation__active=True)\
                                   .exclude(
                                            Q(dissertation__status='DRAFT') |
                                            Q(dissertation__status='ENDED') |
                                            Q(dissertation__status='DEFENDED')
                                           )


def count_by_adviser_and_role_stats(adviser, role):
    return search_by_adviser_and_role_stats(adviser, role).count()


def add(status, adviser, dissertation):
    role = DissertationRole(status=status,
                            adviser=adviser,
                            dissertation=dissertation)
    role.save()


def search_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation)


def search_by_dissertation_and_role(dissertation, role):
    return search_by_dissertation(dissertation).filter(status=role)


def search_by_adviser_and_role(adviser, role):
    return DissertationRole.objects.filter(status=role)\
                                   .filter(adviser=adviser)\
                                   .filter(dissertation__active=True)\
                                   .exclude(dissertation__status='DRAFT')\
                                   .order_by(
                                                'dissertation__status',
                                                'dissertation__author__person__last_name',
                                                'dissertation__author__person__first_name'
                                            )


def search_by_adviser_and_role_and_offer(adviser, role, offer):
    return DissertationRole.objects.filter(status=role)\
                                   .filter(adviser=adviser)\
                                   .filter(dissertation__active=True)\
                                   .filter(dissertation__offer_year_start__offer=offer)\
                                   .exclude(dissertation__status='DRAFT')\
                                   .order_by(
                                                'dissertation__status',
                                                'dissertation__author__person__last_name',
                                                'dissertation__author__person__first_name'
                                            )


def search_by_adviser_and_role_and_status(adviser, role, status):
    return DissertationRole.objects.filter(status=role)\
                                   .filter(adviser=adviser)\
                                   .filter(dissertation__active=True)\
                                   .filter(dissertation__status=status)\
                                   .order_by(
                                                'dissertation__author__person__last_name',
                                                'dissertation__author__person__first_name'
                                            )


def list_teachers_action_needed(offer):
    return DissertationRole.objects.filter(status='PROMOTEUR')\
                                   .filter(dissertation__status='DIR_SUBMIT')\
                                   .filter(dissertation__offer_year_start__offer=offer)\
                                   .filter(dissertation__active=True)\
                                   .distinct('adviser')
