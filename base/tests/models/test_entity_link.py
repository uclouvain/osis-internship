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


class EntityLinkTest(TestCase):

    def setUp(self):
        self.an_entity = EntityFactory()
        self.start_date = datetime.date(2015, 1, 1)
        self.end_date = datetime.date(2015, 12, 31)

        EntityLinkFactory(
            child=self.an_entity,
            start_date=self.start_date,
            end_date=self.end_date
            )

    def test_create_entity_link_same_child_same_dates(self):
        with self.assertRaisesMessage(AttributeError, 'EntityLink invalid parameters'):
            EntityLinkFactory(
                child=self.an_entity,
                start_date=self.start_date,
                end_date=self.end_date
                )

    def test_create_entity_link_same_child_overlapping_dates_end_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityLink invalid parameters'):
            EntityLinkFactory(
                child=self.an_entity,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1), datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2015, 12, 30)).fuzz()
                )

    def test_create_entity_link_same_child_overlapping_dates_start_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityLink invalid parameters'):
            EntityLinkFactory(
                child=self.an_entity,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2015, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1), datetime.date(2020, 12, 30)).fuzz()
                )

    def test_create_entity_link_same_child_overlapping_dates_both_dates_out(self):
        with self.assertRaisesMessage(AttributeError, 'EntityLink invalid parameters'):
            EntityLinkFactory(
                child=self.an_entity,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1), datetime.date(2014, 12, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1), datetime.date(2020, 12, 30)).fuzz()
                )

    def test_create_entity_link_same_child_overlapping_dates_both_dates_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityLink invalid parameters'):
            EntityLinkFactory(
                child=self.an_entity,
                start_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2015, 6, 30)).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(datetime.date(2015, 7, 1), datetime.date(2015, 12, 30)).fuzz()
                )

    def test_create_entity_link_child_equals_parent(self):
        with self.assertRaisesMessage(AttributeError, 'EntityLink invalid parameters'):
            EntityLinkFactory(
                child=self.an_entity,
                parent=self.an_entity
                )

    def test_get_parent_entity_link(self):
        entities = [EntityFactory() for x in range(3)]
        entity_links = [EntityLinkFactory(
                            parent=entities[x],
                            child=entities[x+1],
                            start_date=self.start_date,
                            end_date=self.end_date
                        )
                        for x in range(2)]

        self.assertEqual(entity_links[1].get_parent(), entity_links[0])
        self.assertEqual(entity_links[0].get_parent(), None)

    def test_get_upper_hierarchy(self):
        entities = [EntityFactory() for x in range(6)]
        entity_links = [EntityLinkFactory(
                            parent=entities[x],
                            child=entities[x+1],
                            start_date=self.start_date,
                            end_date=self.end_date
                        )
                        for x in range(5)]
        self.assertCountEqual(entity_links[4].get_upper_hierarchy(), [entity_links[x] for x in range(4)])
