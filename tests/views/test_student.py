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
from datetime import timedelta
from unittest import skipUnless

from django.contrib.auth.models import Permission, User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.datetime_safe import date
from django.utils.translation import gettext_lazy
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from backoffice.settings.base import INSTALLED_APPS
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_address import PersonAddressFactory
from base.tests.factories.student import StudentFactory
from base.tests.models import test_student
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import find_by_cohort, InternshipStudentInformation
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.internship_choice import create_internship_choice
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.score import ScoreFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory
from internship.tests.models import test_organization, test_internship_speciality, test_internship_student_information
from internship.tests.utils.test_student_loader import generate_record
from internship.views import student
from internship.views.student import import_students, internships_student_import_update, internships_student_resume


class TestStudentResume(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        organization = test_organization.create_organization(cohort=cls.cohort)
        cls.student_1 = test_student.create_student(first_name="first", last_name="last", registration_id="64641200")
        cls.student_2 = test_student.create_student(first_name="first", last_name="last", registration_id="606012")
        speciality = test_internship_speciality.create_speciality(cohort=cls.cohort)

        cls.internship = InternshipFactory(cohort=cls.cohort)
        cls.internship_2 = InternshipFactory(cohort=cls.cohort)
        cls.internship_3 = InternshipFactory(cohort=cls.cohort)
        cls.internship_4 = InternshipFactory(cohort=cls.cohort)

        cls.choice_1 = create_internship_choice(organization, cls.student_1, speciality, internship=cls.internship)
        cls.choice_2 = create_internship_choice(organization, cls.student_1, speciality, internship=cls.internship_2)
        cls.choice_3 = create_internship_choice(organization, cls.student_1, speciality, internship=cls.internship_3)
        cls.choice_4 = create_internship_choice(organization, cls.student_1, speciality, internship=cls.internship_4)
        cls.choice_5 = create_internship_choice(organization, cls.student_2, speciality, internship=cls.internship)
        cls.choice_6 = create_internship_choice(organization, cls.student_2, speciality, internship=cls.internship_2)
        cls.choice_7 = create_internship_choice(organization, cls.student_2, speciality, internship=cls.internship_3)
        cls.url = reverse(internships_student_resume, kwargs={
            'cohort_id': cls.cohort.id,
        })

    def setUp(self):
        self.response = self.client.get(self.url)

    def test_get_students_status_empty(self):
        expected = []
        actual, stats = student._get_students_with_status(
            request=self.response.wsgi_request,
            cohort=self.cohort,
            filters=None
        )
        self.assertCountEqual(expected, actual.object_list)

    def test_get_students_status_filled_in(self):
        student_info_1 = test_internship_student_information.create_student_information(
            self.student_1.person,
            "GENERALIST",
            cohort=self.cohort
        )
        student_info_2 = test_internship_student_information.create_student_information(
            self.student_2.person,
            "GENERALIST",
            cohort=self.cohort
        )
        expected = [student_info_1, student_info_2]
        actual, stats = student._get_students_with_status(
            request=self.response.wsgi_request,
            cohort=self.cohort,
            filters=None
        )
        self.assertCountEqual(expected, actual.object_list)
        for item_expected in expected:
            self.assertIn(item_expected, actual.object_list)

    def test_filter_students_by_current_internship(self):
        period = PeriodFactory(cohort=self.cohort, date_start=date.today(), date_end=date.today())
        student_info = InternshipStudentInformationFactory(cohort=self.cohort, person=self.student_1.person)
        affectation = StudentAffectationStatFactory(student=self.student_1, period=period)
        url = reverse(internships_student_resume, kwargs={
            'cohort_id': self.cohort.id,
        })
        response = self.client.get(url)
        actual, stats = student._get_students_with_status(
            request=response.wsgi_request,
            cohort=self.cohort,
            filters=(None, True)
        )
        expected = [student_info]
        self.assertCountEqual(expected, actual)
        for item_expected in expected:
            self.assertIn(item_expected, actual)
        self.assertEqual(
            actual[0].current_internship,
            "{}{}".format(affectation.speciality.acronym, affectation.organization.reference)
        )


class StudentResumeViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.students = [InternshipStudentInformationFactory(cohort=cls.cohort) for _ in range(0, 9)]
        cls.student_with_accent = InternshipStudentInformationFactory(
            cohort=cls.cohort, person=PersonFactory(last_name='Éçàüî')
        )
        cls.students.append(cls.student_with_accent)
        cls.url = reverse(internships_student_resume, kwargs={
            'cohort_id': cls.cohort.id,
        })
        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.user)

    def test_internships_student_resume(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['students'].object_list, self.students)

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_search_student_by_name_unaccent(self):
        query_string = '?name={}'.format("Ecaui")
        response = self.client.get("{}{}".format(self.url, query_string))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['students'].object_list[0], self.student_with_accent)


class StudentsListImport(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('demo', email='demo@demo.org', password='password')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)
        cls.cohort = CohortFactory()

        cls.workbook = Workbook()
        cls.worksheet = cls.workbook.active
        cls.worksheet.append([])
        for _ in range(0, 10):
            student = StudentFactory()
            cls.worksheet.append(generate_record(registration_id=student.registration_id))
        cls.file_content = save_virtual_workbook(cls.workbook)
        cls.worksheet.rows[1][15].value = "Edited_Location"
        cls.edited_file_content = save_virtual_workbook(cls.workbook)

        cls.import_url = reverse(import_students, kwargs={
            'cohort_id': cls.cohort.id,
        })
        cls.apply_update_url = reverse(internships_student_import_update, kwargs={
            'cohort_id': cls.cohort.id,
        })

    def setUp(self):
        self.client.force_login(self.user)

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
        self.assertEqual(len(find_by_cohort(self.cohort.id)), 10)
        self.assertRedirects(
            apply_response, reverse('internships_student_resume', kwargs={"cohort_id": self.cohort.id})
        )

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
        self.assertNotEqual(student.location, "Edited_Location")

        apply_update_response = self.client.post(self.apply_update_url, {
            'data': approve_update_response.context['data_json']
        })
        student.refresh_from_db()
        self.assertRedirects(apply_update_response, reverse('internships_student_resume', kwargs={
            "cohort_id": self.cohort.id
        }))
        self.assertEqual(student.location, "Edited_Location")

    def test_invalid_import(self):
        invalid_file = SimpleUploadedFile('invalid_file.txt', self.file_content)
        response = self.client.post(self.import_url, {
            'file_upload': invalid_file
        })
        self.assertEqual(len(find_by_cohort(self.cohort.id)), 0)
        self.assertRedirects(response, reverse('internships_student_resume', kwargs={"cohort_id": self.cohort.id}))


class StudentsAffectationModification(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('demo', email='demo@demo.org', password='password')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

        cls.cohort = CohortFactory()

        cls.student = StudentFactory()
        PersonAddressFactory(person=cls.student.person)
        InternshipStudentInformationFactory(person=cls.student.person, cohort=cls.cohort)

        cls.periods = [
            PeriodFactory(name='P{}'.format(p), date_end=date.today() + timedelta(days=p*30), cohort=cls.cohort)
            for p in range(1, 8)
        ]

        cls.affectations = [StudentAffectationStatFactory(
            student=cls.student,
            period=period,
            organization__cohort=cls.cohort,
            speciality__cohort=cls.cohort,
            internship__cohort=cls.cohort,
            cost=1,
        ) for period in cls.periods[:-1]]

        cls.offers = [OfferFactory(
            organization=a.organization, speciality=a.speciality, cohort=cls.cohort
        ) for a in cls.affectations]

        cls.scores = [ScoreFactory(student_affectation=a) for a in cls.affectations]
        cls.choices = InternshipChoice(student=cls.student)

    def setUp(self):
        self.client.force_login(self.user)

    def test_should_show_student_affectations_form(self):
        url = reverse('internship_student_affectation_modification', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        })
        context = self.client.get(url).context

        self.assertListEqual(
            list(context['organizations']),
            sorted([a.organization for a in self.affectations], key=lambda o: o.reference)
        )
        self.assertListEqual(
            list(context['periods']),
            sorted([a.period for a in self.affectations], key=lambda p: p.date_end)
        )
        self.assertEqual(list(context['affectations']), self.affectations)
        self.assertEqual(list(context['internships'].values()), [a.internship_id for a in self.affectations])

    def test_should_not_update_student_affectations_if_validated_score_exists_in_affectations(self):
        self.scores[0].validated = True
        self.scores[0].save()

        url = reverse('student_save_affectation_modification', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        })
        response = self.client.post(url, data={
            'period': self.periods[0],
            'internship': [a.internship.id for a in self.affectations],
            'specialty': [a.speciality.name for a in self.affectations],
            'organization': [a.organization.reference for a in self.affectations]
        })
        error_msg = [m.message for m in get_messages(response.wsgi_request)][0]
        self.assertEqual(error_msg, gettext_lazy(
            'Cannot edit affectations because at least one affectation has a linked validated score'
        ))
        self.assertRedirects(response, reverse('internship_student_affectation_modification', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        }))

    def test_should_update_student_affectations(self):
        organizations = [a.organization for a in self.affectations]
        initial_cost = self.affectations[0].cost
        new_organization = OrganizationFactory(cohort=self.cohort)
        organizations[0] = new_organization
        OfferFactory(organization=new_organization, speciality=self.affectations[0].speciality, cohort=self.cohort)

        url = reverse('student_save_affectation_modification', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        })

        response = self.client.post(url, data={
            'organization': [o.reference for o in organizations],
            'period': self.periods[0],
            'specialty': [a.speciality.name for a in self.affectations],
            'internship': [a.internship.pk for a in self.affectations]
        })

        self.assertRedirects(response, reverse('internships_student_read', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        })+"?tab=affectations")

        updated_affectation = self.affectations[0]
        updated_affectation.refresh_from_db()

        self.assertTrue(updated_affectation)
        self.assertGreater(updated_affectation.cost, initial_cost)

    def test_should_delete_student_affectations_when_at_least_one_post_data_is_set_to_empty(self):
        organizations = [a.organization.reference for a in self.affectations]
        organizations[0] = ''  # empty first organization post data

        url = reverse('student_save_affectation_modification', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        })

        response = self.client.post(url, data={
            'organization': organizations,
            'period': self.periods[0],
            'specialty': [a.speciality.name for a in self.affectations],
            'internship': [a.internship.pk for a in self.affectations]
        })

        self.assertRedirects(response, reverse('internships_student_read', kwargs={
            'cohort_id': self.cohort.pk, 'student_id': self.student.pk
        })+"?tab=affectations")

        self.assertFalse(InternshipStudentAffectationStat.objects.filter(
            student=self.student, period=self.periods[0]
        ).exists())
