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
from django.test import TestCase
from django.urls import resolve, reverse


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
                url_path="/internships/cohorts/1/",
                pattern_name="internships_home",
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/offers/',
                pattern_name='internships',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/places/1/students/affectation/',
                pattern_name='place_detail_student_affectation',
                kwargs={'cohort_id': 1, 'organization_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/students/',
                pattern_name='internships_student_resume',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/students/import/',
                pattern_name='internship_students_import',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/students/import/update/',
                pattern_name='internships_student_import_update',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/',
                pattern_name='internship_scores_encoding',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/upload_scores/',
                pattern_name='internship_upload_scores',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/ajax/save_score/',
                pattern_name='save_edited_score',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/ajax/delete_score/',
                pattern_name='delete_edited_score',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/send_summary',
                pattern_name='send_summary',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/ajax/save_evaluation_status/',
                pattern_name='save_evaluation_status',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/ajax/refresh_evolution_score/',
                pattern_name='refresh_evolution_score',
                kwargs={'cohort_id': 1}
            ),
            dict(
                url_path='/internships/cohorts/1/scores_encoding/upload_eval/',
                pattern_name='internship_upload_eval',
                kwargs={'cohort_id': 1}
            ),
        ]

        for url_name, pattern in test_paths(routes_to_test):
            self.assertEqual(url_name, pattern)
