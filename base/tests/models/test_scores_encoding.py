##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase
from base.models.scores_encoding import ScoresEncoding

start_date = datetime.datetime.now()
end_date = start_date.replace(year=start_date.year + 1)


class NumberOfScoresNotYetSubmittedTest(TestCase):

    def test_case_submitted_scores_equals_drafts(self):
        scores_encoding = ScoresEncoding(exam_enrollments_encoded=10,
                                         exam_enrollments_encoded_draft=10)
        self.assertEquals(scores_encoding.number_of_scores_not_yet_submitted(), 0)

    def test_case_submitted_scores_gt_drafts(self):
        scores_encoding = ScoresEncoding(exam_enrollments_encoded=10,
                                         exam_enrollments_encoded_draft=0)
        self.assertEquals(scores_encoding.number_of_scores_not_yet_submitted(), 0)

    def test_case_submitted_scores_lt_drafts(self):
        scores_encoding = ScoresEncoding(exam_enrollments_encoded=7,
                                         exam_enrollments_encoded_draft=10)
        self.assertEquals(scores_encoding.number_of_scores_not_yet_submitted(), 3)
