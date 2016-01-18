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
"""
Unit tests cases
"""
from core.tests import util

__author__ = 'glamarca'

from django.test import TestCase


class CoreAuthTestCase(TestCase):
    """
    Test case for the authentication (login) and authorisations process.
    This has to be independent of the authentication mecanism (basic, remote,...).
    The goal is to test the granted access to specific methods of the views files
    """


@classmethod
def setUpClass(cls):
    """
    Initialise the test environment :
    - Create valid user with required permission to access methods, without admin rights
    - Create valid user with required permission to access methods, with admin rights
    - Create valid user without required permission to access methods
    """
    util.init_all_test_users()
    super(CoreAuthTestCase, cls).setUpClass()


def test_home(self):
    """
    Test the home page.
    """
    return

class UploadScoreTestCase(TestCase):
    """

    """

@classmethod
def setUpClass(cls):
    """
    Initialise the test environment :
    - Create valid user with required permission to access methods, without admin rights
    - Create valid user with required permission to access methods, with admin rights
    - Create valid user without required permission to access methods
    """
    util.init_all_test_users()
    super(CoreAuthTestCase, cls).setUpClass()
