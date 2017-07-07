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
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_component_class import LearningUnitComponentClassFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.entity_component_year import EntityComponentYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.models.enums import entity_container_year_link_type
from base.views import learning_unit as learning_unit_view
from django.utils.translation import ugettext_lazy as _


class LearningUnitViewTestCase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)
        self.learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year)
        self.learning_component_yr = LearningComponentYearFactory(learning_container_year=self.learning_container_yr)
        self.entity_container_yr = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
                                                         type=entity_container_year_link_type.REQUIREMENT_ENTITY)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()

        request = request_factory.get(reverse('learning_units'))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_units

        learning_units(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['current_academic_year'], self.current_academic_year)
        self.assertEqual(len(context['academic_years']), 1)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_units'))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_units

        learning_units(request)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['academic_years'].count(), 1)
        self.assertIsNone(context['learning_units'])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager')
    def test_learning_unit_read(self, mock_program_manager, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        mock_program_manager.return_value = True

        learning_unit_year = LearningUnitYearFactory(academic_year=self.current_academic_year)

        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_unit', args=[learning_unit_year.id]))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_unit_identification

        learning_unit_identification(request, learning_unit_year.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_unit/identification.html')
        self.assertEqual(context['learning_unit_year'], learning_unit_year)

    def test_get_components_no_learning_container_yr(self):
        self.assertEqual(len(learning_unit_view.get_components(None, False)), 0)

    def test_get_components_with_classes(self):
        l_container = LearningContainerFactory()
        l_container_year = LearningContainerYearFactory.build(academic_year=self.current_academic_year,
                                                              title="LC-98998",
                                                              learning_container=l_container)
        l_container_year.save()
        l_component_year = LearningComponentYearFactory(learning_container_year=l_container_year)
        LearningClassYearFactory(learning_component_year=l_component_year)
        LearningClassYearFactory(learning_component_year=l_component_year)

        components = learning_unit_view.get_components(l_container_year, True)
        self.assertEqual(len(components), 1)
        self.assertEqual(len(components[0]['learning_component_year'].classes), 2)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager')
    def test_get_partims_identification_tabs(self, mock_program_manager, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        mock_program_manager.return_value = True

        learning_unit_container_year = LearningContainerYearFactory(
            academic_year=self.current_academic_year
        )
        learning_unit_year = LearningUnitYearFactory(
            acronym="LCHIM1210",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.FULL,
            academic_year=self.current_academic_year
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210A",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.current_academic_year
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210B",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.current_academic_year
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210F",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.current_academic_year
        )

        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_unit', args=[learning_unit_year.id]))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_unit_identification

        learning_unit_identification(request, learning_unit_year.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_unit/identification.html')
        self.assertEqual(len(context['learning_container_year_partims']), 3)

    def test_volumes_undefined(self):
        entity_component_yr = EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                                         entity_container_year=self.entity_container_yr,
                                                         hourly_volume_total=0.00)
        data = learning_unit_view.volumes(entity_component_yr)
        self.assertEqual(data.get(learning_unit_view.HOURLY_VOLUME_KEY), learning_unit_view.UNDEFINED_VALUE)
        self.assertEqual(data.get(learning_unit_view.TOTAL_VOLUME_KEY), learning_unit_view.UNDEFINED_VALUE)
        self.assertEqual(data.get(learning_unit_view.VOLUME_PARTIAL_KEY), learning_unit_view.UNDEFINED_VALUE)
        self.assertEqual(data.get(learning_unit_view.VOLUME_REMAINING_KEY), learning_unit_view.UNDEFINED_VALUE)

    def test_volumes_unknwon_quadrimester(self):
        entity_component_yr=EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=15,
                                   hourly_volume_partial=-1)
        data = learning_unit_view.volumes(entity_component_yr)
        self.assertEqual(data.get(learning_unit_view.HOURLY_VOLUME_KEY), 15)
        self.assertEqual(data.get(learning_unit_view.TOTAL_VOLUME_KEY), 'partial_or_remaining')
        self.assertEqual(data.get(learning_unit_view.VOLUME_PARTIAL_KEY), "(15)")
        self.assertEqual(data.get(learning_unit_view.VOLUME_REMAINING_KEY), "(15)")

    def test_volumes(self):
        entity_component_yr = EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                                         entity_container_year=self.entity_container_yr,
                                                         hourly_volume_total=15,
                                                         hourly_volume_partial=None)
        data = learning_unit_view.volumes(entity_component_yr)
        self.assertEqual(data.get(learning_unit_view.HOURLY_VOLUME_KEY), 15)
        self.assertEqual(data.get(learning_unit_view.TOTAL_VOLUME_KEY), learning_unit_view.UNDEFINED_VALUE)
        self.assertEqual(data.get(learning_unit_view.VOLUME_PARTIAL_KEY), learning_unit_view.UNDEFINED_VALUE)
        self.assertEqual(data.get(learning_unit_view.VOLUME_REMAINING_KEY), learning_unit_view.UNDEFINED_VALUE)

        entity_component_yr = EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                                         entity_container_year=self.entity_container_yr,
                                                         hourly_volume_total=15,
                                                         hourly_volume_partial=15)
        data = learning_unit_view.volumes(entity_component_yr)
        self.assertEqual(data.get(learning_unit_view.HOURLY_VOLUME_KEY), 15)
        self.assertEqual(data.get(learning_unit_view.TOTAL_VOLUME_KEY), 'partial')
        self.assertEqual(data.get(learning_unit_view.VOLUME_PARTIAL_KEY), 15)
        self.assertEqual(data.get(learning_unit_view.VOLUME_REMAINING_KEY), '-')

        entity_component_yr = EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                                         entity_container_year=self.entity_container_yr,
                                                         hourly_volume_total=15,
                                                         hourly_volume_partial=10)
        data = learning_unit_view.volumes(entity_component_yr)
        self.assertEqual(data.get(learning_unit_view.HOURLY_VOLUME_KEY), entity_component_yr.hourly_volume_total)
        self.assertEqual(data.get(learning_unit_view.TOTAL_VOLUME_KEY), 'partial_remaining')
        self.assertEqual(data.get(learning_unit_view.VOLUME_PARTIAL_KEY), entity_component_yr.hourly_volume_partial)
        self.assertEqual(data.get(learning_unit_view.VOLUME_REMAINING_KEY), entity_component_yr.hourly_volume_total-entity_component_yr.hourly_volume_partial)

    def test_learning_component_year_undefined_value(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=15.00,
                                   hourly_volume_partial=None)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                     acronym='LBIOLA',
                                                     learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), learning_unit_view.UNDEFINED_VALUE)

    def test_learning_component_year_remaining(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=15.00,
                                   hourly_volume_partial=0.00)
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=15.00,
                                   hourly_volume_partial=0.00)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('remaining'))

    def test_learning_component_year_partial(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=30.00,
                                   hourly_volume_partial=30.00)
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=15.00,
                                   hourly_volume_partial=15.00)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('partial'))

    def test_learning_component_year_partial_remaining(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=30.00,
                                   hourly_volume_partial=25.00)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('partial_remaining'))

    def test_learning_component_year_partial_remaining_second(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=30.00,
                                   hourly_volume_partial=30.00)
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_partial=0.00)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('partial_remaining'))

    def test_learning_component_year_partial_second(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=30.00,
                                   hourly_volume_partial=30.00)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('partial'))

    def test_learning_component_year_remaining_third(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=30.00,
                                   hourly_volume_partial=0.00)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('remaining'))

    def test_learning_component_yr_unknow_quadrimester(self):
        EntityComponentYearFactory(learning_component_year=self.learning_component_yr,
                                   entity_container_year=self.entity_container_yr,
                                   hourly_volume_total=30.00,
                                   hourly_volume_partial=-1)
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   acronym='LBIOLA',
                                                   learning_container_year=self.learning_container_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                     learning_component_year=self.learning_component_yr)
        self.assertEqual(learning_unit_view.volume_distribution(learning_unit_yr), _('partial_or_remaining'))

    def test_learning_unit_usage_two_usages(self):
        learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                                             acronym='LBIOL')

        learning_unit_yr_1 = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                     acronym='LBIOLA',
                                                     learning_container_year=learning_container_yr)
        learning_unit_yr_2 = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                     acronym='LBIOLB',
                                                     learning_container_year=learning_container_yr)

        learning_component_yr = LearningComponentYearFactory(learning_container_year=learning_container_yr)

        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr_1,
                                     learning_component_year=learning_component_yr)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr_2,
                                     learning_component_year=learning_component_yr)

        self.assertEqual(learning_unit_view._learning_unit_usage(learning_component_yr), 'A, B')

    def test_learning_unit_usage_with_complete_LU(self):
        learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                                             acronym='LBIOL')

        learning_unit_yr_1 = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                     acronym='LBIOL',
                                                     learning_container_year=learning_container_yr)

        learning_component_yr = LearningComponentYearFactory(learning_container_year=learning_container_yr)

        LearningUnitComponentFactory(learning_unit_year=learning_unit_yr_1,
                                     learning_component_year=learning_component_yr)

        self.assertEqual(learning_unit_view._learning_unit_usage(learning_component_yr), _('complete'))

    def test_learning_unit_usage_by_class_with_complete_LU(self):
        academic_year = AcademicYearFactory(year=2016)
        learning_container_yr = LearningContainerYearFactory(academic_year=academic_year,
                                                             acronym='LBIOL')

        learning_unit_yr_1 = LearningUnitYearFactory(academic_year=academic_year,
                                                     acronym='LBIOL',
                                                     learning_container_year=learning_container_yr)

        learning_component_yr = LearningComponentYearFactory(learning_container_year=learning_container_yr)

        learning_unit_component = LearningUnitComponentFactory(learning_unit_year=learning_unit_yr_1,
                                                               learning_component_year=learning_component_yr)
        learning_class_year = LearningClassYearFactory(learning_component_year=learning_component_yr)
        LearningUnitComponentClassFactory(learning_unit_component=learning_unit_component,
                                          learning_class_year=learning_class_year)
        self.assertEqual(learning_unit_view._learning_unit_usage_by_class(learning_class_year), _('complete'))
