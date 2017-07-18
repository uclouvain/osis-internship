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
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from base.tests.factories.student import StudentFactory
from base.tests.factories.person import PersonFactory


class StudentViewTestCase(TestCase):

    # @mock.patch('django.contrib.auth.decorators')
    # @mock.patch('base.views.layout.render')
    # @mock.patch('base.models.program_manager')
    # def test_students(self, mock_program_manager, mock_render, mock_decorators):
    #     mock_decorators.login_required = lambda x: x
    #     mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
    #     mock_program_manager.is_program_manager.return_value = True
    #
    #     request_factory = RequestFactory()
    #
    #     request = request_factory.get(reverse('students'))
    #     request.user = mock.Mock()
    #
    #     from base.views.student import students
    #
    #     students(request)
    #
    #     self.assertTrue(mock_render.called)
    #     request, template, context = mock_render.call_args[0]
    #
    #     self.assertEqual(template, 'student/students.html')
    #
    # @mock.patch('django.contrib.auth.decorators')
    # @mock.patch('base.views.layout.render')
    # @mock.patch('base.models.program_manager')
    # def test_students_search(self, mock_program_manager, mock_render, mock_decorators):
    #     mock_decorators.login_required = lambda x: x
    #     mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
    #     mock_program_manager.is_program_manager.return_value = True
    #
    #     request_factory = RequestFactory()
    #     request = request_factory.get(reverse('students'))
    #     request.user = mock.Mock()
    #
    #     from base.views.student import students
    #
    #     students(request)
    #
    #     self.assertTrue(mock_render.called)
    #
    #     request, template, context = mock_render.call_args[0]
    #
    #     self.assertEqual(template, 'student/students.html')
    #     self.assertIsNone(context['students'])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager')
    def test_student_read(self, mock_program_manager, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_program_manager.return_value = True

        student = StudentFactory(person=PersonFactory(last_name='Durant', first_name='Thomas'))

        request_factory = RequestFactory()
        request = request_factory.get(reverse('student_read', args=[student.id]))
        request.user = mock.Mock()

        from base.views.student import student_read

        student_read(request, student.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'student/student.html')
        self.assertEqual(context['student'], student)
