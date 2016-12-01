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
from base.tests.models import test_person, test_offer_year, test_academic_year
from base.models import program_manager
from django.test import TestCase


def create_program_manager(offer_year):
    person = test_person.create_person("program", "manager")
    a_program_manager = program_manager.ProgramManager(person=person, offer_year=offer_year)
    a_program_manager.save()
    return a_program_manager


def _create_program_manager(offer_year, person):
    pmg = program_manager.ProgramManager(offer_year=offer_year, person=person)
    pmg.save()
    return pmg


class FindByOfferYearTest(TestCase):

    def setUp(self):
        self.academic_year = test_academic_year.create_academic_year()
        self.off_year = test_offer_year.create_offer_year('DROI1BA',
                                                          'Bachelor in law',
                                                          self.academic_year)

    def test_case_offer_is_none(self):
        self.assertEquals(len(program_manager.find_by_offer_year(None)), 0)

    def test_case_no_existing_program_manager_for_one_offer(self):
        off_year = test_offer_year.create_offer_year('MATH2MS/G',
                                                     'Master in mathematics (general orientation)',
                                                     self.academic_year)
        self.assertEquals(len(program_manager.find_by_offer_year(off_year)), 0)

    def test_return_sorted_managers(self):
        _create_program_manager(self.off_year, test_person.create_person("Yannick", "Leblanc"))
        _create_program_manager(self.off_year, test_person.create_person("Yannick", "Ferreira"))
        _create_program_manager(self.off_year, test_person.create_person("Laura", "Ferreira"))
        _create_program_manager(self.off_year, test_person.create_person("Bob", "Uncle"))
        _create_program_manager(self.off_year, test_person.create_person("Laura", "Dupont"))
        managers = program_manager.find_by_offer_year(self.off_year)
        self.assertEquals(managers[0].person.last_name, "Dupont")
        self.assertEquals(managers[1].person.last_name, "Ferreira")
        self.assertEquals(managers[1].person.first_name, "Laura")
        self.assertEquals(managers[2].person.last_name, "Ferreira")
        self.assertEquals(managers[2].person.first_name, "Yannick")
        self.assertEquals(managers[3].person.last_name, "Leblanc")
        self.assertEquals(managers[4].person.last_name, "Uncle")
