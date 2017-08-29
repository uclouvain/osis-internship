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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from decimal import Decimal
from django.test import TestCase

from base.business import learning_unit_year_volumes
from base.models.enums import entity_container_year_link_type


class LearningUnitYearVolumesTestCase(TestCase):
    def test_is_not_tot_annual_equal_to_q1_q2(self):
        self.assertFalse(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**{
            'VOLUME_TOTAL': Decimal(10),
            'VOLUME_Q1': Decimal(9),
            'VOLUME_Q2': Decimal(14)
        }))

    def test_is_tot_annual_equal_to_q1_q2(self):
        self.assertTrue(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**{
            'VOLUME_TOTAL': Decimal(40),
            'VOLUME_Q1': Decimal(38),
            'VOLUME_Q2': Decimal(2)
        }))

    def test_is_tot_annual_equal_to_q1_without_q2(self):
        self.assertTrue(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**{
            'VOLUME_TOTAL': Decimal(40),
            'VOLUME_Q1': Decimal(40),
        }))

    def test_is_tot_annual_equal_to_without_q1_q2(self):
        self.assertTrue(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**{
            'VOLUME_TOTAL': Decimal(70.4),
            'VOLUME_Q2': Decimal(70.4),
        }))

    def test_is_not_tot_req_entities_equal_to_vol_req_entity(self):
        self.assertFalse(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY : Decimal(40),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: Decimal(40),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: Decimal(40),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': Decimal(80)
        }))

    def test_is_tot_req_entities_equal_to_vol_req_entity_without_additional_req(self):
        self.assertTrue(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: Decimal(40),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': Decimal(40)
        }))

    def test_is_not_tot_req_entities_equal_to_vol_req_entity_without_additional_req_2(self):
        self.assertFalse(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: Decimal(40),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: Decimal(40),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': Decimal(40)
        }))

    def test_is_tot_req_entities_equal_to_vol_req_entity_without_additional_req_2(self):
        self.assertFalse(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: Decimal(30.46),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: Decimal(30.98),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': Decimal(61.44)
        }))

