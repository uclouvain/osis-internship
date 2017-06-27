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
import datetime
import json

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.user import UserFactory
from base.tests.factories.person import PersonFactory

from assistant.views.assistant_form import form_part4_edit
from assistant.tests.factories.academic_assistant import AcademicAssistantFactory
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories.settings import SettingsFactory
from assistant.models.enums import assistant_mandate_state


class AssistantFormViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.settings = SettingsFactory()
        self.user = UserFactory()
        self.person = PersonFactory(first_name="James", last_name="Dupont", user=self.user)
        self.academic_assistant = AcademicAssistantFactory(person=self.person)
        self.assistant_mandate = AssistantMandateFactory()
        self.assistant_mandate.assistant = self.academic_assistant
        self.assistant_mandate.state = assistant_mandate_state.TRTS
        self.academic_year = AcademicYearFactory(year=datetime.date.today().year)
        self.learning_unit_year = LearningUnitYearFactory(
            acronym="LBIR1210",
            academic_year=self.academic_year)
        self.learning_unit_year = LearningUnitYearFactory(
            acronym="LBIR1211",
            academic_year=self.academic_year)
        self.client.login(username=self.user.username, password=self.user.password)

    def test_assistant_form_part4_edit_view_basic(self):
        request = self.factory.get(reverse('form_part4_edit', kwargs={'mandate_id': self.assistant_mandate.id}))
        request.user = self.user
        with self.assertTemplateUsed('assistant_form_part4.html'):
            response = form_part4_edit(request, self.assistant_mandate.id)
            self.assertEqual(response.status_code, 200)

    def test_get_learning_units_year(self):
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
