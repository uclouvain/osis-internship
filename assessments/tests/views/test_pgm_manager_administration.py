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
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory

from base.tests.models import test_exam_enrollment, test_offer_year_calendar, test_offer_enrollment, \
    test_learning_unit_enrollment, test_session_exam
from attribution.tests.models import test_attribution
from assessments.views import score_encoding
from base.models.exam_enrollment import ExamEnrollment

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.student import StudentFactory

class PgmManagerAdministrationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('tmp', 'tmp@gmail.com', 'tmp')

    def test_set_filter_find_manager_faculty(self):
        pass

    def test_set_filter_find_faculty_entities(self):
        pass

    def test_set_filter_find_pgm_manager_by_faculty(self):
        pass

    def test_search_find_programs_by_default_criteria(self):
        pass

    def test_search_find_programs_by_entity(self):
        pass

    def test_search_find_programs_by_pgm_type(self):
        pass

    def test_search_find_programs_by_pgm_manager(self):
        pass

    def test_search_find_programs_by_entity_pgm_type(self):
        pass

    def test_search_find_programs_by_entity_pgm_type_pgm_manager(self):
        pass

    def test_add_pgm_manager_to_one_pgm(self):
        pass

    def test_add_pgm_manager_to_more_than_one_pgm(self):
        pass

    def test_remove_pgm_manager_from_one_pgm(self):
        pass

    def test_remove_pgm_manager_from_more_than_one_pgm(self):
        pass

    def test_find_staff_member(self):
        pass

