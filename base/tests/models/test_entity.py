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
from base.models import entity
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_link import EntityLinkFactory
from base.tests.factories.entity_version import EntityVersionFactory


class EntityTest(TestCase):

    def setUp(self):
        self.start_date = datetime.date(2015, 1, 1)
        self.end_date = datetime.date(2015, 12, 31)
        self.date_in_2015 = factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2015, 12, 30)).fuzz()
        self.date_in_2017 = factory.fuzzy.FuzzyDate(datetime.date(2017, 1, 1), datetime.date(2017, 12, 30)).fuzz()
        self.parent = EntityFactory()
        self.children = [EntityFactory() for x in range(4)]
        for x in range(4):
            EntityLinkFactory(
                parent=self.parent,
                child=self.children[x],
                start_date=self.start_date,
                end_date=self.end_date
                )

    def test_get_entity_direct_children_in_dates(self):
        self.assertCountEqual(self.parent.get_direct_children(date=self.date_in_2015),
                              [self.children[x] for x in range(4)])

    def test_get_entity_direct_children_out_dates(self):
        self.assertCountEqual(self.parent.get_direct_children(date=self.date_in_2017), [])

    def test_get_entity_direct_children_in_and_out_dates(self):
        in_2017_children = [EntityFactory() for x in range(4)]
        for x in range(4):
            EntityLinkFactory(
                parent=self.parent,
                child=in_2017_children[x],
                start_date=datetime.date(2017, 1, 1),
                end_date=datetime.date(2017, 12, 31)
                )
        self.assertCountEqual(self.parent.get_direct_children(date=self.date_in_2017),
                              [in_2017_children[x] for x in range(4)])

    def test_find_descendants(self):
        grandchildren = [EntityFactory() for x in range(8)]
        grandgrandchildren = [EntityFactory() for x in range(4)]

        for x in range(4):
            EntityLinkFactory(
                parent=self.children[x],
                child=grandchildren[x*2],
                start_date=self.start_date,
                end_date=self.end_date
            )
            EntityLinkFactory(
                parent=self.children[x],
                child=grandchildren[x * 2 + 1],
                start_date=self.start_date,
                end_date=self.end_date
            )
            EntityLinkFactory(
                parent=grandchildren[x*2],
                child=grandgrandchildren[x],
                start_date=self.start_date,
                end_date=self.end_date
            )

        descendants = self.children + grandchildren + grandgrandchildren

        self.assertCountEqual(self.parent.find_descendants(date=self.date_in_2015),
                              descendants)

    def test_search_entities_by_version_acronym_date_in(self):
        for x in range(4):
            EntityVersionFactory(
                entity=self.children[x],
                acronym="ENTITY_V_" + str(x),
                start_date=self.start_date,
                end_date=self.end_date
            )

        self.assertCountEqual(entity.search(acronym='ENTITY_V', version_date=self.date_in_2015), self.children)
        self.assertCountEqual(entity.search(acronym='NON_EXISTING', version_date=self.date_in_2015), [])
        self.assertCountEqual(entity.search(acronym='ENTITY_V_1', version_date=self.date_in_2015), [self.children[1]])

    def test_search_entities_by_version_acronym_date_out(self):
        for x in range(4):
            EntityVersionFactory(
                entity=self.children[x],
                acronym="ENTITY_V_" + str(x),
                start_date=self.start_date,
                end_date=self.end_date
            )

        self.assertCountEqual(entity.search(acronym='ENTITY_V', version_date=self.date_in_2017), [])
        self.assertCountEqual(entity.search(acronym='NON_EXISTING', version_date=self.date_in_2017), [])
        self.assertCountEqual(entity.search(acronym='ENTITY_V_1', version_date=self.date_in_2017), [])
