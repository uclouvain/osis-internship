import unittest

from django.test import TestCase

from internship.tests.factories.cohort import CohortFactory
from internship.utils.import_students import import_csv


@unittest.skip("Implemented but support the .csv file from the hard disk: BAD")
class ImportStudentsXLSTestCase(TestCase):
    def test_import_file(self):
        cohort = CohortFactory()

        with open('/tmp/LISTE R6 2017 2018.csv') as csvfile:
            import_csv(cohort, csvfile)

