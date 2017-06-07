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
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.offer_proposition_group import OfferPropositionGroup
from base.models.offer import Offer
from django.test import TestCase


class OfferPropositionTestCase(TestCase):
    def setUp(self):
        OfferPropositionGroup.objects.create(name_short="PSP", name_long="Faculté de Psychologie")
        offer_proposition_g=OfferPropositionGroup.objects.get(name_short='PSP')
        offer_PSP2MSG=create_offer('PSP2MSG')
        OfferProposition.objects.create(acronym="PSP2MSG",
                                             offer=offer_PSP2MSG,
                                             offer_proposition_group=offer_proposition_g)


    def test_offer_proposition_exist(self):
        offer_proposition_psp = OfferProposition.objects.get(acronym='PSP2MSG')
        self.assertEqual(offer_proposition_psp.offer_proposition_group,OfferPropositionGroup.objects.get(name_short='PSP'))


def create_offer_proposition(acronym, offer,offer_proposition_group):
    offer_proposition = OfferProposition.objects.create(acronym=acronym, offer=offer, offer_proposition_group=offer_proposition_group)
    return offer_proposition

def create_offer(title):
    offer = Offer.objects.create(title=title)
    return offer
