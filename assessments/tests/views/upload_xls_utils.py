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

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.tests.factories.user import UserFactory
from base.tests.factories.academic_year import AcademicYearFakerFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory


LEARNING_UNIT_ACRONYM = "LOSIS1211"


class TestUploadXls(TestCase):
    def setUp(self):
        user = UserFactory()
        self.client = Client()
        self.client.force_login(user=user)
        self.url = reverse('upload_encoding', kwargs={'learning_unit_year_id': 1})

    def test_with_no_file_uploaded(self):
        # with open("assessments/tests/resources/empty_scores.xlsx", 'rb') as score_sheet:
        response = self.client.post(self.url, {'file': ''}, follow=True)
        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('no_file_submitted'))

    def test_with_no_scores_encoded(self):
        an_academic_year = AcademicYearFakerFactory(year=2017,
                                                    start_date=datetime.date(year=2017, month=9, day=1),
                                                    end_date=datetime.date(year=2018, month=10, day=1))
        a_learning_unit_year = LearningUnitYearFakerFactory(academic_year=an_academic_year,
                                                            acronym=LEARNING_UNIT_ACRONYM)
        with open("assessments/tests/resources/empty_scores.xlsx", 'rb') as score_sheet:
            response = self.client.post(self.url, {'file': score_sheet}, follow=True)
            messages = list(response.context['messages'])

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].tags, 'error')
            self.assertEqual(messages[0].message, _('no_score_injected'))
