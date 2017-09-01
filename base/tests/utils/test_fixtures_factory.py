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

    def test_get_students_persons(self):
        a_person = PersonFactory()
        persons = [a_person]
        student = StudentFactory(person=a_person)
        student.save()
        self.assertCountEqual(fixtures_factory.get_students_persons([a_person]), [])

    def test_get_students_no_persons(self):
        a_person = PersonFactory()
        student = StudentFactory(person=a_person)
        student.save()
        self.assertEqual(len(fixtures_factory.get_students_persons([])), 0)
