##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import SimpleTestCase
from internship.utils import affect_student


class TestAffectStudent(SimpleTestCase):
    def test_input_file(self):
        actual_offers, actual_choices, actual_priority_choices = affect_student.input_file("./internship/tests/utils/ressources/sample1.txt")
        expected_offers = {(1, 1): [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2],
                           (2, 1): [2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 2],
                           (2, 2): [3, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
                           (3, 3): [4, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
                           (4, 3): [5, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2]}
        expected_choices = {(2, 1, 1): [[2, 2, 1, 1, 1, 0], [2, 1, 1, 1, 2, 0]],
                            (3, 1, 2): [[3, 2, 2, 1, 1, 0]],
                            (3, 2, 3): [[3, 3, 3, 2, 1, 0], [3, 4, 3, 2, 2, 0]]}
        expected_priority_choices = {(1, 1, 1): [[1, 1, 1, 1, 1, 1], [1, 2, 1, 1, 2, 1]],
                                     (1, 2, 3): [[1, 4, 3, 2, 1, 1]],
                                     (4, 1, 1): [[4, 1, 1, 1, 1, 1]],
                                     (4, 2, 3): [[4, 4, 3, 2, 1, 1]]}
        self.assertDictEqual(actual_offers, expected_offers)
        self.assertDictEqual(actual_choices, expected_choices)
        self.assertDictEqual(actual_priority_choices, expected_priority_choices)

