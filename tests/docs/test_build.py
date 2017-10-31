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
import sys
import unittest
import os.path
from mock import patch
from internship.docs.build import generate_pdf, generate_homepage, generate_html, get_path, show_help


class TestDocumentationBuild(unittest.TestCase):

    path_args = ["-p", "internship/docs/"]

    def test_generate_pdf(self):
        try:
            run_under_args_context(generate_pdf, self.path_args)
            self.assertTrue(os.path.isfile("internship/docs/user-manual_fr.pdf"))
        except FileNotFoundError:
            self.assertTrue(True)

    def test_generate_html(self):
        try:
            run_under_args_context(generate_html, self.path_args)
            self.assertTrue(os.path.isfile("internship/docs/user-manual_fr.html"))
        except FileNotFoundError:
            self.assertTrue(True)

    def test_generate_homepage(self):
        run_under_args_context(generate_homepage, self.path_args)
        self.assertTrue(os.path.isfile("internship/docs/index.html"))

    def test_get_path(self):
        self.assertEqual(get_path(), "")
        with patch.object(sys, 'argv', self.path_args):
            self.assertEqual(get_path(), "internship/docs/")

    def test_show_help(self):
        self.assertFalse(show_help())
        testargs = ["-h"]
        with patch.object(sys, 'argv', testargs):
            self.assertTrue(show_help())


def run_under_args_context(func, args):
    with patch.object(sys, 'argv', args):
        func()


if __name__ == '__main__':
    unittest.main()
