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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase, RequestFactory
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from base.tests.factories.student import StudentFactory
from base.tests.models import test_student
from internship.models.internship_student_information import find_by_cohort, find_by_person, \
    InternshipStudentInformation, find_all
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.models import test_organization, test_internship_speciality, test_internship_student_information
from internship.tests.utils.test_student_loader import generate_record
from internship.views import student
from internship.views.student import import_students, internships_student_import_update, internships_student_resume


class TestStudentResume(TestCase):
    def setUp(self):
        self.cohort = CohortFactory()
        organization = test_organization.create_organization(cohort=self.cohort)
        self.student_1 = test_student.create_student(first_name="first", last_name="last", registration_id="64641200")
        self.student_2 = test_student.create_student(first_name="first", last_name="last", registration_id="606012")
        speciality = test_internship_speciality.create_speciality(cohort=self.cohort)

        self.internship = InternshipFactory(cohort=self.cohort)
        self.internship_2 = InternshipFactory(cohort=self.cohort)
        self.internship_3 = InternshipFactory(cohort=self.cohort)
        self.internship_4 = InternshipFactory(cohort=self.cohort)

        self.choice_1 = create_internship_choice(organization, self.student_1, speciality, internship=self.internship)
        self.choice_2 = create_internship_choice(organization, self.student_1, speciality, internship=self.internship_2)
        self.choice_3 = create_internship_choice(organization, self.student_1, speciality, internship=self.internship_3)
        self.choice_4 = create_internship_choice(organization, self.student_1, speciality, internship=self.internship_4)
        self.choice_5 = create_internship_choice(organization, self.student_2, speciality, internship=self.internship)
        self.choice_6 = create_internship_choice(organization, self.student_2, speciality, internship=self.internship_2)
        self.choice_7 = create_internship_choice(organization, self.student_2, speciality, internship=self.internship_3)

    def test_get_students_status_empty(self):
        url = reverse(internships_student_resume, kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        expected = []
        actual = student._get_students_with_status(
            request=response.wsgi_request,
            page=None,
            cohort=self.cohort,
            filter_name=None
        )
        self.assertCountEqual(expected, actual)

    def test_get_students_status_filled_in(self):
        url = reverse(internships_student_resume, kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        test_internship_student_information.create_student_information(self.student_1.person, "GENERALIST",
                                                                       cohort=self.cohort)
        test_internship_student_information.create_student_information(self.student_2.person, "GENERALIST",
                                                                       cohort=self.cohort)
        expected = [(self.student_1, True), (self.student_2, False)]
        actual = student._get_students_with_status(
            request=response.wsgi_request,
            page=None,
            cohort=self.cohort,
            filter_name=None
        )
        self.assertCountEqual(expected, actual)
        for item_expected in expected:
            self.assertIn(item_expected, actual)


class StudentResumeViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()

    def test_internships_student_resume(self):
        url = reverse(internships_student_resume, kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StudentsListImport(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', email='demo@demo.org', password='password')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.cohort = CohortFactory()

        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.append([])
        for i in range(0,10):
            student = StudentFactory()
            self.worksheet.append(generate_record(registration_id=student.registration_id))
        self.file_content = save_virtual_workbook(self.workbook)
        self.worksheet.rows[1][15].value = "Edited_Location"
        self.edited_file_content = save_virtual_workbook(self.workbook)

        self.import_url = reverse(import_students, kwargs={
            'cohort_id': self.cohort.id,
        })
        self.apply_update_url = reverse(internships_student_import_update, kwargs={
            'cohort_id': self.cohort.id,
        })

    def test_valid_import_with_original_list_empty(self):
        uploaded_file = SimpleUploadedFile('student_list.xlsx', self.file_content)
        response = self.client.post(self.import_url, {
            'file_upload': uploaded_file
        })
        apply_response = self.client.post(self.apply_update_url, {
            'data': response.context['data_json']
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students_update.html")
        self.assertEqual(len(find_by_cohort(self.cohort.id)),10)
        self.assertRedirects(apply_response, reverse('internships_student_resume', kwargs={"cohort_id": self.cohort.id}))

    def test_valid_import_with_edited_row(self):
        uploaded_file = SimpleUploadedFile('student_list.xlsx', self.file_content)
        response = self.client.post(self.import_url, {
            'file_upload': uploaded_file
        })
        self.client.post(self.apply_update_url, {
            'data': response.context['data_json']
        })
        edited_file = SimpleUploadedFile('student_list.xlsx', self.edited_file_content)
        approve_update_response = self.client.post(self.import_url, {
            'file_upload': edited_file
        })
        data = approve_update_response.context['differences'][0]['data']
        student = InternshipStudentInformation.objects.get(pk=data.pk)
        self.assertEqual(approve_update_response.status_code, 200)
        self.assertTemplateUsed(approve_update_response, "students_update.html")
        self.assertNotEqual(student.location,"Edited_Location")

        apply_update_response = self.client.post(self.apply_update_url, {
            'data': approve_update_response.context['data_json']
        })
        student.refresh_from_db()
        self.assertRedirects(apply_update_response, reverse('internships_student_resume', kwargs={
            "cohort_id": self.cohort.id
        }))
        self.assertEqual(student.location,"Edited_Location")

    def test_invalid_import(self):
        invalid_file = SimpleUploadedFile('invalid_file.txt', self.file_content)
        response = self.client.post(self.import_url, {
            'file_upload': invalid_file
        })
        self.assertEqual(len(find_by_cohort(self.cohort.id)),0)
        self.assertRedirects(response, reverse('internships_student_resume', kwargs={"cohort_id": self.cohort.id}))
