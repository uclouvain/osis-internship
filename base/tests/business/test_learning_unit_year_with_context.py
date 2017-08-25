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
from base.business import learning_unit_year_with_context
from base.tests.factories.entity_component_year import EntityComponentYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.academic_year import AcademicYearFactory


class LearningUnitYearWithContextTestCase(TestCase):
    def test_get_floated_only_element_of_list(self):
        a_list = []
        self.assertIsNone(learning_unit_year_with_context._get_floated_only_element_of_list(a_list))
        self.assertEquals(learning_unit_year_with_context._get_floated_only_element_of_list(a_list, 0), 0)

        a_list = [17]
        self.assertEquals(learning_unit_year_with_context._get_floated_only_element_of_list(a_list), 17.0)
        self.assertEquals(type(learning_unit_year_with_context._get_floated_only_element_of_list(a_list)), float)

        a_list = [1, 2]
        with self.assertRaisesMessage(ValueError, "The provided list should contain 0 or 1 elements"):
            learning_unit_year_with_context._get_floated_only_element_of_list(a_list)

    def test_get_requirement_entities_volumes(self):
        learning_container_year = LearningContainerYearFactory(academic_year=AcademicYearFactory(year=2016))
        entity_types = ['REQUIREMENT_ENTITY', 'ADDITIONAL_REQUIREMENT_ENTITY_1', 'ADDITIONAL_REQUIREMENT_ENTITY_2']
        entity_containers_year = [EntityContainerYearFactory(type=entity_types[x],
                                                             learning_container_year=learning_container_year
                                                             ) for x in range(3)]
        components = [EntityComponentYearFactory(entity_container_year=entity_containers_year[x],
                                                 hourly_volume_total=x+5
                                                 ) for x in range(3)]
        wanted_response = {
            "REQUIREMENT_ENTITY": 5,
            "ADDITIONAL_REQUIREMENT_ENTITY_1": 6,
            "ADDITIONAL_REQUIREMENT_ENTITY_2": 7,
        }

        self.assertDictEqual(learning_unit_year_with_context._get_requirement_entities_volumes(components),
                             wanted_response)
