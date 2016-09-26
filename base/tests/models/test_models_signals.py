##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import User, Group
from django.test import TestCase
from base.models.academic_year import AcademicYear
from base.models.offer import Offer
from base.models.offer_year import OfferYear
from base.models.person import Person
from base.models.program_manager import ProgramManager
from base.models.student import Student
from base.models.tutor import Tutor


def is_member(user, group):
    return user.groups.filter(name=group).exists()


def create_test_student(person):
    return Student.objects.create(registration_id=123456789, person=person)


def create_test_tutor(person):
    return Tutor.objects.create(person=person)


def create_test_pgm_manager(person):
    title = 'Test1BA'
    acronym = 'Test1BA'
    offer = Offer.objects.create(title=title)
    academic_year = AcademicYear.objects.create(year=2016)
    offer_year = OfferYear.objects.create(offer=offer, academic_year=academic_year, title=title, acronym=acronym)
    return ProgramManager.objects.create(offer_year=offer_year, person=person)


class AddToGroupsSignalsTest(TestCase):

    def setUp(self):
        self.user_foo = User.objects.create_user('user_foo')
        self.person_foo = Person.objects.create(user=self.user_foo)

    def test_add_to_students_group(self):
        create_test_student(self.person_foo)
        self.assertTrue(is_member(self.user_foo, 'students'), 'user_foo should be in students group')

    def test_remove_from_students_group(self):
        student_foo = create_test_student(self.person_foo)
        student_foo.delete()
        self.assertFalse(is_member(self.user_foo, 'students'), 'user_foo should not be in students group anymore')

    def test_add_to_tutors_group(self):
        create_test_tutor(self.person_foo)
        self.assertTrue(is_member(self.user_foo, 'tutors'), 'user_foo should be in tutors group')

    def test_remove_from_tutors_group(self):
        tutor_foo = create_test_tutor(self.person_foo)
        tutor_foo.delete()
        self.assertFalse(is_member(self.user_foo, 'tutors'), 'user_foo should not be in tutors group anymore')

    def test_add_to_pgm_manager_group(self):
        create_test_pgm_manager(self.person_foo)
        self.assertTrue(is_member(self.user_foo, 'program_managers'), 'user_foo should be in program_managers group')

    def test_remove_from_manager_group(self):
        pgm_manager_foo = create_test_pgm_manager(self.person_foo)
        pgm_manager_foo.delete()
        self.assertFalse(is_member(self.user_foo, 'program_managers'),
                         'user_foo should not be in program_managers group anymore')