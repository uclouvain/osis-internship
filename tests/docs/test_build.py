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
import unittest
import os.path
from internship.docs import build


class TestDocumentationBuild(unittest.TestCase):

    def test_generate_pdf(self):
        build.generate_pdf()
        self.assertTrue(os.path.isfile("internship/docs/user_manual_fr.pdf"))

    def test_generate_html(self):
        self.assertFalse(True)

    def test_generate_homepage(self):
        self.assertFalse(True)

    def test_initialize_content(self):
        self.assertFalse(True)


if __name__ == '__main__':
    unittest.main()
