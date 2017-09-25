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
from django.utils import timezone
from attribution.models import attribution
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models.enums import entity_container_year_link_type
from base.models import learning_unit_year
import datetime
from reference.tests.factories.country import CountryFactory


now = datetime.datetime.now()


def create_learning_unit_year(acronym, title, academic_year):
    learning_unit = LearningUnitFactory(acronym=acronym, title=title, start_year=2010)
    return LearningUnitYearFactory(acronym=acronym,
                                   title=title,
                                   academic_year=academic_year,
                                   learning_unit=learning_unit)


class LearningUnitYearTest(TestCase):
    def setUp(self):
        self.country = CountryFactory()
        self.tutor = TutorFactory()
        self.academic_year = AcademicYearFactory(year=timezone.now().year)
        self.learning_unit_year = LearningUnitYearFactory(acronym="LDROI1004", title="Juridic law courses",
                                                          academic_year=self.academic_year)
    #
    # def test_find_by_tutor_with_none_argument(self):
    #     self.assertEquals(attribution.find_by_tutor(None), None)
    #
    # def test_subdivision_computation(self):
    #     l_container_year = LearningContainerYearFactory(acronym="LBIR1212", academic_year=self.academic_year)
    #     l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year= l_container_year,
    #                             academic_year=self.academic_year)
    #     l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year= l_container_year,
    #                             academic_year=self.academic_year)
    #     l_unit_3 = LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year= l_container_year,
    #                             academic_year=self.academic_year)
    #
    #     self.assertFalse(l_unit_1.subdivision)
    #     self.assertEqual(l_unit_2.subdivision, 'A')
    #     self.assertEqual(l_unit_3.subdivision, 'B')
    #
    # def test_find_reference_fac(self):
    #     l_container = L
    #     l_container_year = LearningContainerYearFactory(acronym="LDROI1001",
    #                                                     academic_year=self.academic_year)
    #     l_unit_yr = LearningUnitYearFactory(acronym="LDROI1001",
    #                                         learning_container_year= l_container_year,
    #                                         academic_year=self.academic_year,
    #                                         learning_unit=LearningUnitFactory())

    def test_is_service_course(self):
        start_date = self.academic_year.start_date
        end_date = self.academic_year.end_date

        l_container = LearningContainerFactory()
        l_container_year = LearningContainerYearFactory(acronym="LDROI1001",
                                                        learning_container=l_container,
                                                        academic_year=self.academic_year)
        l_unit_yr = LearningUnitYearFactory(acronym="LDROI1001",
                                            learning_container_year= l_container_year,
                                            academic_year=self.academic_year,
                                            learning_unit=LearningUnitFactory())
        year = self.academic_year.year

        entity_faculty = EntityFactory(country=self.country)
        entity_faculty_version = EntityVersionFactory(
            entity=entity_faculty,
            acronym="ENTITY_FACULTY",
            title="This is the entity faculty ",
            entity_type="FACULTY",
            parent=None,
            start_date=start_date,
            end_date=end_date
        )
        entity_school_child_level1 = EntityFactory(country=self.country)
        EntityVersionFactory(entity=entity_school_child_level1,
                             acronym="ENTITY_LEVEL1",
                             title="This is the entity version level1 ",
                             entity_type="SCHOOL",
                             parent=entity_faculty,
                             start_date=start_date,
                             end_date=end_date)
        entity_school_child_level2 = EntityFactory(country=self.country)
        entity_school_version_level2 = EntityVersionFactory(
            entity=entity_school_child_level2,
            acronym="ENTITY_LEVEL2",
            title="This is the entity version level 2",
            entity_type="SCHOOL",
            parent=entity_school_child_level1,
            start_date=start_date,
            end_date=end_date
        )


##
        entity_requirement = EntityFactory()
        EntityVersionFactory(entity=entity_requirement,
                             parent=entity_school_child_level2,
                             acronym="Entity requi",
                             start_date=start_date,
                             end_date=end_date)

        EntityContainerYearFactory(
            entity=entity_requirement,
            learning_container_year=l_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        entity_allocation = EntityFactory()
        EntityVersionFactory(entity=entity_allocation,
                             parent=None,
                             acronym="Entity_allo",
                             start_date=start_date,
                             end_date=end_date)

        EntityContainerYearFactory(
            entity=entity_allocation,
            learning_container_year=l_container_year,
            type=entity_container_year_link_type.ALLOCATION_ENTITY
        )


        self.assertTrue(learning_unit_year.is_service_course(l_unit_yr))

    def test_is_not_service_course(self):
        start_date = self.academic_year.start_date
        end_date = self.academic_year.end_date

        l_container = LearningContainerFactory()
        l_container_year = LearningContainerYearFactory(acronym="LDROI1001",
                                                        learning_container=l_container,
                                                        academic_year=self.academic_year)
        l_unit_yr = LearningUnitYearFactory(acronym="LDROI1001",
                                            learning_container_year= l_container_year,
                                            academic_year=self.academic_year,
                                            learning_unit=LearningUnitFactory())
        year = self.academic_year.year

        entity_faculty = EntityFactory(country=self.country)
        entity_faculty_version = EntityVersionFactory(
            entity=entity_faculty,
            acronym="ENTITY_FACULTY",
            title="This is the entity faculty ",
            entity_type="FACULTY",
            parent=None,
            start_date=start_date,
            end_date=end_date
        )
        entity_school_child_level1 = EntityFactory(country=self.country)
        EntityVersionFactory(entity=entity_school_child_level1,
                             acronym="ENTITY_LEVEL1",
                             title="This is the entity version level1 ",
                             entity_type="SCHOOL",
                             parent=entity_faculty,
                             start_date=start_date,
                             end_date=end_date)
        entity_school_child_level2 = EntityFactory(country=self.country)
        entity_school_version_level2 = EntityVersionFactory(
            entity=entity_school_child_level2,
            acronym="ENTITY_LEVEL2",
            title="This is the entity version level 2",
            entity_type="SCHOOL",
            parent=entity_school_child_level1,
            start_date=start_date,
            end_date=end_date
        )


        ##
        entity_requirement = EntityFactory()
        EntityVersionFactory(entity=entity_requirement,
                             parent=entity_school_child_level2,
                             acronym="Entity requi",
                             start_date=start_date,
                             end_date=end_date)

        EntityContainerYearFactory(
            entity=entity_requirement,
            learning_container_year=l_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        entity_allocation = EntityFactory()
        EntityVersionFactory(entity=entity_allocation,
                             parent=entity_school_child_level2,
                             acronym="Entity_allo",
                             start_date=start_date,
                             end_date=end_date)

        EntityContainerYearFactory(
            entity=entity_allocation,
            learning_container_year=l_container_year,
            type=entity_container_year_link_type.ALLOCATION_ENTITY
        )


        self.assertFalse(learning_unit_year.is_service_course(l_unit_yr))