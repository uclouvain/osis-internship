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
from django.utils import timezone
import factory
import factory.fuzzy
import datetime
from base.models import entity_version
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory


class EntityVersionTest(TestCase):

    def setUp(self):
        self.entities = [EntityFactory() for x in range(2)]
        self.start_date = timezone.make_aware(datetime.datetime(2015, 1, 1))
        self.end_date = timezone.make_aware(datetime.datetime(2015, 12, 31))

        self.entity_versions = [EntityVersionFactory(
                                entity=self.entities[x],
                                acronym="ENTITY_V_"+str(x),
                                start_date=self.start_date,
                                end_date=self.end_date
                                )
                                for x in range(2)]

    def test_create_entity_version_same_entity_same_dates(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=self.start_date,
                end_date=self.end_date
                )

    def test_create_entity_version_same_entity_overlapping_dates_end_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2010, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2014, 12, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                 timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_entity_overlapping_dates_start_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2016, 1, 1)),
                                                 timezone.make_aware(datetime.datetime(2020, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_entity_overlapping_dates_both_dates_out(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2010, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2014, 12, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2016, 1, 1)),
                                                 timezone.make_aware(datetime.datetime(2020, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_entity_overlapping_dates_both_dates_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                entity=self.entities[0],
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2015, 6, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 7, 1)),
                                                 timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_acronym_overlapping_dates_end_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2010, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2014, 12, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                 timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_acronym_overlapping_dates_start_date_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2016, 1, 1)),
                                                 timezone.make_aware(datetime.datetime(2020, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_acronym_overlapping_dates_both_dates_out(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2010, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2014, 12, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2016, 1, 1)),
                                                 timezone.make_aware(datetime.datetime(2020, 12, 30))).fuzz()
                )

    def test_create_entity_version_same_acronym_overlapping_dates_both_dates_in(self):
        with self.assertRaisesMessage(AttributeError, 'EntityVersion invalid parameters'):
            EntityVersionFactory(
                acronym=self.entity_versions[0].acronym,
                start_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                   timezone.make_aware(datetime.datetime(2015, 6, 30))).fuzz(),
                end_date=factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 7, 1)),
                                                 timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
                )

    def test_search_entity_version(self):
        search_date = factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                              timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
        self.assertEqual(entity_version.find("ENTITY_V_0", search_date), self.entity_versions[0])
        self.assertEqual(entity_version.find("ENTITY_V_1", search_date), self.entity_versions[1])
        self.assertEqual(entity_version.find("NOT_EXISTING_ENTITY", search_date), None)
