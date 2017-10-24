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
from internship.docs.build import build, generate_pdf, generate_homepage, generate_html, get_path, show_help


class TestDocumentationBuild(unittest.TestCase):

    def test_generate_pdf(self):
        testargs = ["-p", "internship/docs/"]
        with patch.object(sys, 'argv', testargs):
            generate_pdf()
        self.assertTrue(os.path.isfile("internship/docs/user-manual_fr.pdf"))

    def test_generate_html(self):
        testargs = ["-p", "internship/docs/"]
        with patch.object(sys, 'argv', testargs):
            generate_html()
        self.assertTrue(os.path.isfile("internship/docs/user-manual_fr.html"))

    def test_generate_homepage(self):
        testargs = ["-p", "internship/docs/"]
        with patch.object(sys, 'argv', testargs):
            generate_homepage()
        self.assertTrue(os.path.isfile("internship/docs/index.html"))

    def test_get_path(self):
        self.assertEqual(get_path(), "")
        testargs = ["-p", "internship/docs/"]
        with patch.object(sys, 'argv', testargs):
            self.assertEqual(get_path(), "internship/docs/")

    def test_show_help(self):
        self.assertFalse(show_help())
        testargs = ["-h"]
        with patch.object(sys, 'argv', testargs):
            self.assertTrue(show_help())


if __name__ == '__main__':
    unittest.main()
