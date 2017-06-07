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
from dissertation.models.offer_proposition_group import *
from django.test import TestCase


class OfferPropositionGroupTestCase(TestCase):
    def setUp(self):
        OfferPropositionGroup.objects.create(name_short="PSP", name_long="Faculté de Psychologie")
        OfferPropositionGroup.objects.create(name_short="DROIT", name_long="Faculté de droit")

    def test_offer_proposition_group_exist(self):
        psp = OfferPropositionGroup.objects.get(name_short='PSP')
        drt = OfferPropositionGroup.objects.get(name_long='Faculté de droit')
        self.assertEqual(psp.name_long, "Faculté de Psychologie")
        self.assertEqual(drt.name_short, "DROIT")

    def test_find_all_ordered_by_name_short(self):
        all_offer_proposition_group = find_all_ordered_by_name_short()
        self.assertEqual(all_offer_proposition_group.count(), 2)

