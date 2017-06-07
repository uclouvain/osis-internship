##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from django.utils import timezone
from base.models import entity
from base.models.enums import entity_type
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory


class EntityTest(TestCase):

    def setUp(self):
        self.start_date = timezone.make_aware(datetime.datetime(2015, 1, 1))
        self.end_date = timezone.make_aware(datetime.datetime(2015, 12, 31))
        self.date_in_2015 = factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                    timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
        self.date_in_2017 = factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2017, 1, 1)),
                                                    timezone.make_aware(datetime.datetime(2017, 12, 30))).fuzz()
        self.parent = EntityFactory()
        self.children = [EntityFactory() for x in range(4)]
        for x in range(4):
            EntityVersionFactory(
                entity=self.children[x],
                parent=self.parent,
                start_date=self.start_date,
                end_date=self.end_date
                )

    def test_get_entity_direct_children_in_dates(self):
        self.assertCountEqual(self.parent.find_direct_children(date=self.date_in_2015),
                              [self.children[x] for x in range(4)])

    def test_get_entity_direct_children_out_dates(self):
        self.assertCountEqual(self.parent.find_direct_children(date=self.date_in_2017), [])

    def test_get_entity_direct_children_in_and_out_dates(self):
        in_2017_children = [EntityFactory() for x in range(4)]
        for x in range(4):
            EntityVersionFactory(
                entity=in_2017_children[x],
                parent=self.parent,
                start_date=timezone.make_aware(datetime.datetime(2017, 1, 1)),
                end_date=timezone.make_aware(datetime.datetime(2017, 12, 31))
                )
        self.assertCountEqual(self.parent.find_direct_children(date=self.date_in_2017),
                              [in_2017_children[x] for x in range(4)])

    def test_find_descendants(self):
        grandchildren = [EntityFactory() for x in range(8)]
        grandgrandchildren = [EntityFactory() for x in range(4)]

        for x in range(4):
            EntityVersionFactory(
                entity=grandchildren[x * 2],
                parent=self.children[x],
                start_date=self.start_date,
                end_date=self.end_date
            )
            EntityVersionFactory(
                entity=grandchildren[x * 2 + 1],
                parent=self.children[x],
                start_date=self.start_date,
                end_date=self.end_date
            )
            EntityVersionFactory(
                entity=grandgrandchildren[x],
                parent=grandchildren[x * 2],
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

    def test_find_entity_descendants_from_entity_version_and_date(self):
        EntityVersionFactory(
            entity=self.parent,
            acronym="ENTITY_PARENT",
            start_date=self.start_date,
            end_date=self.end_date
        )
        for ent in entity.search(acronym='ENTITY_PARENT', version_date=self.date_in_2015):
            self.assertCountEqual(ent.find_descendants(date=self.date_in_2015), self.children)

    def test_search_entities_by_version_type(self):
        types_dict = dict(entity_type.ENTITY_TYPES)
        types = [types_dict['SECTOR'],
                 types_dict['FACULTY'],
                 types_dict['SCHOOL'],
                 types_dict['FACULTY']]
        for x in range(4):
            EntityVersionFactory(
                entity=self.children[x],
                acronym="ENTITY_V_" + str(x),
                start_date=self.start_date,
                end_date=self.end_date,
                entity_type=types[x]
            )

        self.assertCountEqual(entity.search(entity_type=types_dict['FACULTY']), [self.children[1], self.children[3]])
        self.assertCountEqual(entity.search(entity_type='NON_EXISTING'), [])

    def test_get_most_recent_acronym(self):
        start_dates = [
            timezone.make_aware(datetime.datetime(2015, 1, 1)),
            timezone.make_aware(datetime.datetime(2016, 1, 1)),
            timezone.make_aware(datetime.datetime(2017, 1, 1))
        ]
        end_dates = [
            timezone.make_aware(datetime.datetime(2015, 12, 31)),
            timezone.make_aware(datetime.datetime(2016, 12, 31)),
            timezone.make_aware(datetime.datetime(2017, 12, 31))
        ]

        for x in range(3):
            EntityVersionFactory(
                entity=self.parent,
                acronym="ENTITY_V_" + str(x),
                start_date=start_dates[x],
                end_date=end_dates[x]
            )

        self.assertEqual(self.parent.most_recent_acronym(), "ENTITY_V_2")

    def test_get_by_external_id(self):
        an_entity = EntityFactory(external_id="1234567")
        self.assertEqual(entity.get_by_external_id("1234567"), an_entity)
        self.assertEqual(entity.get_by_external_id("321"), None)

    def test_get_by_internal_id(self):
        an_entity = EntityFactory()
        self.assertEqual(entity.get_by_internal_id(an_entity.id), an_entity)
        self.assertEqual(entity.get_by_internal_id(an_entity.id+1), None)

    def test_find_versions(self):
        start_dates = [
            timezone.make_aware(datetime.datetime(2015, 1, 1)),
            timezone.make_aware(datetime.datetime(2016, 1, 1)),
            timezone.make_aware(datetime.datetime(2017, 1, 1))
        ]
        end_dates = [
            timezone.make_aware(datetime.datetime(2015, 12, 31)),
            timezone.make_aware(datetime.datetime(2016, 12, 31)),
            timezone.make_aware(datetime.datetime(2017, 12, 31))
        ]

        versions = [EntityVersionFactory(
                    entity=self.parent,
                    acronym="ENTITY_V_" + str(x),
                    entity_type="FACULTY",
                    title="Faculty n° " + str(x),
                    start_date=start_dates[x],
                    end_date=end_dates[x]
                    ) for x in range(3)]
        self.assertCountEqual(self.parent.find_versions(),
                              [versions[0],
                              versions[1],
                              versions[2]
                               ])
