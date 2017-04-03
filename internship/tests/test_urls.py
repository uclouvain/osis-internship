from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve


def test_paths(routes_to_test):
    for route in routes_to_test:
        path = route["url_path"]
        pattern = route["pattern_name"]
        params = route.get('args')
        kwparams = route.get("kwargs")

        if kwparams:
            yield reverse(pattern, args=params, kwargs=kwparams), path
        else:
            yield reverse(pattern, args=params), path

        yield resolve(path).url_name, pattern


class UrlsTestCase(TestCase):
    def test_cohort_url(self):
        routes_to_test = [
            dict(
                url_path='/internships/',
                pattern_name='internship',
            ),
            dict(
                url_path = "/internships/cohort/1/",
                pattern_name="internships_home",
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohort/1/offers/',
                pattern_name='internships',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/places/1/students/affectation/',
                pattern_name='place_detail_student_affectation',
                args=(1,)
            )
        ]

        for url_name, pattern in test_paths(routes_to_test):
            self.assertEqual(url_name, pattern)