import unittest

from django.test import TestCase

from internship.utils.import_students import import_csv


@unittest.skip("Implemented but support the .csv file from the hard disk: BAD")
class ImportStudentsXLSTestCase(TestCase):
    def test_import_file(self):
        with open('/tmp/LISTE R6 2017 2018.csv') as csvfile:
            import_csv(csvfile)

