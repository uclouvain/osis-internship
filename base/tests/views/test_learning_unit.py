from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class LearningUnitViewTestCase(TestCase):
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
        self.assertIsNone(context['current_academic_year'], None)
        self.assertEqual(len(context['academic_years']), 0)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_units_search'))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_units_search

        learning_units_search(request)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['academic_years'].count(), 0)
        self.assertIsNone(context['learning_units'])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager')
    def test_learning_unit_read(self, mock_program_manager, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        mock_program_manager.return_value = True

        learning_unit_year = LearningUnitYearFactory()

        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_unit_read', args=[learning_unit_year.id]))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_unit_read

        learning_unit_read(request, learning_unit_year.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_unit.html')
        self.assertEqual(context['learning_unit_year'], learning_unit_year)
        self.assertEqual(context['attributions'].count(), 0)
        self.assertEqual(context['enrollments'].count(), 0)