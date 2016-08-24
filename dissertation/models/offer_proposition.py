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
from django.contrib import admin
from django.db import models
from django.utils import timezone
from base.models import offer
from datetime import datetime


class OfferPropositionAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'offer')
    raw_id_fields = ('offer',)


class OfferProposition(models.Model):
    acronym = models.CharField(max_length=200)
    offer = models.ForeignKey(offer.Offer)
    student_can_manage_readers = models.BooleanField(default=True)
    readers_visibility_date_for_students = models.BooleanField(default=False)
    adviser_can_suggest_reader = models.BooleanField(default=False)
    evaluation_first_year = models.BooleanField(default=False)
    validation_commission_exists = models.BooleanField(default=False)
    start_visibility_proposition = models.DateField(default=timezone.now)
    end_visibility_proposition = models.DateField(default=timezone.now)
    start_visibility_dissertation = models.DateField(default=timezone.now)
    end_visibility_dissertation = models.DateField(default=timezone.now)

    @property
    def in_periode_visibility_proposition(self):
        now = datetime.date(datetime.now())
        start = self.start_visibility_proposition
        end = self.end_visibility_proposition

        return start <= now <= end

    @property
    def in_periode_visibility_dissertation(self):
        now = datetime.date(datetime.now())
        start = self.start_visibility_dissertation
        end = self.end_visibility_dissertation

        return start <= now <= end

    def __str__(self):
        return self.acronym


def get_by_offer(an_offer):
    return OfferProposition.objects.get(offer=an_offer)


def search_by_offer(offers):
    return OfferProposition.objects.filter(offer__in=offers)\
                                   .distinct()\
                                   .order_by('acronym')


def show_validation_commission(offer_props):
    # True si validation_commission_exists est True pour au moins une offer_prop dans offer_props
    # False sinon
    return any([offer_prop.validation_commission_exists for offer_prop in offer_props])


def show_evaluation_first_year(offer_props):
    # True si evaluation_first_year est True pour au moins une offer_prop dans offer_props
    # False sinon
    return any([offer_prop.evaluation_first_year for offer_prop in offer_props])
