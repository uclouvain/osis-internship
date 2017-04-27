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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
import factory
import factory.fuzzy
import datetime
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_link import EntityLinkFactory


class EntityTest(TestCase):

    def setUp(self):
        self.start_date = datetime.date(2015, 1, 1)
        self.end_date = datetime.date(2015, 12, 31)
        self.date_in_2015 = factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2015, 12, 30)).fuzz()
        self.date_in_2017 = factory.fuzzy.FuzzyDate(datetime.date(2017, 1, 1), datetime.date(2017, 12, 30)).fuzz()
        self.parent = EntityFactory()
        self.children = [EntityFactory() for x in range(4)]
        [EntityLinkFactory(
            parent=self.parent,
            child=self.children[x],
            start_date=self.start_date,
            end_date=self.end_date
            )
            for x in range(4)]

    def test_get_entity_direct_children_in_dates(self):
        self.assertCountEqual(self.parent.get_direct_children(date=self.date_in_2015),
                              [self.children[x] for x in range(4)])

    def test_get_entity_direct_children_out_dates(self):
        self.assertCountEqual(self.parent.get_direct_children(date=self.date_in_2017), [])

    def test_get_entity_direct_children_in_and_out_dates(self):
        in_2017_children = [EntityFactory() for x in range(4)]
        [EntityLinkFactory(
            parent=self.parent,
            child=in_2017_children[x],
            start_date=datetime.date(2017, 1, 1),
            end_date=datetime.date(2017, 12, 31)
            )
            for x in range(4)]
        self.assertCountEqual(self.parent.get_direct_children(date=self.date_in_2017),
                              [in_2017_children[x] for x in range(4)])
