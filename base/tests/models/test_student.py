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
from base.models import student
from base.tests.models import test_person
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory


def create_student(first_name, last_name, registration_id):
    person = test_person.create_person(first_name, last_name)
    a_student = student.Student(person=person, registration_id=registration_id)
    a_student.save()
    return a_student


class StudentTest(TestCase):
    def test_find_by_person_name_case_insensitive(self):
        a_person = PersonFactory.build(last_name="Smith", user=None)
        a_person.save()
        a_student = StudentFactory.build(person=a_person)
        a_student.save()
        found = list(student.find_by(person_name="smith"))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, a_student.id)

    def test_find_by_id(self):
        tmp_student = StudentFactory()
        db_student = student.find_by_id(tmp_student.id)
        self.assertIsNotNone(tmp_student.person.user)
        self.assertEqual(db_student.person.id, tmp_student.person.id)
        self.assertEqual(db_student.person.email, tmp_student.person.email)
