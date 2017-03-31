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
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory

from base.tests.models import test_exam_enrollment, test_offer_year_calendar, test_offer_enrollment, \
    test_learning_unit_enrollment, test_session_exam
from attribution.tests.models import test_attribution
from assessments.views import pgm_manager_administration
from base.models import program_manager

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.structure import StructureFactory
from base.enums import structure_type
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.academic_year import AcademicYearFactory
from reference.tests.factories.grade_type import GradeTypeFactory

class PgmManagerAdministrationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('tmp', 'tmp@gmail.com', 'tmp')
        self.person = PersonFactory()


        self.structure_root = StructureFactory()
        self.structure_faculty = StructureFactory(acronym='ESPO',type=structure_type.FACULTY)

        #self.academic_year = AcademicYearFactory(year=datetime.now().year)

        # self.structure_child1 = StructureFactory(part_of=self.structure_root)
        # self.structure_child2 = StructureFactory(part_of=self.structure_root)

    def test_set_find_faculty_entities(self):
        self.assertIsNone(pgm_manager_administration.get_entity_list(None))
        self.assertEqual(len(pgm_manager_administration.get_entity_list(self.structure_faculty.acronym)),1)
        self.assertIsNone(pgm_manager_administration.get_entity_list('zzzz'))
        # self.assertEqual(len(pgm_manager_administration.get_entity_list(self.structure_root.acronym)), 2)

    def test_search_find_programs_by_entity_grade_type(self):
        a_grade_type = GradeTypeFactory()
        offer_year1 = OfferYearFactory(entity_management=self.structure_faculty,
                                      grade_type=a_grade_type)
        offer_year2 = OfferYearFactory(academic_year=offer_year1.academic_year,
                                       entity_management=StructureFactory(),
                                       grade_type=a_grade_type)
        self.assertEqual(len(pgm_manager_administration.filter_by_entity_grade_type(offer_year1.academic_year,
                                                                                    [self.structure_faculty],
                                                                                    a_grade_type )),1)

        self.assertEqual(len(pgm_manager_administration.filter_by_entity_grade_type(offer_year1.academic_year,
                                                                                    [self.structure_faculty],
                                                                                    None )),1)
        self.assertEqual(len(pgm_manager_administration.filter_by_entity_grade_type(offer_year1.academic_year,
                                                                                    None,
                                                                                    None )),2)

    def test_add_pgm_manager_to_non_existing_pgm(self):
        an_academic_year = AcademicYearFactory(year=datetime.now().year)
        list_offer_id = [str(1)]
        pgm_manager_administration.add_program_managers(list_offer_id, self.person)
        managers = program_manager.ProgramManager.objects.all()
        self.assertEqual(len(managers), 0)

    def test_add_pgm_manager_to_one_pgm(self):
        an_academic_year = AcademicYearFactory(year=datetime.now().year)
        offer_year1 = OfferYearFactory(academic_year=an_academic_year)
        list_offer_id = [str(offer_year1.id)]
        pgm_manager_administration.add_program_managers(list_offer_id, self.person)
        managers = program_manager.find_by_offer_year_list([offer_year1])
        self.assertEqual(len(managers),1)

    def test_add_pgm_manager_to_two_pgm(self):
        an_academic_year = AcademicYearFactory(year=datetime.now().year)
        offer_year1 = OfferYearFactory(academic_year=an_academic_year)
        offer_year2 = OfferYearFactory(academic_year=an_academic_year)
        list_offer_id = [str(offer_year1.id),str(offer_year2.id)]
        pgm_manager_administration.add_program_managers(list_offer_id, self.person)
        managers = program_manager.find_by_offer_year_list([offer_year1, offer_year2])
        self.assertEqual(len(managers),2)

    def test_remove_pgm_manager_from_one_pgm(self):
        offer_year1 = OfferYearFactory()
        ProgramManagerFactory(person=self.person, offer_year=offer_year1)
        managers_count_before = len(program_manager.ProgramManager.objects.all())
        pgm_manager_administration.remove_programs_managers([offer_year1], self.person)
        managers_count_after = len(program_manager.ProgramManager.objects.all())
        self.assertEqual(managers_count_after, managers_count_before-1)

    def test_remove_pgm_manager_from_two_pgm(self):
        offer_year1 = OfferYearFactory()
        offer_year2 = OfferYearFactory()
        ProgramManagerFactory(person=self.person, offer_year=offer_year1)
        ProgramManagerFactory(person=self.person, offer_year=offer_year2)

        managers_count_before = len(program_manager.ProgramManager.objects.all())
        pgm_manager_administration.remove_programs_managers([offer_year1, offer_year2], self.person)
        managers_count_after = len(program_manager.ProgramManager.objects.all())
        self.assertEqual(managers_count_after, managers_count_before-2)