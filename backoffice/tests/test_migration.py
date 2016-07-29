##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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

# This class tests the portal_migration functions.


from django.test import TestCase
from base.models import student, tutor, person
from reference.models import country, domain, education_institution, language
import backoffice.portal_migration as portal_migration
from django.core.exceptions import ObjectDoesNotExist
import backoffice.tests.data_for_tests as data_for_tests


class PortalMigrationTest(TestCase):
    def setUp(self):
        self.list_students = data_for_tests.create_students()
        self.list_tutors = data_for_tests.create_tutors()

    def testGetModelClass(self):
        list_expected = ['reference.Country',
                         'reference.Domain',
                         'reference.EducationInstitution'
                         'reference.Language',
                         'base.Student',
                         'base.Tutor']
        list_actual = [portal_migration.get_model_class_str(country.Country),
                       portal_migration.get_model_class_str(domain.Domain),
                       portal_migration.get_model_class_str(education_institution.EducationInstitution),
                       portal_migration.get_model_class_str(language.Language),
                       portal_migration.get_model_class_str(student.Student),
                       portal_migration.get_model_class_str(tutor.Tutor)]
        self.assertListEqual(list_expected, list_actual, "get_model_class_str doesn't "
                                                         "return the correct string for"
                                                         "the class.")

    def testGetAllDataStudent(self):
        list_expected = self.list_students

        # Need to transform results query into model object
        list_query = portal_migration.get_all_data(student.Student)
        list_actual = []
        for item in list_query:
            try:
                list_actual.append(student.Student.objects.get(id=item['id']))
            except ObjectDoesNotExist:
                print("Error when retrieving data " + str(item))

        self.assertListEqual(list_expected, list_actual, "Get all data doesn't return all data "
                                                         "for the student model.")

    def testGetAllDataTutors(self):
        list_expected = self.list_tutors

        # Need to transform results query into model object
        list_query = portal_migration.get_all_data(tutor.Tutor)
        list_actual = []
        for item in list_query:
            try:
                list_actual.append(tutor.Tutor.objects.get(id=item['id']))
            except ObjectDoesNotExist:
                print("Error when retrieving data " + str(item))

        self.assertListEqual(list_expected, list_actual, "Get all data doesn't return all data "
                                                         "for the tutor model.")
