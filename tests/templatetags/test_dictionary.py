##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.test import TestCase

from internship.templatetags.dictionary import get_item, has_substr, to_json


class TestDictionary(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dict = {'key': 'value'}

    def test_get_item_with_given_key_should_return_value(self):
        self.assertEqual(get_item(self.dict, 'key'), self.dict['key'])

    def test_has_substr_should_assert_str_is_in_dict(self):
        self.assertEqual(has_substr(self.dict, 'key'), 'key' in str(self.dict))

    def test_to_json_converts_dict_to_json(self):
        self.assertEqual(to_json(self.dict), '{"key": "value"}')

