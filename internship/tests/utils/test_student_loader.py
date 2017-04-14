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
import csv
import io
from io import StringIO
import unittest
from unittest.mock import Mock, patch

import django.db
import factory
import factory.fuzzy
import faker
from django.test import SimpleTestCase, TestCase

from internship.utils import student_loader


class CsvRowFactory:
    name = factory.Faker('name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    gender = 'F'

    birthdate = '2011-01-21'
    birthplace = factory.Faker('city')

    nationality = 'Belge'

    noma = factory.Faker('numerify', text='##########')
    fgs = factory.Faker('numerify', text='######')

    street = factory.Faker('lexify', text='??????')
    postal_code = factory.Faker('zipcode')
    city = factory.Faker('city')
    country = factory.Faker('country')
    phone_mobile = factory.Faker('phone_number')
    email = factory.Faker('email')


@unittest.skip("to rest")
class CsvRowFactoryTestCase(SimpleTestCase):
    def _is_faker(self, attribute):
        return isinstance(getattr(CsvRowFactory, attribute),
                          factory.faker.Faker)

    def test_headers(self):
        headers = set(field
                      for field in student_loader.CSVRow._fields
                      if not field.startswith('ignored'))

        fields = set(attribute
                     for attribute in dir(CsvRowFactory)
                     if self._is_faker(attribute))

        self.assertSetEqual(headers, fields)


def _generate_record():
    row = CsvRowFactory()
    return (
        '{}, {}'.format(row.last_name.generate({}), row.first_name.generate({})),
        # row.name.generate({}),
        row.gender,
        row.birthdate,
        row.birthplace.generate({}),
        row.nationality,
        row.noma.generate({}),
        row.fgs.generate({}),
        row.street.generate({}),
        row.postal_code.generate({}),
        row.city.generate({}),
        row.country.generate({}),
        row.phone_mobile.generate({}),
        row.email.generate({}),
    )


def create_csv_stream(filename, number=2, headers=True):
    str_io = StringIO()
    writer = csv.writer(str_io)
    if headers:
        headers = student_loader.CSVRow._fields
        writer.writerow(headers)

    records = [
        _generate_record()
        for idx in range(0, number)
    ]

    writer.writerows(records)
    str_io.seek(0)
    str_io.name = filename
    return str_io


#@unittest.skip("Skip")
class StudentLoaderTestCase(TestCase):
    @patch('base.models.person.find_by_global_id')
    def test_insert_internship_student_information_not_found(self,
                                                             mock_person_find_by_global_id):
        mock_person_find_by_global_id.return_value = False

        idx, row = 0, CsvRowFactory()
        result = student_loader._insert_internship_student_information(idx, row)

        self.assertEqual((idx, False, True, False, False), result)

    @patch('base.models.person.find_by_global_id')
    @patch('internship.models.internship_student_information.InternshipStudentInformation')
    def test_insert_internship_student_information_imported(self,
                                                            mock_isi,
                                                            mock_person_find_by_global_id):
        mock_person_find_by_global_id.return_value = Mock()
        mock_isi.return_value = Mock()

        idx, row = 0, CsvRowFactory()
        result = student_loader._insert_internship_student_information(idx, row)

        self.assertEqual((idx, True, False, False, False), result)

    @patch('base.models.person.find_by_global_id')
    @patch('internship.models.internship_student_information.InternshipStudentInformation')
    def test_insert_internship_student_information_duplicated(self,
                                                            mock_isi,
                                                            mock_person_find_by_global_id):
        mock_person_find_by_global_id.return_value = Mock()
        mock_isi.return_value = Mock()
        mock_isi.return_value.save = Mock(side_effect=django.db.IntegrityError)

        idx, row = 0, CsvRowFactory()
        result = student_loader._insert_internship_student_information(idx, row)

        self.assertEqual((idx, False, False, True, False), result)

    @patch('base.models.person.find_by_global_id')
    @patch('internship.models.internship_student_information.InternshipStudentInformation')
    def test_insert_internship_student_information_error(self,
                                                         mock_isi,
                                                         mock_person_find_by_global_id):
        mock_person_find_by_global_id.return_value = Mock()
        mock_isi.return_value = Mock()
        mock_isi.return_value.save = Mock(side_effect=django.db.DataError)

        idx, row = 0, CsvRowFactory()
        result = student_loader._insert_internship_student_information(idx, row)
        self.assertEqual((idx, False, False, False, True), result)

    def test_load_empty_csv_without_header(self):
        with StringIO() as strIo:
            csv.writer(strIo)
            strIo.seek(0)

            with self.assertRaises(student_loader.BadCSVFormat):
                # Delimiter not detected
                student_loader.load_internship_students(strIo)

    @patch('base.models.person.find_by_global_id')
    def test_load_empty_csv_with_header(self, mock_person_find_by_global_id):
        with StringIO() as strIo:
            writer = csv.writer(strIo)
            headers = student_loader.CSVRow._fields
            writer.writerow(headers)

            strIo.seek(0)

            student_loader.load_internship_students(strIo)

            self.assertFalse(mock_person_find_by_global_id.called)

    def test_load_csv_with_header(self):
        with StringIO() as strIo:
            writer = csv.writer(strIo)
            headers = student_loader.CSVRow._fields
            writer.writerow(headers)

            def generate_record(idx):
                row = CsvRowFactory()
                return (
                    idx,
                    row.noma.generate({}),
                    row.street.generate({}),
                    row.postal_code.generate({}),
                    row.city.generate({}),
                    row.country.generate({}),
                    row.phone_mobile.generate({}),
                    row.email.generate({}),
                )

            records = [
                generate_record(idx)
                for idx in range(0, 2)
            ]

            writer.writerows(records)
            strIo.seek(0)

            with patch('base.models.person.find_by_global_id') as mock_person_find_by_global_id, \
                 create_csv_stream('demo.csv') as strIo:
                mock_person_find_by_global_id.return_value = False
                student_loader.load_internship_students(strIo)
                self.assertEqual(mock_person_find_by_global_id.call_count, len(records))

    @unittest.skip("We will receive a .csv file")
    def test_load_text_file(self):
        fake = faker.Faker()

        def row_compute():
            return ' '.join([
                fake.time(pattern='%Y-%m-%d %H:%M:%S'),
                '[{}]'.format(fake.numerify(text='########')),
                fake.random_element(elements=('ERROR', 'WARNING', 'INFO', 'DEBUG')),
                fake.sentence(nb_words=10, variable_nb_words=True)
            ])

        text = '\n'.join(row_compute()
                         for idx in range(fake.random_int(min=10, max=50)))

        with self.assertRaises(student_loader.BadCSVFormat), io.StringIO(text) as str_io:
            student_loader.load_internship_students(str_io)
