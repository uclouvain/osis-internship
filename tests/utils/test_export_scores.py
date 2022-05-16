##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import timedelta

from django.test import TestCase
from django.utils.datetime_safe import date

from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.student import StudentFactory
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.utils.exporting.score_encoding_xls import _append_row_data, _append_evolution_score

EXCUSED_PERIOD_SCORE = None
EDITED_PERIOD_SCORE = 15
COMPUTED_PERIOD_SCORE = 10
NO_SUBMISSION_SCORE = 0


class XlsExportScoresTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.past_period_no_scores_submitted = PeriodFactory(cohort=cls.cohort, date_end=date.today()-timedelta(days=1))
        cls.past_period_excused = PeriodFactory(cohort=cls.cohort, date_end=date.today()-timedelta(days=1))
        cls.past_period_edited = PeriodFactory(cohort=cls.cohort, date_end=date.today()-timedelta(days=1))
        cls.user = PersonWithPermissionsFactory('is_internship_manager').user
        cls.student = StudentFactory()
        cls.student.organizations = {
            cls.past_period_no_scores_submitted.name: {'reference': OrganizationFactory().reference},
            cls.past_period_excused.name: {'reference': OrganizationFactory().reference},
            cls.past_period_edited.name: {'reference': OrganizationFactory().reference},
        }
        cls.student.periods_scores = {
            cls.past_period_no_scores_submitted.name: NO_SUBMISSION_SCORE,
            cls.past_period_excused.name: {'edited': {'score': EXCUSED_PERIOD_SCORE}, 'computed': NO_SUBMISSION_SCORE},
            cls.past_period_edited.name: {'edited': {'score': EDITED_PERIOD_SCORE}, 'computed': COMPUTED_PERIOD_SCORE},
        }
        cls.periods = [
            cls.past_period_no_scores_submitted,
            cls.past_period_excused,
            cls.past_period_edited,
        ]

    def setUp(self):
        self.client.force_login(self.user)

    def test_append_row_data(self):
        columns = [self.student.person.last_name, self.student.person.first_name, self.student.registration_id]
        for period in self.periods:
            _append_row_data(columns, period, self.student)
        self.assertEqual(len(columns), 9)
        self.assertEqual(columns[4], NO_SUBMISSION_SCORE)
        self.assertEqual(columns[6], '')
        self.assertEqual(columns[8], EDITED_PERIOD_SCORE)

    def test_append_evolution_score_edited(self):
        evolution_score = {'computed': 15, 'edited': {'score': 20, 'reason': ''}}
        columns = [self.student.person.last_name, self.student.person.first_name, self.student.registration_id]
        _append_evolution_score(columns, evolution_score)
        self.assertEqual(len(columns), 6)
        self.assertEqual(columns[3], evolution_score['edited']['score'])
        self.assertEqual(columns[4], evolution_score['computed'])
        self.assertEqual(columns[5], evolution_score['edited']['score'])

    def test_append_evolution_score_computed(self):
        evolution_score = 15
        columns = [self.student.person.last_name, self.student.person.first_name, self.student.registration_id]
        _append_evolution_score(columns, evolution_score)
        self.assertEqual(len(columns), 6)
        self.assertEqual(columns[3], evolution_score)
        self.assertEqual(columns[4], evolution_score)
        self.assertEqual(columns[5], '')
