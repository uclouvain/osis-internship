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
from django.contrib import admin
from base.models import person, offer_year


class ProgrammeManagerAdmin(admin.ModelAdmin):
    list_display = ('person', 'offer_year')


class ProgrammeManager(models.Model):
    changed = models.DateTimeField(null=True)
    person  = models.ForeignKey(person.Person)
    offer_year = models.ForeignKey(offer_year.OfferYear, blank=True, null = True)

    def __str__(self):
        return u"%s - %s" % (self.person, self.offer_year)


def find_offer_year_by_user(user):
    programme_manager = ProgrammeManager.objects.filter(person__user=user).first()
    if programme_manager:
        return programme_manager.offer_year
    else:
        return None


def is_programme_manager(user, offer_year):
    pers = person.Person.objects.get(user=user)
    if user:
        programme_manager = ProgrammeManager.objects.filter(person=pers.id, offer_year=offer_year)
        if programme_manager:
            return True
    return False
