import csv
from io import StringIO
from unittest import skip
from unittest.mock import MagicMock, Mock, patch

import contextlib
import django.db
import factory
import factory.fuzzy
from django.test import SimpleTestCase, TestCase

from internship.utils import student_loader


class CsvRowFactory:
    global_id = factory.Faker('ean8')

    location = factory.Faker('lexify', text='??????')
    postal_code = factory.Faker('zipcode')
    city = factory.Faker('city')
    country = factory.Faker('country')
    phone_mobile = factory.Faker('phone_number')
    email = factory.Faker('email')


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


def create_csv_stream(filename):
    def generate_record(idx):
        row = CsvRowFactory()
        return (
            idx,
            row.global_id.generate({}),
            row.location.generate({}),
            row.postal_code.generate({}),
            row.city.generate({}),
            row.country.generate({}),
            row.phone_mobile.generate({}),
            row.email.generate({}),
        )

    str_io = StringIO()
    writer = csv.writer(str_io)
    headers = student_loader.CSVRow._fields
    writer.writerow(headers)

    records = [
        generate_record(idx)
        for idx in range(0, 2)
    ]

    writer.writerows(records)
    str_io.seek(0)
    str_io.name = filename
    return str_io


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

            with self.assertRaises(csv.Error):
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
                    row.global_id.generate({}),
                    row.location.generate({}),
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
