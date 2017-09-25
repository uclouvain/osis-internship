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
import json
import datetime
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory

from assistant.views.assistant_form import form_part4_edit
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories.settings import SettingsFactory


class AssistantFormViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.settings = SettingsFactory()
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)
        self.assistant_mandate = AssistantMandateFactory(academic_year=self.current_academic_year)
        LearningUnitYearFactory(academic_year=self.current_academic_year, acronym="LBIR1210")
        LearningUnitYearFactory(academic_year=self.current_academic_year, acronym="LBIR1211")


    def test_assistant_form_part4_edit_view_basic(self):
        self.client.force_login(self.assistant_mandate.assistant.person.user)
        request = self.factory.get(reverse('form_part4_edit'))
        request.user = self.assistant_mandate.assistant.person.user
        with self.assertTemplateUsed('assistant_form_part4.html'):
            response = form_part4_edit(request)
            self.assertEqual(response.status_code, 200)

    def test_get_learning_units_year(self):
        self.client.force_login(self.assistant_mandate.assistant.person.user)
        response = self.client.generic(method='get',
                                       path='/assistants/assistant/form/part2/get_learning_units_year/?term=LBIR1211',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data[0]['value'], 'LBIR1211')
        self.assertEqual(len(data), 1)
        response = self.client.generic(method='get',
                                       path='/assistants/assistant/form/part2/get_learning_units_year/?term=LBIR12',
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)
