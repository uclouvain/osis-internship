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
from base.models import offer_year
from base.tests.models import test_offer
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_year import OfferYearFactory
from django.test import TestCase
from django.utils import timezone


def create_offer_year(acronym, title, academic_year):
    an_offer_year = offer_year.OfferYear(offer=test_offer.create_offer(title),
                                         academic_year=academic_year,
                                         acronym=acronym, title=title)
    an_offer_year.save()
    return an_offer_year


class OfferYearTest(TestCase):

    def test_find_by_id_list_none_ids_list(self):
        self.assertIsNone(offer_year.find_by_id_list(None))

    def test_find_by_id_list_empty_ids_list(self):
        self.assertIsNone(offer_year.find_by_id_list([]))

    def test_search_offers(self):
        academic_year = AcademicYearFactory(year=timezone.now().year)
        self.assertFalse(offer_year.search_offers(None, academic_year, None).exists())

        offer_yr = OfferYearFactory(academic_year=academic_year)
        self.assertEqual(offer_year.search_offers([offer_yr.entity_management], academic_year, None)[0], offer_yr)

        previous_academic_year = AcademicYearFactory(year=timezone.now().year-1)
        self.assertFalse(offer_year.search_offers([offer_yr.entity_management], previous_academic_year, None).exists())

