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
from base.models.enums import learning_component_year_type
from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_component_year import EntityComponentYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class LearningUnitYearVolumesTestCase(TestCase):
    def setUp(self):
        ac = AcademicYearFactory(year=2016)
        lc = LearningContainerYearFactory(academic_year=ac, acronym="LBIR1100",
                                          container_type=learning_container_year_types.COURSE)

        #Create UE Parent LBIR1100
        self.learning_unit_year_full = self._create_parent_with_components(lc)

        #Create UE Partim LBIR1100A
        self.learning_unit_year_partim = self._create_partim_A_with_components(lc)

    def test_validate_decimals(self):
        # Dot separator
        self.assertEqual(learning_unit_year_volumes._validate_decimals("40.65"), round(Decimal(40.65), 2))
        # Comma separator
        self.assertEqual(learning_unit_year_volumes._validate_decimals("40,65"), round(Decimal(40.65), 2))
        # Not digit
        with self.assertRaises(ValueError):
            learning_unit_year_volumes._validate_decimals("Not Digit")
        # More than 2 decimal
        with self.assertRaises(ValueError):
            learning_unit_year_volumes._validate_decimals("40.6555")

    def test_is_not_tot_annual_equal_to_q1_q2(self):
        VOLUME_TOTAL = learning_unit_year_volumes._validate_decimals('10')
        VOLUME_Q1 = learning_unit_year_volumes._validate_decimals('9')
        VOLUME_Q2 = learning_unit_year_volumes._validate_decimals('14')
        self.assertFalse(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**locals()))

    def test_is_tot_annual_equal_to_q1_q2(self):
        VOLUME_TOTAL = learning_unit_year_volumes._validate_decimals('40')
        VOLUME_Q1 = learning_unit_year_volumes._validate_decimals('37.45')
        VOLUME_Q2 = learning_unit_year_volumes._validate_decimals('2.55')
        self.assertTrue(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**locals()))

    def test_is_tot_annual_equal_to_q1_without_q2(self):
        VOLUME_TOTAL = learning_unit_year_volumes._validate_decimals('40')
        VOLUME_Q1 = learning_unit_year_volumes._validate_decimals('40.00')
        self.assertTrue(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**locals()))

    def test_is_tot_annual_equal_to_without_q1_q2(self):
        VOLUME_TOTAL = learning_unit_year_volumes._validate_decimals('70.4')
        VOLUME_Q2 = learning_unit_year_volumes._validate_decimals('70.40')
        self.assertTrue(learning_unit_year_volumes._is_tot_annual_equal_to_q1_q2(**locals()))

    def test_is_not_tot_req_entities_equal_to_vol_req_entity(self):
        self.assertFalse(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY : learning_unit_year_volumes._validate_decimals('40'),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: learning_unit_year_volumes._validate_decimals('40'),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: learning_unit_year_volumes._validate_decimals('40'),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': learning_unit_year_volumes._validate_decimals('80')
        }))

    def test_is_tot_req_entities_equal_to_vol_req_entity_without_additional_req(self):
        self.assertTrue(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: learning_unit_year_volumes._validate_decimals('60.1'),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': learning_unit_year_volumes._validate_decimals('60.1')
        }))

    def test_is_not_tot_req_entities_equal_to_vol_req_entity_without_additional_req_2(self):
        self.assertFalse(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: learning_unit_year_volumes._validate_decimals('40'),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: learning_unit_year_volumes._validate_decimals('40'),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': learning_unit_year_volumes._validate_decimals('40')
        }))

    def test_is_tot_req_entities_equal_to_vol_req_entity_without_additional_req_2(self):
        self.assertTrue(learning_unit_year_volumes._is_tot_req_entities_equal_to_vol_req_entity(**{
            'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: learning_unit_year_volumes._validate_decimals('30.46'),
            'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: learning_unit_year_volumes._validate_decimals('30.98'),
            'VOLUME_TOTAL_REQUIREMENT_ENTITIES': learning_unit_year_volumes._validate_decimals('61.44')
        }))

    def test_get_volumes_from_db(self):
        # If we take volume from database with learning unit year full / partim, it should be the same
        result_by_parent = learning_unit_year_volumes._get_volumes_from_db(self.learning_unit_year_full.id)
        result_by_partim = learning_unit_year_volumes._get_volumes_from_db(self.learning_unit_year_partim.id)
        self.assertEqual(result_by_parent, result_by_partim)

    def test_validate_components_data(self):
        volumes = learning_unit_year_volumes._get_volumes_from_db(self.learning_unit_year_full.id)

        l_full_with_volumes_computed = next((lunit_year for lunit_year in volumes
                                            if lunit_year.id == self.learning_unit_year_full.id), None)
        self.assertEqual(l_full_with_volumes_computed,  self.learning_unit_year_full)

        # No error found [No user change]
        self.assertFalse(learning_unit_year_volumes._validate_components_data(l_full_with_volumes_computed))

        # Simulate user modification -- Set VOL_TOT to 100 for CM/TP
        for component, data in l_full_with_volumes_computed.components.items():
            data['VOLUME_TOTAL'] = round(Decimal(100), 2)
        errors = learning_unit_year_volumes._validate_components_data(l_full_with_volumes_computed)
        self.assertTrue(errors)

        # It should have 4 errors
        # For each components (2), we do not respect - VOL_TOT = Q1 + Q2
        #                                            - VOL_TOT * PLANNED_CLASSE = VOL_TOT_REQ_ENTITIES
        self.assertEqual(4, len(errors))

    def test_validate_parent_partim_component(self):
        parent_data = {'VOLUME_TOTAL': Decimal(30), 'VOLUME_Q1': Decimal(15),
                       'VOLUME_Q2': Decimal(15), 'PLANNED_CLASSES': 1,
                       'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: Decimal(15),
                       'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: Decimal(30),
                       'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: Decimal(10)}

        partim_data = {'VOLUME_TOTAL': Decimal(15), 'VOLUME_Q1': Decimal(5),
                       'VOLUME_Q2': Decimal(10), 'PLANNED_CLASSES': 1,
                       'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: Decimal(10),
                       'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1:  Decimal(20),
                       'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2:  Decimal(5)}

        # Test no error on initial data
        self.assertFalse(learning_unit_year_volumes._validate_parent_partim_component(parent_data, partim_data))

        # Test error : Volume total parent must be greater than Volume total Partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['VOLUME_TOTAL'] = 5
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

        # Test error : Volume Q1 parent must be greater or equals than Volume Q1 Partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['VOLUME_Q1'] = 2
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

        # Test error : Volume Q2 parent must be greater or equals than Volume Q2 Partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['VOLUME_Q2'] = 9
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

        # Test error : Planned classes full must be greater or equals than planned classes partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['PLANNED_CLASSES'] = 0
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

        # Test error: Volume requirement entity full must be greater or equals than Volume requirement entity partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY] = 0
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

        # Test error: Volume additional 1 requirement entity full must be greater or equals than Volume requirement entity partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1] = 0
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

        # Test error: Volume additional 2 requirement entity full must be greater or equals than Volume requirement entity partim
        wrong_parent_data = parent_data.copy()
        wrong_parent_data['VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2] = 0
        self.assertTrue(learning_unit_year_volumes._validate_parent_partim_component(wrong_parent_data, partim_data))

    def test_update_volumes(self):
        volumes = learning_unit_year_volumes._get_volumes_from_db(self.learning_unit_year_full.id)
        l_full_with_volumes_computed = next((lunit_year for lunit_year in volumes
                                             if lunit_year.id == self.learning_unit_year_full.id), None)
        component_cm = next((lcomponent_year for lcomponent_year in l_full_with_volumes_computed.components.keys()
                             if lcomponent_year.type == learning_component_year_type.LECTURING), None)

        # Simulate user modification on lecturing component of full learning unit
        updated_volume = {
            l_full_with_volumes_computed.id: {
                component_cm.id: {
                    'VOLUME_TOTAL': '60',
                    'VOLUME_Q1': '5',
                    'VOLUME_Q2': '55',
                    'PLANNED_CLASSES': '2',
                    'VOLUME_' + entity_container_year_link_type.REQUIREMENT_ENTITY: '40',
                    'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: '40',
                    'VOLUME_' + entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: '40',
                    'VOLUME_TOTAL_REQUIREMENT_ENTITIES': '120'
                }
            }
        }
        # Save it
        errors = learning_unit_year_volumes.update_volumes(self.learning_unit_year_full.id, updated_volume)
        # No errors
        self.assertFalse(errors)

        # Reload data - Verify if it save to database
        volumes = learning_unit_year_volumes._get_volumes_from_db(self.learning_unit_year_full.id)
        l_full_with_volumes_computed = next((lunit_year for lunit_year in volumes
                                             if lunit_year.id == self.learning_unit_year_full.id), None)
        data_component_cm = next((data for lcomponent_year, data in l_full_with_volumes_computed.components.items()
                                  if lcomponent_year.type == learning_component_year_type.LECTURING), None)
        self.assertEqual(data_component_cm['VOLUME_TOTAL'], 60)
        self.assertEqual(data_component_cm['VOLUME_Q1'], 5)
        self.assertEqual(data_component_cm['VOLUME_Q2'], 55)
        self.assertEqual(data_component_cm['PLANNED_CLASSES'], 2)
        self.assertEqual(data_component_cm['VOLUME_TOTAL_REQUIREMENT_ENTITIES'], 120)

    def _create_parent_with_components(self, learning_container_year):
        # Create learning unit year full
        luy_full = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                           academic_year=learning_container_year.academic_year, acronym="LBIR1100",
                                           subtype=learning_unit_year_subtypes.FULL)
        ## Create component CM
        cm_component = LearningComponentYearFactory(acronym="CM",
                                                    type=learning_component_year_type.LECTURING,
                                                    learning_container_year=learning_container_year,
                                                    planned_classes=1)
        LearningUnitComponentFactory(learning_unit_year=luy_full, learning_component_year=cm_component)

        ### Assign Volume
        cm_volume_parent = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: {'vol_tot': 50},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: {'vol_tot': 10},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: {'vol_tot': 20},

        }
        _assign_volume(learning_container_year, cm_component, cm_volume_parent)

        ## Create component TP
        tp_component = LearningComponentYearFactory(acronym="TP",
                                                    type=learning_component_year_type.PRACTICAL_EXERCISES,
                                                    learning_container_year=learning_container_year,
                                                    planned_classes=1)
        LearningUnitComponentFactory(learning_unit_year=luy_full, learning_component_year=tp_component)

        ### Assign Volume
        tp_volume_parent = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: {'vol_tot': 30},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: {'vol_tot': 10},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: {'vol_tot': 10},

        }
        _assign_volume(learning_container_year, tp_component, tp_volume_parent)

        return luy_full

    def _create_partim_A_with_components(self, learning_container_year):
        luy_partim_a = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                               academic_year=learning_container_year.academic_year, acronym="LBIR1100A",
                                               subtype=learning_unit_year_subtypes.PARTIM)
        ## Create component CM
        cm_component = LearningComponentYearFactory(acronym="CM2",
                                                    type=learning_component_year_type.LECTURING,
                                                    learning_container_year=learning_container_year,
                                                    planned_classes=1)
        LearningUnitComponentFactory(learning_unit_year=luy_partim_a, learning_component_year=cm_component)

        ### Assign Volume
        cm_volume_parent = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: {'vol_tot': 20},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: {'vol_tot': 10},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: {'vol_tot': 20},

        }
        _assign_volume(learning_container_year, cm_component, cm_volume_parent)

        ## Create component TP
        tp_component = LearningComponentYearFactory(acronym="TP2",
                                                    type=learning_component_year_type.PRACTICAL_EXERCISES,
                                                    learning_container_year=learning_container_year,
                                                    planned_classes=1)
        LearningUnitComponentFactory(learning_unit_year=luy_partim_a, learning_component_year=tp_component)

        ### Assign Volume
        tp_volume_parent = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: {'vol_tot': 15},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: {'vol_tot': 5},
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: {'vol_tot': 5},

        }
        _assign_volume(learning_container_year, tp_component, tp_volume_parent)

        return luy_partim_a


def _assign_volume(container_year, component_year, map_entity_type_and_volume):
    for entity_type, volume in map_entity_type_and_volume.items():
        entity_cont = EntityContainerYearFactory(type=entity_type, learning_container_year=container_year)
        EntityComponentYearFactory(entity_container_year=entity_cont,
                                   learning_component_year=component_year,
                                   hourly_volume_total=volume.get('vol_tot'),
                                   hourly_volume_partial=volume.get('vol_partial'))