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
import datetime
from itertools import chain
from django.contrib.auth.models import User
from django.test import TestCase
from assessments.views import scores_responsible
from attribution.models import attribution
from attribution.tests.models import test_attribution
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_manager import EntityManagerFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.structure import StructureFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.models.test_person import create_person_with_user


class ScoresResponsibleViewTestCase(TestCase):
    def setUp(self):
        self.user = User(first_name="John", last_name="Smith")
        self.user.save()
        self.person = create_person_with_user(self.user)
        self.structure = StructureFactory()
        self.structure_children = StructureFactory(part_of=self.structure)
        self.entity_manager = EntityManagerFactory(person=self.person, structure=self.structure)
        self.tutor = TutorFactory()
        self.academic_year = AcademicYearFactory(year=datetime.date.today().year,
                                                 start_date=datetime.date.today())
        self.learning_unit_year = LearningUnitYearFactory(structure=self.structure,
                                                          acronym="LBIR1210",
                                                          academic_year=self.academic_year)
        self.learning_unit_year_children = LearningUnitYearFactory(structure=self.structure_children,
                                                                   acronym="LBIR1211",
                                                                   academic_year=self.academic_year)
        test_attribution.create_attribution(tutor=self.tutor,
                                            learning_unit_year=self.learning_unit_year,
                                            score_responsible=True)
        test_attribution.create_attribution(tutor=self.tutor,
                                            learning_unit_year=self.learning_unit_year_children,
                                            score_responsible=True)

    def test_is_faculty_admin(self):
        a_faculty_administrator = scores_responsible.is_faculty_admin(self.user)
        self.assertTrue(a_faculty_administrator)

    def test_create_dictionary(self):
        attributions = attribution.find_attributions(self.structure)
        attributions_children = attribution.find_all_distinct_children(attributions[0])
        attributions_list = list(chain(attributions, attributions_children))
        dictionary = scores_responsible.create_attributions_list(attributions_list)
        self.assertIsNotNone(dictionary)

    def test_find_entities_list(self):
        entities_list = scores_responsible.find_attributions_list(self.structure)
        self.assertIsNotNone(entities_list)
