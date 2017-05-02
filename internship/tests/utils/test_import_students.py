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
from unittest import mock
from unittest.mock import patch

import faker
import pendulum
from django.test import TestCase

fake = faker.Faker()


class ImportStudentsXLSTestCase(TestCase):
    @patch('base.models.person.Person')
    @patch('internship.models.internship_student_information.InternshipStudentInformation')
    def test_import_students_with_person(self, mock_isi, mock_person):
        from internship.utils.import_students import import_csv_row
        from internship.tests.utils.test_student_loader import _generate_record

        mock_person.objects = mock.Mock()

        person = mock.Mock()
        cohort = mock.Mock()

        conf = {
            'filter.return_value.first.return_value': person
        }
        mock_person.objects.configure_mock(**conf)

        mock_isi.objects = mock.Mock()

        row = _generate_record()

        import_csv_row(cohort, row)

        self.assertTrue(mock_isi.objects.create.called)

        mock_isi.objects.create.assert_called_with(
            person=person, country=row[10], postal_code=row[8], email=row[12],
            phone_mobile=row[11], city=row[9], cohort=cohort
        )

    @patch('base.models.person.Person')
    @patch('internship.models.internship_student_information.InternshipStudentInformation')
    def test_no_person_name_with_comma(self, mock_isi, mock_person):
        from internship.utils.import_students import import_csv_row
        from internship.tests.utils.test_student_loader import _generate_record

        mock_person.objects = mock.Mock()

        cohort = mock.Mock()
        person = mock.Mock()

        conf = {
            'create.return_value': person,
            'filter.return_value.first.return_value': None
        }
        mock_person.objects.configure_mock(**conf)

        mock_isi.objects = mock.Mock()

        row = list(_generate_record())
        first_name = fake.first_name()
        last_name = fake.last_name()
        row[0] = '{}, {}'.format(last_name, first_name)

        import_csv_row(cohort, row)

        mock_person.objects.create.assert_called_with(
            global_id=row[6], gender=row[1],
            first_name=first_name, last_name=last_name,
            birth_date=pendulum.parse(row[2]).strftime('%Y-%m-%d')
        )

        mock_isi.objects.create.assert_called_with(
            person=person, country=row[10], postal_code=row[8], email=row[12],
            phone_mobile=row[11], city=row[9], cohort=cohort
        )

    @patch('base.models.person.Person')
    @patch('internship.models.internship_student_information.InternshipStudentInformation')
    def test_no_person_name_without_comma(self, mock_isi, mock_person):
        from internship.utils.import_students import import_csv_row
        from internship.tests.utils.test_student_loader import _generate_record

        mock_person.objects = mock.Mock()

        cohort = mock.Mock()
        person = mock.Mock()

        conf = {
            'create.return_value': person,
            'filter.return_value.first.return_value': None
        }
        mock_person.objects.configure_mock(**conf)

        mock_isi.objects = mock.Mock()

        row = list(_generate_record())
        first_name = fake.first_name()
        last_name = fake.last_name()
        row[0] = '{} {}'.format(last_name, first_name)

        import_csv_row(cohort, row)

        mock_person.objects.create.assert_called_with(
            global_id=row[6], gender=row[1],
            first_name=first_name, last_name=last_name,
            birth_date=pendulum.parse(row[2]).strftime('%Y-%m-%d')
        )

        mock_isi.objects.create.assert_called_with(
            person=person, country=row[10], postal_code=row[8], email=row[12],
            phone_mobile=row[11], city=row[9], cohort=cohort
        )

    @patch('internship.utils.import_students.import_csv_row')
    def test_import_csv(self, mock_import_csv_row):
        from internship.tests.utils.test_student_loader import create_csv_stream
        from internship.utils.import_students import import_csv

        with create_csv_stream('demo.csv', number=5) as str_io:
            cohort = mock.Mock()
            import_csv(cohort, str_io)
            self.assertTrue(mock_import_csv_row.called)
            self.assertEqual(mock_import_csv_row.call_count, 5)