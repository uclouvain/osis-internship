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

from base.models.academic_calendar import AcademicCalendar
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory


def save(self, *args, **kwargs):
    return super(AcademicCalendar, self).save()


class EducationGroupViewTestCase(TestCase):
    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_education_groups(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        today = datetime.date.today()
        academic_year = AcademicYearFactory(start_date=today,
                                            end_date=today.replace(year=today.year + 1),
                                            year=today.year)

        request_factory = RequestFactory()

        request = request_factory.get(reverse('offers'))
        request.user = mock.Mock()

        from base.views.education_group import education_groups

        education_groups(request)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'education_groups.html')
        self.assertEqual(len(context['education_group_years']), 0)
        self.assertEqual(context['academic_year'], academic_year.id)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_education_groups_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()
        today = datetime.date.today()
        academic_year = AcademicYearFactory(start_date=today,
                                            end_date=today.replace(year=today.year + 1),
                                            year=today.year)

        request = request_factory.get(reverse('education_groups_search'), data={
            'entity_acronym': 'entity',
            'code': 'code',
            'academic_year': academic_year.id,
        })
        request.user = mock.Mock()

        from base.views.education_group import education_groups_search
        education_groups_search(request)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'education_groups.html')
        self.assertCountEqual(context['education_group_years'], [])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager', return_value=True)
    def test_education_group_read(self,
                                  mock_program_manager,
                                  mock_render,
                                  mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        today = datetime.date.today()
        academic_year = AcademicYearFactory(start_date=today,
                                            end_date=today.replace(year=today.year + 1),
                                            year=today.year)
        education_group_year = EducationGroupYearFactory(academic_year=academic_year)

        request = mock.Mock(method='GET')

        from base.views.education_group import education_group_read

        education_group_read(request, education_group_year.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'education_group/tab_identification.html')
