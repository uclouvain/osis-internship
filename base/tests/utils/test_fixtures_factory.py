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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from base.utils import fixtures_factory
from base.tests.factories.structure import StructureFactory
from base.tests.factories.person import PersonFactory
from reference.tests.factories.country import CountryFactory
from base.tests.factories.student import StudentFactory

class TestFixturesFactory(TestCase):
    def test_create_fake_entity_manager_no_result(self):
        persons = [PersonFactory()]
        structures = [StructureFactory()]

        self.assertCountEqual(fixtures_factory.create_fake_entity_manager(None, None), [])
        self.assertCountEqual(fixtures_factory.create_fake_entity_manager(persons, None), [])
        self.assertCountEqual(fixtures_factory.create_fake_entity_manager(None, structures), [])

    def test_create_fake_entity_manager_less_than_5_results(self):
        persons = [PersonFactory()]
        structures = [StructureFactory()]
        self.assertEqual(len(fixtures_factory.create_fake_entity_manager(persons, structures)), 1)


    def test_create_fake_entity_manager_no_more_than_5_results(self):
        persons = [PersonFactory(), PersonFactory(), PersonFactory(), PersonFactory(), PersonFactory(),
                   PersonFactory(), PersonFactory(), PersonFactory()]
        structures = [StructureFactory()]
        self.assertEqual(len(fixtures_factory.create_fake_entity_manager(persons, structures)), 5)


    def test_find_person_max_id_first_person(self):
        self.assertEqual(fixtures_factory.find_person_max_id([]), 0)

    def test_find_person_max_id(self):
        person_1 = PersonFactory()
        person_2 = PersonFactory()
        persons = [person_1, person_2]
        self.assertEqual(fixtures_factory.find_person_max_id(persons), person_2.id)


    def test_de_identifying_person_addresses_with_no_countries(self):
        self.assertEqual(len(fixtures_factory.de_identifying_person_addresses([PersonFactory()], None)),1)
        self.assertEqual(len(fixtures_factory.de_identifying_person_addresses([PersonFactory()], [])), 1)

    def test_de_identifying_person_addresses_with_countries(self):
        a_country = CountryFactory()
        countries = [a_country]
        self.assertEqual(fixtures_factory.de_identifying_person_addresses([PersonFactory()], countries)[0].country, a_country)

    def test_de_identifying_person_addresses_with_fake_country(self):
        self.assertEqual(len(fixtures_factory.de_identifying_person_addresses([PersonFactory()], [])), 1)

    def test_get_students_persons(self):
        a_person = PersonFactory()
        persons = [a_person]
        student = StudentFactory(person=a_person)
        student.save()
        self.assertCountEqual(fixtures_factory.get_students_persons([a_person]), [a_person])

    def test_get_students_no_persons(self):
        a_person = PersonFactory()
        student = StudentFactory(person=a_person)
        student.save()
        self.assertEqual(len(fixtures_factory.get_students_persons([])), 0)

