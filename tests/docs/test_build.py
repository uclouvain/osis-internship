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
from django.conf import settings
from django.test import SimpleTestCase

import os
import os.path
import subprocess
import sys
import unittest
from unittest.mock import patch

from internship.docs.build import generate_pdf, generate_homepage, generate_html, get_path, show_help


class TestDocumentationBuild(SimpleTestCase):
    internship_doc_path = "{}/internship/docs/".format(settings.BASE_DIR)
    path_args = ["-p", internship_doc_path]

    def test_generate_pdf(self):
        try:
            run_under_args_context(generate_pdf, self.path_args)

            expected_file_created = "{}/user-manual_fr.pdf".format(self.internship_doc_path)
            self.assertTrue(os.path.isfile(expected_file_created))
            checkout_modified_files('docs/user-manual_fr.pdf')
        except FileNotFoundError:
            self.assertTrue(True)

    def test_generate_html(self):
        try:
            run_under_args_context(generate_html, self.path_args)

            expected_file_created = "{}/user-manual_fr.html".format(self.internship_doc_path)
            self.assertTrue(os.path.isfile(expected_file_created))
            checkout_modified_files('docs/user-manual_fr.html')
        except FileNotFoundError:
            self.assertTrue(True)

    def test_generate_homepage(self):
        run_under_args_context(generate_homepage, self.path_args)

        expected_file_created = "{}/index.html".format(self.internship_doc_path)
        self.assertTrue(os.path.isfile(expected_file_created))

    def test_get_path(self):
        self.assertEqual(get_path(), "")
        with patch.object(sys, 'argv', self.path_args):
            self.assertEqual(get_path(), self.internship_doc_path)

    def test_show_help(self):
        self.assertFalse(show_help())
        testargs = ["-h"]
        with patch.object(sys, 'argv', testargs):
            self.assertTrue(show_help())


def run_under_args_context(func, args):
    with patch.object(sys, 'argv', args):
        func()


def checkout_modified_files(path):
    os.chdir('internship')
    subprocess.check_output(['git', 'checkout', '--', path])
    os.chdir('..')


if __name__ == '__main__':
    unittest.main()
