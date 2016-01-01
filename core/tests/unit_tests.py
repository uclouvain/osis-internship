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
