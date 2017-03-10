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
from base.models import person
from base.enums import person_source_type
from django.conf import settings


def create_person(first_name, last_name, email=None):
    a_person = person.Person(first_name=first_name, last_name=last_name, email=email)
    a_person.save()
    return a_person


def create_person_with_user(user):
    a_person = person.Person(first_name=user.first_name, last_name=user.last_name, user=user)
    a_person.save()
    return a_person


class PersonTest(TestCase):

    settings.INTERNAL_EMAIL_SUFIX = 'osis.org'

    def test_person_from_external_source(self):
        p = person.Person(email='matheus@osis.org',
                          last_name='Nashtergeith',
                          first_name='Matheus',
                          source=person_source_type.DISSERTATION)
        self.assertRaises(AttributeError, p.save)

    def test_person_from_internal_source(self):
        p = person.Person(email='matheus@osis.org',
                          last_name='Nashtergeith',
                          first_name='Matheus')
        try:
            p.save()
        except AttributeError:
            self.fail("Exception not expected")

    def test_person_without_source(self):
        p = person.Person(email='matheus@osis.org',
                          last_name='Nashtergeith',
                          first_name='Matheus',
                          source=None)
        try:
            p.save()
        except AttributeError:
            self.fail("Exception not expected")

    def test_find_by_global_id(self):
        a_person = person.Person(global_id="123")
        a_person.save()
        dupplicated_person = person.Person(global_id="123")
        dupplicated_person.save()
        found_person = person.find_by_global_id("1234")
        return self.assertEqual(found_person, None, "find_by_global_id should return None if a record is not found.")
