import unittest
from internship.utils.list_utils import difference
from django.test import TestCase

class ListUtilsTestCase(TestCase):
    # List utils
    def test_difference_non_empty_lists(self):
        first_list = [1,2,3,4,5]
        second_list = [4,5]
        expected = [1,2,3]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_second_list(self):
        first_list = [1,2,3,4,5]
        second_list = []
        expected = [1,2,3,4,5]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_first_list(self):
        first_list = []
        second_list = [1,2]
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_lists(self):
        first_list = []
        second_list = []
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_list_without_common_elements(self):
        first_list = [1,2,3,4]
        second_list = [5,6]
        expected = [1,2,3,4]
        self.assertEqual(expected, difference(first_list, second_list))

if __name__ == '__main__':
        unittest.main()
